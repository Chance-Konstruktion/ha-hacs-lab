"""Installationsnaht: Release-Anhang oder Tag-Archiv an den Zielort tauschen.

Stufe M4b rundet die Naht ab, die M5 fuer den ``install``-Dienst
gezogen hat. Drei Dinge kommen dazu:

* **Quelle:** der Anhang des Releases, wenn der Besitzer dem Tag ein
  ZIP beigelegt hat (gebaut, nicht gepackt-vom-Quellstand), sonst das
  Archiv des Tags. Die Auswahl ist streng: genau EIN Zip-Anhang wird
  genommen, null oder mehrere bedeuten Rueckfall aufs Tag-Archiv --
  Raterei beim Installieren hilft niemandem.
* **Protokoll:** die Installation vermerkt den Zielweg in der Ablage
  (``stand.pfad``). Ohne Weg keine ehrliche Deinstallation -- und mit
  ihm ist die Rueckwaerts-Frage eine Ja/Nein-Pruefung, kein Globbing.
* **Deinstallation:** was der Tausch hingelegt hat, geht in einem Zug
  weg -- erst wegbenennen, dann entfernen. Ein Abbruch dazwischen
  hinterlaesst kein halbes Verzeichnis im Ziel.

Metadaten (manifest.json, hacs.json) werden hier nur GELESEN, nie
entpackt -- das Schreiben bleibt allein beim geprueften Weg des Kerns.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from .core import entpacken, zielpfade
from .core.forge import Release
from .core.validierung import pruefe_manifest

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .core.forge import Forge
    from .eintraege import Eintrag

#: Zwischenlager unter der Konfiguration -- dasselbe Dateisystem wie das
#: Ziel, das verlangt der atomare Tausch aus M4a.
ZWISCHENLAGER_NAME = ".hacs_lab_zwischenlager"

#: Der Name der Integrations-Beschreibung im Archiv.
_MANIFEST = "manifest.json"

#: Der Name der HACS-Beschreibung im Archiv.
_HACS_JSON = "hacs.json"


class InstallationsFehler(Exception):
    """Die Installation ist gescheitert -- der Text ist für Menschen."""


# ----------------------------------------------------------- Quelle


def waehle_anhang(anhaenge: dict[str, str]) -> str | None:
    """Die Adresse des einzigen ZIP-Anhangs, sonst ``None``.

    Ein Anhang zaehlt, wenn sein Name auf ``.zip`` endet (Gross-/
    Kleinschreibung egal) und eine Adresse dabeisteht. Gibt es genau
    einen, liefert er die Installation; gibt es keinen, greift der
    Rueckfall aufs Tag-Archiv; gibt es mehrere, ebenfalls -- zwischen
    zwei Zips zu wuerfeln ist Raterei, und genau die ruiniert
    Installationen. Andere Dateien (Signaturen, Pruefsummen, Tarbaelle)
    bleiben unberuehrt: sie sind Zusatz, nicht Konkurrenz.
    """
    treffer = [
        adresse
        for name, adresse in (anhaenge or {}).items()
        if name.lower().endswith(".zip") and adresse
    ]
    if len(treffer) == 1:
        return treffer[0]
    return None


async def beschaffe_archiv(forge: Forge, pfad: str, tag: str) -> tuple[bytes, str]:
    """Das Archiv zur Version -- Anhang zuerst, Tag-Archiv sonst.

    Zurueck kommen die Bytes und die Herkunft (``"anhang"`` oder
    ``"archiv"``) -- die Herkunft wandert ins Protokoll, weil sie beim
    Rueckwaertsdebuggen den Unterschied erklaert zwischen dem, was der
    Besitzer gebaut hat, und dem, was der Anbieter aus dem Quellstand
    gepackt hat.
    """
    try:
        releases: list[Release] = await forge.releases(pfad)
    except Exception:  # Anhang ist Bevorzugung, keine Pflicht
        releases = []
    for release in releases:
        if release.tag != tag:
            continue
        adresse = waehle_anhang(release.anhaenge)
        if adresse:
            return await forge.anhang(adresse), "anhang"
        break  # der passende Release ohne Anhang -- weiter macht kein Sinn
    return await forge.archiv(pfad, tag), "archiv"


# ------------------------------------------------- Ziel und Tausch


def lese_archiv_datei(archiv: bytes, name: str) -> bytes | None:
    """Liest eine Datei aus dem Archiv, ohne etwas zu entpacken.

    GitLab-Tag-Archive packen alles unter einen Ordner
    (``projekt-v1.2.0/...``), Release-Anhaenge stehen je nach Bauart in
    der Wurzel oder ebenfalls unter einem Ordner. Gesucht wird eine
    Datei dieses Namens genau eine Ebene unter der Wurzel oder in der
    Wurzel selbst -- mehrdeutige Treffer zaehlen als Fehlschlag, weil
    Raterei beim Installieren niemandem hilft.
    """
    treffer: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(archiv)) as zip_datei:
            for info in zip_datei.infolist():
                if info.is_dir() or "/" + name not in "/" + (info.filename or ""):
                    continue
                teile = [t for t in (info.filename or "").split("/") if t]
                if len(teile) <= 2 and teile[-1] == name:
                    treffer.append(info.filename)
            if len(treffer) == 1:
                return zip_datei.read(treffer[0])
    except zipfile.BadZipFile as fehlschlag:
        raise InstallationsFehler(
            "das Archiv ist kein ZIP -- ein Release-Anhang, der kein ZIP "
            "ist, wird nicht installiert (Befund M4b)"
        ) from fehlschlag
    return None


def _domain_aus_manifest(archiv: bytes) -> str:
    roh = lese_archiv_datei(archiv, _MANIFEST)
    if roh is None:
        raise InstallationsFehler(
            "im Archiv fehlt die manifest.json -- ohne sie kennt Home "
            "Assistant keine Integration"
        )
    befund = pruefe_manifest(roh)
    if not befund:
        raise InstallationsFehler("manifest.json untauglich: " + "; ".join(befund.fehler))
    domain = str(json.loads(roh).get("domain") or "")
    if not domain:
        raise InstallationsFehler("manifest.json nennt keine Domain")
    return domain


def _zielname(eintrag: Eintrag, archiv: bytes) -> str:
    """Der Verzeichnisname im Ziel: Domain bei Integrationen, sonst Projektname."""
    if eintrag.kategorie == "integration":
        return _domain_aus_manifest(archiv)
    name = eintrag.identitaet.full_name.rsplit("/", 1)[-1]
    return name or eintrag.identitaet.full_name


def _installiere_sync(
    archiv: bytes, kategorie: str, zielname: str, konfiguration: Path
) -> PurePosixPath:
    """Der schreibende Teil -- laeuft im Vorfuehrer (Executor), nie im Kreis.

    Zurueck kommt der Zielweg (relativ zur Konfiguration) fuer das
    Protokoll: die Deinstallation nimmt genau diesen Weg wieder.
    """
    plan = entpacken.plane(archiv)
    namen = [eintrag.name for eintrag in plan if not eintrag.ist_verzeichnis]

    hacs_roh = lese_archiv_datei(archiv, _HACS_JSON)
    hacs_daten: dict | None = None
    if hacs_roh is not None:
        try:
            hacs_daten = json.loads(hacs_roh)
        except json.JSONDecodeError as fehlschlag:
            raise InstallationsFehler(
                f"hacs.json ist kein gueltiges JSON: {fehlschlag}"
            ) from fehlschlag

    try:
        schnitt = zielpfade.ausschnitt(hacs_daten)
        zuordnung = zielpfade.waehle_eintraege(schnitt, namen)
    except zielpfade.ZielpfadFehler as fehlschlag:
        raise InstallationsFehler(str(fehlschlag)) from fehlschlag

    ziel = konfiguration / zielpfade.zielverzeichnis(kategorie, zielname)
    zwischenlager = konfiguration / ZWISCHENLAGER_NAME
    try:
        entpacken.installiere(archiv, zwischenlager, ziel, nur=zuordnung)
    except entpacken.EntpackFehler as fehlschlag:
        raise InstallationsFehler(str(fehlschlag)) from fehlschlag
    return PurePosixPath(*ziel.relative_to(konfiguration).parts)


# ---------------------------------------------------- Deinstallation


def _deinstalliere_sync(pfad_relativ: str, konfiguration: Path) -> None:
    """Entfernt ein installiertes Verzeichnis -- in einem Zug.

    Der Weg kommt aus dem Protokoll und wird hier noch einmal geprueft
    (:func:`zielpfade.ist_zielpfad`): die Ablage ist eine Datei, Dateien
    lassen sich von Hand veraendern, und ein veraenderter Eintrag darf
    nie dazu fuehren, dass hier etwas ausserhalb der Kategorie-Wurzeln
    wegbenannt wird.

    Die Reihenfolge ist dieselbe wie beim Installieren: erst das Ziel
    ins Zwischenlager wegbenennen (``.weg``), dann dort entfernen.
    Scheitert das Wegbenennen, steht das Ziel noch unberuehrt; scheitert
    das Entfernen, ist das Ziel zumindest verschwunden und das Lager
    raeumt der naechste Lauf auf -- halbe Zustaende gibt es im Ziel
    nicht.
    """
    rein = (pfad_relativ or "").strip()
    if not zielpfade.ist_zielpfad(rein):
        raise InstallationsFehler(
            f"untauglicher installierter Pfad: {pfad_relativ!r} -- die "
            "Deinstallation fasst nur bekannte Kategorie-Wurzeln an"
        )
    ziel = konfiguration.joinpath(*PurePosixPath(rein).parts)
    if not ziel.is_dir():
        raise InstallationsFehler(
            f"nichts installiert unter {pfad_relativ!r} -- schon entfernt?"
        )
    zwischenlager = konfiguration / ZWISCHENLAGER_NAME
    zwischenlager.mkdir(parents=True, exist_ok=True)
    weg = zwischenlager / (ziel.name + ".weg")
    shutil.rmtree(weg, ignore_errors=True)
    try:
        os.replace(ziel, weg)
    except OSError as schaden:
        raise InstallationsFehler(
            f"das Ziel laesst sich nicht wegbewegen: {schaden}"
        ) from schaden
    shutil.rmtree(weg, ignore_errors=True)


# ------------------------------------------------------- Ereigniskreis


async def installiere_version(
    hass: HomeAssistant, forge: Forge, eintrag: Eintrag, tag: str
) -> PurePosixPath:
    """Bringt die Version an ihren Ort und meldet den Zielweg.

    Quelle: Anhang des Releases, sonst Archiv des Tags (Stufe M4b).
    Netz im Ereigniskreis (ueber die aiohttp-Sitzung), Schreiben im
    Vorfuehrer -- Home Assistant blockiert die Schleife fuer niemanden.
    Fehler kommen als :class:`InstallationsFehler` mit Klartext; die
    aufrufende Entity reicht ihn als HomeAssistantError weiter.

    Der Zielweg (relativ zur Konfiguration) ist das Protokoll fuer die
    Deinstallation -- die aufrufende Stelle sorgt dafuer, dass er in der
    Ablage landet, noch bevor die Version als installiert gilt.
    """
    pfad = eintrag.identitaet.full_name
    archiv, _herkunft = await beschaffe_archiv(forge, pfad, tag)
    zielname = _zielname(eintrag, archiv)
    konfiguration = Path(hass.config.config_dir)
    return await hass.async_add_executor_job(
        _installiere_sync, archiv, eintrag.kategorie, zielname, konfiguration
    )


async def deinstalliere_version(hass: HomeAssistant, pfad_relativ: str) -> None:
    """Nimmt eine installierte Version weg -- den Weg aus dem Protokoll.

    Fehler sind Klartext und werden von der aufrufenden Stelle als
    HomeAssistantError weitergereicht. Was gefehlt hat, ist kein
    Fehlerbild, das hier entschaeft werden muss: die Meldung sagt,
    dass nichts (mehr) da ist.
    """
    konfiguration = Path(hass.config.config_dir)
    await hass.async_add_executor_job(_deinstalliere_sync, pfad_relativ, konfiguration)
