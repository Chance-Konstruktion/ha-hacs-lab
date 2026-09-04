"""Home-Assistant-Schicht von HACS*lab (Stufe M2: das Geruest).

Die Trennung ist Absicht und Architektur-Entscheidung: alles, was ohne
Home Assistant auskommt, liegt in ``hacs_lab/core`` und ist dort ohne
HA-Installation testbar. Diese Schicht hier macht nichts Eigenes --
sie reicht Home Assistants aiohttp-Sitzung an den HTTP-Klienten
weiter (ARCHITEKTUR.md, Entscheidung 3) und haengt die Bausteine des
Kerns an einander.

Wie diese Integration den Kern findet: ``hacs_lab`` liegt im
Entwicklungs-Check-out neben ``custom_components``. Beim Lauf aus einem
ausgepackten Stand liegt es ebenso daneben -- deshalb reicht ein
einziger Fallback auf das Nachbarverzeichnis. Der endgueltige Vertrieb
(pip-Paket oder Release-Form) ist Stufe M10.
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

if importlib.util.find_spec("hacs_lab") is None:
    # Lauf aus dem Entwicklungs- oder Release-Verzeichnis: der Kern
    # liegt zwei Ebenen hoeher, direkt neben custom_components.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from homeassistant.components import websocket_api as ha_websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from hacs_lab.core.forge import ForgeFehler
from hacs_lab.core.gitlab_forge import GitLabForge
from hacs_lab.http_aiohttp import AiohttpClient

from .ablage import Ablage
from .const import (
    ABLAGE_VERSION,
    CONF_ABSTAND_MINUTEN,
    CONF_HOST,
    CONF_TOKEN,
    DOMAIN,
    STANDARD_ABSTAND_MINUTEN,
    ablage_schluessel,
)
from .eintraege import Eintraege
from .frontend import richten as oberflaeche_richten
from .websocket_api import BEFEHLE

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Einmal je Laden der Komponente: die Oberflaeche (Stufe M7).

    WebSocket-Befehle und Panel werden hier angemeldet, nicht je
    Eintrag -- sie gehoeren der Integration, nicht der Instanz. Das
    Panel bleibt in der Sidebar stehen, auch wenn die letzte Instanz
    entfernt wird; die Liste zeigt dann ehrlich Leere. Der Alias beim
    Import ist Absicht: unser Modul heisst genauso wie das von Home
    Assistant (uebliche Namensgebung fuer Befehl-Dateien).
    """
    await oberflaeche_richten(hass)
    for befehl in BEFEHLE:
        ha_websocket_api.async_register_command(hass, befehl)
    return True


class HacsLabKoordinator(DataUpdateCoordinator[dict[str, int | str]]):
    """Herzschlag gegen die Instanz.

    M2 fragt hier nur, was ohnehin gefragt wird: die Projekte zum Topic
    ``hacs``. Das beweist Sitzung, Token und API auf jedem Takt und
    haelt die Instanz warm -- M5 haengt an dieselbe Stelle die echten
    Update-Laeufe.
    """

    def __init__(
        self, hass: HomeAssistant, eintrag: ConfigEntry, forge: GitLabForge
    ) -> None:
        minuten = int(
            eintrag.options.get(CONF_ABSTAND_MINUTEN) or STANDARD_ABSTAND_MINUTEN
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=eintrag,
            name=f"{DOMAIN}_{forge.host}",
            update_interval=timedelta(minutes=minuten),
        )
        self.forge = forge

    async def _async_update_data(self) -> dict[str, int | str]:
        try:
            funde = await self.forge.suche_nach_topic()
        except ForgeFehler as fehler:
            raise UpdateFailed(str(fehler)) from fehler
        except Exception as fehler:
            # Breit gefasst mit Absicht: ein stockender Takt darf Home
            # Assistant nie umwerfen, nur einen Wiederholungsversuch
            # ausloesen.
            raise UpdateFailed(f"unerwarteter Fehler: {fehler}") from fehler
        return {
            "instanz": self.forge.host,
            "gefundene_projekte": len(funde),
        }


@dataclass
class Laufzeit:
    """Was ein eingerichteter Eintrag im Arbeitsspeicher braucht.

    Seit Stufe M3 gehoert die Liste der Custom Repositories dazu: sie
    wird beim Richten aus der Ablage gelesen und bleibt fuer den
    Optionsdialog greifbar.
    """

    forge: GitLabForge
    koordinator: HacsLabKoordinator
    ablage: Ablage
    eintraege: Eintraege


async def async_setup_entry(hass: HomeAssistant, eintrag: ConfigEntry) -> bool:
    """Eintrag richten: Sitzung, Klient, Forge, Ablage, Herzschlag.

    Der erste Herzschlag entscheidet: schlaegt er fehl, meldet sich der
    Eintrag als "nicht bereit" und Home Assistant versucht spaeter
    erneut -- ehrlicher als ein scheinbar eingerichteter Eintrag ohne
    Verbindung.
    """
    sitzung = async_get_clientsession(hass)
    klient = AiohttpClient(sitzung, eintrag.data.get(CONF_TOKEN) or None)
    forge = GitLabForge(klient, eintrag.data[CONF_HOST])

    ablage = Ablage(
        Store(hass, ABLAGE_VERSION, ablage_schluessel(eintrag.data[CONF_HOST]))
    )
    # Geladen und gleich gehalten: Frueher verfiel das Ergebnis hier,
    # die Liste der Eintraege blieb unlesbar -- seit Stufe M3 gehoert
    # sie in die Laufzeit (Nachschau zu #13).
    eintraege = await Eintraege.aus_ablage(ablage)

    koordinator = HacsLabKoordinator(hass, eintrag, forge)
    await koordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[eintrag.entry_id] = Laufzeit(
        forge=forge, koordinator=koordinator, ablage=ablage, eintraege=eintraege
    )
    # Stufe M5: die Waben des Vorhabens -- eine update-Entity je Eintrag
    # samt Vorab-Schalter. Erst nach dem Herzschlag: steht die Verbindung
    # nicht, gibt es nichts zu beobachten, und der Eintrag meldet sich
    # ohnehin als nicht bereit.
    await hass.config_entries.async_forward_entry_setups(eintrag, ("update", "switch"))
    eintrag.async_on_unload(eintrag.add_update_listener(_abstand_geaendert))
    _LOGGER.info("HACS*lab eingerichtet fuer %s", forge.host)
    return True


async def async_unload_entry(hass: HomeAssistant, eintrag: ConfigEntry) -> bool:
    """Eintrag abmelden. Die Sitzung gehoert Home Assistant und bleibt."""
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).pop(eintrag.entry_id, None)
    waben_entladen = await hass.config_entries.async_unload_platforms(
        eintrag, ("update", "switch")
    )
    if laufzeit is not None:
        await laufzeit.koordinator.async_shutdown()
        aktualisierer = getattr(laufzeit, "aktualisierer", None)
        if aktualisierer is not None:
            await aktualisierer.async_shutdown()
    return waben_entladen


async def _abstand_geaendert(hass: HomeAssistant, eintrag: ConfigEntry) -> None:
    """Optionswechsel ohne Neustart: nur der Takt wird neu gesetzt."""
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).get(eintrag.entry_id)
    if laufzeit is None:
        return
    minuten = int(eintrag.options.get(CONF_ABSTAND_MINUTEN) or STANDARD_ABSTAND_MINUTEN)
    laufzeit.koordinator.update_interval = timedelta(minutes=minuten)
    _LOGGER.info("Abstand fuer %s auf %s Minuten gesetzt", laufzeit.forge.host, minuten)
