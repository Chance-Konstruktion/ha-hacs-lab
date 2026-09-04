"""Die Befehle der Oberflaeche -- Stufe M7.

Das Panel (``frontend/panel.js``) redet mit Home Assistant, nicht mit
der Welt: Diese Datei ist die ganze Schnittstelle zwischen beiden.
Sechs Befehle, mehr braucht kein Laden:

* ``hacs_lab/eintraege`` -- die Liste der beobachteten Repositories,
  mit Stand (installiert), neuester Version, Sternen und Verweisen
* ``hacs_lab/entdecken`` -- der Scan aus Stufe M6: ganze Instanz oder
  Gruppe, Ergebnisliste mit allem, was die Oberflaeche zeigt
* ``hacs_lab/detail`` -- Stammdaten, README und Releases eines
  Repositorys
* ``hacs_lab/hinzufuegen`` -- ein Fund aufnehmen (derselbe Weg wie der
  Dialog: Identitaet klaeren, Kategorie pruefen, Eintrag anlegen)
* ``hacs_lab/entfernen`` -- einen Eintrag aus der Liste nehmen
* ``hacs_lab/deinstallieren`` -- Stufe M4b: die installierten Dateien
  wegnehmen, den verzeichneten Weg entlang. Home Assistants
  update-Entities kennen kein Uninstall -- deshalb ist das hier ein
  Befehl, nicht ein Dienst von ihnen.

Installieren und aktualisieren geht bewusst NICHT durch diese Datei:
dafuer gibt es die update-Entities aus Stufe M5 mit ihrem
install-Dienst. Das Panel ruft den ganz normalen Home-Assistant-Dienst
-- genau wie jede andere Oberflaeche auch.

Bahn-Disziplin aus #13: ``config_flow.py`` und ``eintraege.py`` werden
hier nicht angefasst, nur ihre oeffentlichen Stuecke aufgerufen. Der
Scan schreibt nichts (Stufe M6), die Aufnahme bleibt die Entscheidung
der Bedienung.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .core.entdeckung import entdecke
from .core.forge import ForgeFehler, NichtGefunden
from .core.identity import SUFFIX, RepositoryIdentity
from .core.validierung import KATEGORIEN
from .eintraege import (
    BereitsVorhanden,
    KategorieUnbekannt,
    NichtVorhanden,
    kategorie_aus_topics,
)
from .installation import InstallationsFehler, deinstalliere_version
from .neustart import neustart_hinweis

if TYPE_CHECKING:
    from homeassistant.components.websocket_api.connection import ActiveConnection

    from . import Laufzeit

_LOGGER = logging.getLogger(__name__)

#: Kandidaten fuer die Projektbeschreibung, in dieser Reihenfolge
#: gefragt. Dateinamen sind keine Anbieterkenntnis -- jede Forge hat
#: Dateien, die Reihenfolge ist schlicht Gewohnheit.
README_KANDIDATEN = ("README.md", "readme.md", "Readme.md", "README.rst")


def _laufzeiten(hass: HomeAssistant) -> dict[str, Laufzeit]:
    """Die eingerichteten Instanzen, nach Host geordnet.

    Mehrere Instanzen (gitlab.com und die eigene) stehen nebeneinander
    -- genau dafuer traegt der storage_key den Host. Die Oberflaeche
    bekommt sie alle zu sehen.
    """
    karte: dict[str, Laufzeit] = {}
    for laufzeit in hass.data.get("hacs_lab", {}).values():
        forge = getattr(laufzeit, "forge", None)
        if forge is not None:
            karte[forge.host] = laufzeit
    return karte


def _laufzeit_nach_host(hass: HomeAssistant, host: str) -> Laufzeit | None:
    return _laufzeiten(hass).get(host)


def _entity_id(hass: HomeAssistant, storage_key: str) -> str | None:
    """Die update-Entity eines Eintrags, wie Home Assistant sie nennt."""
    registry = er.async_get(hass)
    return registry.async_get_entity_id("update", "hacs_lab", storage_key)


def _anzeigename(full_name: str, provider: str) -> str:
    """Der Name mit Kennzeichnung -- der Suffix gehoert dem Anbieter.

    GitLab traegt ``*lab``, Forgejo ``*forge`` (Stufe M9). Die Stelle
    hier fragt nach, statt beides zu wissen.
    """
    return full_name + SUFFIX.get(provider, "")


def _fund_anteil(laufzeit: Laufzeit, storage_key: str) -> dict[str, str]:
    """Was der letzte Lauf zu diesem Eintrag wusste (leer, wenn nichts)."""
    aktualisierer = getattr(laufzeit, "aktualisierer", None)
    daten = aktualisierer.data if aktualisierer is not None else None
    fund = (daten or {}).get(storage_key)
    if fund is None or fund.fehler is not None:
        return {}
    return {
        "neueste": fund.neueste,
        "tag": fund.tag,
        "veroeffentlicht_am": fund.veroeffentlicht_am,
    }


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "hacs_lab/eintraege"})
@websocket_api.async_response
async def ws_eintraege(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Die Liste alles Beobachteten, ueber alle Instanzen.

    Sterne und Beschreibung sind ein frischer Blick je Eintrag: was
    gestern drei Sterne hatte, kann heute fuenf haben. Ein Fehler
    dabei (Repository verschwunden, Netz weg) reisst die Liste nicht
    mit -- der Eintrag erscheint mit Fehlertext, wie der Lauf aus
    Stufe M5 ihn auch traegt.
    """
    zeilen: list[dict[str, Any]] = []
    for host, laufzeit in sorted(_laufzeiten(hass).items()):
        staende = getattr(laufzeit, "staende", None)
        for eintrag in laufzeit.eintraege.alle():
            zeile: dict[str, Any] = {
                "storage_key": eintrag.storage_key,
                "name": eintrag.anzeigename,
                "pfad": eintrag.identitaet.full_name,
                "kategorie": eintrag.kategorie,
                "host": host,
                "hinzugefuegt_am": eintrag.hinzugefuegt_am,
                "entity_id": _entity_id(hass, eintrag.storage_key),
            }
            zeile.update(_fund_anteil(laufzeit, eintrag.storage_key))
            stand = staende.stand(eintrag.storage_key) if staende is not None else None
            zeile["installiert"] = stand.installiert if stand else ""
            zeile["fehler"] = ""
            try:
                info = await laufzeit.forge.repository(eintrag.identitaet.full_name)
            except Exception as fehler:  # noqa: BLE001 - ein Eintrag, keine Liste
                zeile["fehler"] = str(fehler) or fehler.__class__.__name__
                _LOGGER.debug(
                    "Stammdaten zu %s gescheitert: %s",
                    eintrag.anzeigename,
                    zeile["fehler"],
                )
            else:
                zeile["beschreibung"] = info.beschreibung
                zeile["sterne"] = info.sterne
                zeile["offene_tickets"] = info.offene_tickets
                zeile["web_url"] = info.web_url
                zeile["tickets_url"] = info.tickets_url
                zeile["releases_url"] = info.releases_url
            zeilen.append(zeile)

    connection.send_result(
        msg["id"],
        {
            "eintraege": zeilen,
            "instanzen": sorted(_laufzeiten(hass)),
            "kategorien": list(KATEGORIEN),
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_lab/entdecken",
        vol.Required("host"): str,
        vol.Optional("gruppe", default=""): str,
        vol.Optional("mit_untergruppen", default=True): bool,
        vol.Optional("mit_entwicklung", default=False): bool,
    }
)
@websocket_api.async_response
async def ws_entdecken(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Der Scan aus Stufe M6: finden, nicht aufnehmen.

    Der Lauf schreibt nichts -- was davon in die Liste soll, entscheidet
    die Bedienung danach. Projekte mit ``hacs-development``-Topic
    bleiben aussen vor, ausser sie werden ausdruecklich gewuenscht.
    """
    laufzeit = _laufzeit_nach_host(hass, str(msg["host"]))
    if laufzeit is None:
        connection.send_error(
            msg["id"], "unbekannte_instanz", str(msg["host"]) + " ist nicht eingerichtet"
        )
        return

    try:
        funde = await entdecke(
            laufzeit.forge,
            gruppe=str(msg["gruppe"]) or None,
            mit_untergruppen=bool(msg["mit_untergruppen"]),
            mit_vorab=bool(msg["mit_entwicklung"]),
        )
    except ForgeFehler as fehler:
        connection.send_error(msg["id"], "forge_fehler", str(fehler))
        return

    ergebnis: list[dict[str, Any]] = []
    for fund in funde:
        info = fund.info
        ergebnis.append(
            {
                "full_name": info.full_name,
                "name": fund.anzeigename,
                "beschreibung": info.beschreibung,
                "sterne": info.sterne,
                "offene_tickets": info.offene_tickets,
                "letzte_version": fund.letzte_version,
                "kategorie": kategorie_aus_topics(info.topics) or "integration",
                "gueltig": fund.befund.gueltig,
                "fehler": "; ".join(fund.befund.fehler),
                "vorhanden": laufzeit.eintraege.vorhanden(fund.identitaet.storage_key),
                "web_url": info.web_url,
                "tickets_url": info.tickets_url,
                "releases_url": info.releases_url,
            }
        )
    connection.send_result(msg["id"], {"funde": ergebnis})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_lab/detail",
        vol.Required("host"): str,
        vol.Required("pfad"): str,
    }
)
@websocket_api.async_response
async def ws_detail(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Stammdaten, README und Releases eines Repositorys.

    Die Beschreibung wird als Klartext geliefert und im Panel gerendert
    -- welches Format sie hat, entscheidet das Projekt, nicht wir. Die
    Liste der Releases ist die gleiche, die der Update-Lauf sieht.
    """
    laufzeit = _laufzeit_nach_host(hass, str(msg["host"]))
    if laufzeit is None:
        connection.send_error(
            msg["id"], "unbekannte_instanz", str(msg["host"]) + " ist nicht eingerichtet"
        )
        return
    pfad = str(msg["pfad"])

    try:
        info = await laufzeit.forge.repository(pfad)
    except NichtGefunden as fehler:
        connection.send_error(msg["id"], "nicht_gefunden", str(fehler))
        return
    except ForgeFehler as fehler:
        connection.send_error(msg["id"], "forge_fehler", str(fehler))
        return

    releases: list[dict[str, Any]] = []
    try:
        releases = [
            {
                "tag": release.tag,
                "name": release.name,
                "beschreibung": release.beschreibung,
                "veroeffentlicht_am": release.veroeffentlicht_am,
                "vorabversion": release.vorabversion,
            }
            for release in await laufzeit.forge.releases(pfad)
        ]
    except Exception as fehler:  # noqa: BLE001 - Releases fehlen, Rest bleibt
        _LOGGER.debug("Releases zu %s gescheitert: %s", pfad, fehler)

    readme: str | None = None
    readme_datei = ""
    for kandidat in README_KANDIDATEN:
        try:
            roh = await laufzeit.forge.datei(pfad, kandidat, info.standardzweig)
        except ForgeFehler:
            continue
        readme = roh.decode("utf-8", errors="replace")
        readme_datei = kandidat
        break

    connection.send_result(
        msg["id"],
        {
            "info": {
                "full_name": info.full_name,
                "name": _anzeigename(info.full_name, laufzeit.forge.provider),
                "beschreibung": info.beschreibung,
                "sterne": info.sterne,
                "offene_tickets": info.offene_tickets,
                "archiviert": info.archiviert,
                "topics": list(info.topics),
                "standardzweig": info.standardzweig,
                "web_url": info.web_url,
                "tickets_url": info.tickets_url,
                "releases_url": info.releases_url,
            },
            "readme": readme,
            "readme_datei": readme_datei,
            "releases": releases,
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_lab/hinzufuegen",
        vol.Required("host"): str,
        vol.Required("pfad"): str,
        vol.Required("kategorie"): str,
    }
)
@websocket_api.async_response
async def ws_hinzufuegen(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Ein Repository aufnehmen -- derselbe Weg wie der Dialog aus M3.

    Identitaet klaeren (ein einziger API-Abruf, wie im Dialog), dann
    der Liste uebergeben: doppelte storage_key werden abgewiesen,
    unbekannte Kategorien ebenso. Die update-Entity entsteht durch den
    Beobachter aus Stufe M5 von selbst -- ohne Neustart.
    """
    laufzeit = _laufzeit_nach_host(hass, str(msg["host"]))
    if laufzeit is None:
        connection.send_error(
            msg["id"], "unbekannte_instanz", str(msg["host"]) + " ist nicht eingerichtet"
        )
        return
    pfad = str(msg["pfad"])

    try:
        info = await laufzeit.forge.repository(pfad)
    except NichtGefunden as fehler:
        connection.send_error(msg["id"], "nicht_gefunden", str(fehler))
        return
    except ForgeFehler as fehler:
        connection.send_error(msg["id"], "forge_fehler", str(fehler))
        return

    identitaet = RepositoryIdentity(
        provider=laufzeit.forge.provider,
        host=laufzeit.forge.host,
        provider_id=info.provider_id,
        full_name=info.full_name,
    )
    try:
        eintrag = await laufzeit.eintraege.hinzufuegen(identitaet, str(msg["kategorie"]))
    except BereitsVorhanden as fehler:
        connection.send_error(msg["id"], "bereits_vorhanden", str(fehler))
        return
    except KategorieUnbekannt as fehler:
        connection.send_error(msg["id"], "kategorie_unbekannt", str(fehler))
        return

    _LOGGER.info(
        "Custom Repository ueber die Oberflaeche aufgenommen: %s (%s)",
        eintrag.anzeigename,
        eintrag.kategorie,
    )
    # Der Beobachter aus Stufe M5 legt die update-Entity gleich an; noch
    # einen Herzschlag warten, dann kennt die Registry die Nummer.
    await hass.async_block_till_done()
    connection.send_result(
        msg["id"],
        {
            "eintrag": {
                "storage_key": eintrag.storage_key,
                "name": eintrag.anzeigename,
                "kategorie": eintrag.kategorie,
                "host": laufzeit.forge.host,
                "entity_id": _entity_id(hass, eintrag.storage_key),
            }
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_lab/entfernen",
        vol.Required("storage_key"): str,
    }
)
@websocket_api.async_response
async def ws_entfernen(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Einen Eintrag aus der Liste nehmen -- installierte Dateien bleiben.

    Dateien mitzuentfernen ist Stufe M4 (und wird dort ehrlich
    geloest); hier verschwindet nur die Beobachtung. Die zugehoerige
    update-Entity nimmt der Beobachter aus Stufe M5 mit.
    """
    schluessel = str(msg["storage_key"])
    for laufzeit in _laufzeiten(hass).values():
        if not laufzeit.eintraege.vorhanden(schluessel):
            continue
        try:
            entfernt = await laufzeit.eintraege.entfernen(schluessel)
        except NichtVorhanden as fehler:
            connection.send_error(msg["id"], "nicht_mehr_da", str(fehler))
            return
        _LOGGER.info(
            "Custom Repository ueber die Oberflaeche entfernt: %s",
            entfernt.anzeigename,
        )
        connection.send_result(
            msg["id"], {"entfernt": entfernt.anzeigename, "host": laufzeit.forge.host}
        )
        return

    connection.send_error(
        msg["id"], "nicht_mehr_da", schluessel + " steht in keiner Liste"
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_lab/deinstallieren",
        vol.Required("storage_key"): str,
    }
)
@websocket_api.async_response
async def ws_deinstallieren(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Installierte Dateien entfernen -- den verzeichneten Weg (M4b).

    Der Eintrag bleibt in der Liste (dafuer gibt es ``entfernen``);
    hier verschwinden nur die Dateien, und der Stand vergisst Version
    und Weg. Ohne verzeichneten Weg (installiert vor M4b) kommt die
    ehrliche Ansage: erst neu installieren, dann laesst sich auch
    sauber entfernen.
    """
    schluessel = str(msg["storage_key"])
    for laufzeit in _laufzeiten(hass).values():
        eintrag = laufzeit.eintraege.finde(schluessel)
        if eintrag is None:
            continue
        stand = laufzeit.staende.stand(schluessel)
        if not stand.installiert:
            connection.send_error(msg["id"], "nichts_installiert", "nichts installiert")
            return
        if not stand.pfad:
            connection.send_error(
                msg["id"],
                "kein_weg",
                "kein installierter Pfad verzeichnet (installiert vor M4b?) "
                "-- einmal neu installieren, dann laesst sich auch "
                "entfernen",
            )
            return
        try:
            await deinstalliere_version(hass, stand.pfad)
        except InstallationsFehler as fehlschlag:
            connection.send_error(
                msg["id"], "deinstallation_fehlgeschlagen", str(fehlschlag)
            )
            return
        await laufzeit.staende.setzen(schluessel, installiert="", pfad="")
        neustart_hinweis(hass, eintrag, stand.installiert, "deinstallation")
        _LOGGER.info(
            "Custom Repository ueber die Oberflaeche deinstalliert: %s",
            eintrag.anzeigename,
        )
        connection.send_result(
            msg["id"], {"deinstalliert": eintrag.anzeigename, "host": laufzeit.forge.host}
        )
        return

    connection.send_error(
        msg["id"], "nicht_mehr_da", schluessel + " steht in keiner Liste"
    )


#: Alle Befehle dieser Datei -- ``__init__.py`` meldet sie der Reihe nach an.
BEFEHLE = (
    ws_eintraege,
    ws_entdecken,
    ws_detail,
    ws_hinzufuegen,
    ws_entfernen,
    ws_deinstallieren,
)
