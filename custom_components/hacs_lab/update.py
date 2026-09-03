"""Update-Entities je Eintrag -- Stufe M5, die sichtbare Seite.

Jedes beobachtete Custom Repository bekommt eine ``update``-Entity:
installierte Version, neueste Version, Release-Notizen, und einen
``install``-Dienst, der das Archiv des Tags ueber die M4a-Naht an den
Zielort tauscht (siehe :mod:`.installation`). Neue Eintraege erscheinen
ohne Neustart als Entity, entfernte verschwinden -- genau das verlangt
die Abnahme: «ein neues Release im GitLab erscheint ohne Zutun in HA».
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from hacs_lab.core.aktualisierungen import Fund

from .aktualisierer import HacsLabAktualisierer, hole_aktualisierer
from .const import DOMAIN
from .installation import InstallationsFehler, installiere_version

if TYPE_CHECKING:
    from . import Laufzeit
    from .eintraege import Eintrag
    from .stand import Staende

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    eintrag: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet die M5-Wabe: Spur holen, Entities anlegen, weiter wachsen."""
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).get(eintrag.entry_id)
    if laufzeit is None:
        return

    aktualisierer = hole_aktualisierer(hass, eintrag)
    if aktualisierer is None:
        return
    await laufzeit.staende.laden()
    await aktualisierer.async_config_entry_first_refresh()

    entities: dict[str, HacsLabUpdateEntity] = {}

    def _anlegen(eintrag_obj: Eintrag) -> None:
        entity = HacsLabUpdateEntity(laufzeit, aktualisierer, eintrag_obj)
        entities[eintrag_obj.storage_key] = entity
        async_add_entities([entity])

    for eintrag_obj in laufzeit.eintraege.alle():
        _anlegen(eintrag_obj)

    def _bei_aenderung(art: str, eintrag_obj: Eintrag) -> None:
        if art == "hinzugefuegt":
            _anlegen(eintrag_obj)
            # Frischer Eintrag, frischer Fund: gleich eine Runde ansetzen,
            # statt auf den naechsten Takt zu warten. async_create_task,
            # weil der Beobachter selbst synchron ist.
            hass.async_create_task(aktualisierer.async_request_refresh())
            return
        entity = entities.pop(eintrag_obj.storage_key, None)
        if entity is not None and entity.hass is not None:
            hass.async_create_task(entity.async_remove())

    laufzeit.eintraege.melde_aenderungen(_bei_aenderung)


class HacsLabUpdateEntity(UpdateEntity):
    """Eine ``update``-Entity je Custom Repository."""

    _attr_should_poll = False

    def __init__(
        self,
        laufzeit: Laufzeit,
        aktualisierer: HacsLabAktualisierer,
        eintrag: Eintrag,
    ) -> None:
        self._forge = laufzeit.forge
        self._staende: Staende = laufzeit.staende
        self._eintrag = eintrag
        self._aktualisierer = aktualisierer
        self._attr_unique_id = eintrag.storage_key
        self._attr_name = eintrag.anzeigename
        self._attr_title = eintrag.anzeigename
        self._attr_supported_features = UpdateEntityFeature.INSTALL
        self._laeuft_gerade = False

    @property
    def in_progress(self) -> bool:
        """Eigene Fassung statt ``_attr_``: steuerbar waehrend des Laufs."""
        return self._laeuft_gerade

    async def async_added_to_hass(self) -> None:
        """Auf den Takt horchen -- jede Runde schreibt den neuen Stand."""
        self.async_on_remove(self._aktualisierer.async_add_listener(self._schreibe))

    def _schreibe(self) -> None:
        if self.hass is not None:
            self.async_write_ha_state()

    @property
    def _fund(self) -> Fund | None:
        daten: dict[str, Fund] | None = self._aktualisierer.data
        if daten is None:
            return None
        return daten.get(self._eintrag.storage_key)

    @property
    def available(self) -> bool:
        # Stufe M8: ein Instanz-Ausfall macht die Entity unehrlich-verfuegbar,
        # aber der letzte Fund bleibt im Koordinator -- alte Daten werden
        # behalten, nicht geloescht, und kommen zurueck, sobald es wieder geht.
        if not self._aktualisierer.last_update_success:
            return False
        fund = self._fund
        return fund is None or fund.fehler is None

    @property
    def installed_version(self) -> str | None:
        installiert = self._staende.stand(self._eintrag.storage_key).installiert
        return installiert or None

    @property
    def latest_version(self) -> str | None:
        fund = self._fund
        if fund is None or fund.fehler is not None:
            return None
        return fund.neueste or None

    @property
    def release_summary(self) -> str | None:
        fund = self._fund
        if fund is None or fund.fehler is not None or not fund.notizen:
            return None
        return fund.notizen

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        fund = self._fund
        if fund is None:
            return {}
        return {
            "quelle": fund.quelle,
            "tag": fund.tag,
            "veroeffentlicht_am": fund.veroeffentlicht_am,
            "kategorie": self._eintrag.kategorie,
            "vorabversionen": self._staende.stand(
                self._eintrag.storage_key
            ).vorabversionen,
            "fehler": fund.fehler or "",
        }

    async def async_install(
        self, version: str | None = None, backup: bool = False
    ) -> None:
        """Installiert die neueste Version ueber die M4a-Naht.

        Eine bestimmte aeltere Version zu waehlen ist bewusst noch nicht
        dabei: der Lauf traegt nur die neueste je Eintrag. Das Feld
        ``version`` wird geprueft und abgewiesen, wenn es nicht die
        neueste ist -- lieber ehrlich meckern als heimlich das Falsche
        installieren.
        """
        fund = self._fund
        if fund is None or fund.fehler is not None or not fund.tag:
            raise HomeAssistantError(
                "kein Stand zum Installieren -- der letzte Lauf schlug fehl"
            )
        if version is not None and version != fund.neueste:
            raise HomeAssistantError(
                f"nur die neueste Version ({fund.neueste}) ist installierbar"
            )
        self._laeuft_gerade = True
        self._schreibe()
        try:
            await installiere_version(self.hass, self._forge, self._eintrag, fund.tag)
        except InstallationsFehler as fehlschlag:
            raise HomeAssistantError(str(fehlschlag)) from fehlschlag
        finally:
            self._laeuft_gerade = False
        await self._staende.setzen(self._eintrag.storage_key, installiert=fund.neueste)
        self._schreibe()
        _LOGGER.info(
            "%s auf %s installiert",
            self._eintrag.anzeigename,
            fund.neueste,
        )
