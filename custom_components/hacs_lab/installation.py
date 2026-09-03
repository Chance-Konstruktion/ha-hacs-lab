"""Installationsnaht: das Archiv eines Tags wird an seinen Zielort getauscht.

Stufe M5 verlangt einen ``install``-Dienst auf den update-Entities. Die
hier gezeichnete Naht ist bewusst schmal und nutzt nur, was der Kern
(Stufe M4a) bereits mitbringt:

* Quelle: das Archiv des gewaehlten Tags -- ueber ``forge.archiv``,
  dahinter steckt die Anbieterkenntnis. Die Bevorzugung eines
  Release-Anhangs bleibt Stufe M4b (Issue #4), ebenso Deinstallation
  und Neustart-Hinweise.
* Ziel: ``zielpfade.zielverzeichnis`` je Kategorie; bei Integrationen
  liefert die ``manifest.json`` aus dem Archiv den Domain-Namen.
* Ausschnitt: ``hacs.json`` aus dem Archiv, ausgewertet vom Kern.
* Tausch: ``entpacken.installiere`` -- Zwischenlager, atomarer Tausch,
  Rueckholung bei Abbruch. Das Zwischenlager liegt unter der
  Home-Assistant-Konfiguration, damit Tausch und Ziel auf demselben
  Dateisystem liegen (Forderung aus M4a).

Metadaten (manifest.json, hacs.json) werden hier nur GELESEN, nie
entpackt -- das Schreiben bleibt allein beim geprueften Weg des Kerns.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from hacs_lab.core import entpacken, zielpfade
from hacs_lab.core.validierung import pruefe_manifest

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from hacs_lab.core.forge import Forge

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


def lese_archiv_datei(archiv: bytes, name: str) -> bytes | None:
    """Liest eine Datei aus dem Archiv, ohne etwas zu entpacken.

    GitLab-Tag-Archive packen alles unter einen Ordner
    (``projekt-v1.2.0/...``). Gesucht wird eine Datei dieses Namens
    genau eine Ebene unter der Wurzel oder in der Wurzel selbst --
    mehrdeutige Treffer zaehlen als Fehlschlag, weil Raterei beim
    Installieren niemandem hilft.
    """
    treffer: list[str] = []
    with zipfile.ZipFile(io.BytesIO(archiv)) as zip_datei:
        for info in zip_datei.infolist():
            if info.is_dir() or "/" + name not in "/" + (info.filename or ""):
                continue
            teile = [t for t in (info.filename or "").split("/") if t]
            if len(teile) <= 2 and teile[-1] == name:
                treffer.append(info.filename)
        if len(treffer) == 1:
            return zip_datei.read(treffer[0])
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
) -> None:
    """Der schreibende Teil -- laeuft im Vorfuehrer (Executor), nie im Kreis."""
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


async def installiere_version(
    hass: HomeAssistant, forge: Forge, eintrag: Eintrag, tag: str
) -> None:
    """Holt das Archiv zum Tag und tauscht es an den Zielort.

    Netz im Ereigniskreis (ueber die aiohttp-Sitzung), Schreiben im
    Vorfuehrer -- Home Assistant blockiert die Schleife fuer niemanden.
    Fehler kommen als :class:`InstallationsFehler` mit Klartext; die
    aufrufende Entity reicht ihn als HomeAssistantError weiter.
    """
    pfad = eintrag.identitaet.full_name
    archiv = await forge.archiv(pfad, tag)
    zielname = _zielname(eintrag, archiv)
    konfiguration = Path(hass.config.config_dir)
    await hass.async_add_executor_job(
        _installiere_sync, archiv, eintrag.kategorie, zielname, konfiguration
    )
