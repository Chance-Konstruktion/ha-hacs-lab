"""Schalter je Eintrag: Vorabversionen mitnehmen oder nicht.

Stufe M5: «Schalter je Eintrag fuer Vorabversionen». Der Schalter liegt
im Stand des Eintrags (Ablage, Feld ``stand``) und dreht sofort eine
neue Runde des Aktualisierers -- die Auswahl der neuesten Version
sollte nach dem Schalten sichtbar werden, nicht erst im naechsten Takt.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aktualisierer import HacsLabAktualisierer, hole_aktualisierer
from .const import DOMAIN

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
    """Ein Schalter je Eintrag -- wachsend und schrumpfend mit der Liste."""
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).get(eintrag.entry_id)
    if laufzeit is None:
        return

    aktualisierer = hole_aktualisierer(hass, eintrag)
    if aktualisierer is None:
        return
    await laufzeit.staende.laden()

    entities: dict[str, HacsLabVorabSchalter] = {}

    def _anlegen(eintrag_obj: Eintrag) -> None:
        entity = HacsLabVorabSchalter(laufzeit.staende, aktualisierer, eintrag_obj)
        entities[eintrag_obj.storage_key] = entity
        async_add_entities([entity])

    for eintrag_obj in laufzeit.eintraege.alle():
        _anlegen(eintrag_obj)

    def _bei_aenderung(art: str, eintrag_obj: Eintrag) -> None:
        if art == "hinzugefuegt":
            _anlegen(eintrag_obj)
            return
        entity = entities.pop(eintrag_obj.storage_key, None)
        if entity is not None and entity.hass is not None:
            hass.async_create_task(entity.async_remove())

    laufzeit.eintraege.melde_aenderungen(_bei_aenderung)


class HacsLabVorabSchalter(SwitchEntity):
    """Vorabversionen eines Eintrags erlauben oder nicht."""

    _attr_should_poll = False
    _attr_icon = "mdi:alpha-v-circle-outline"

    def __init__(
        self,
        staende: Staende,
        aktualisierer: HacsLabAktualisierer,
        eintrag: Eintrag,
    ) -> None:
        self._staende = staende
        self._aktualisierer = aktualisierer
        self._eintrag = eintrag
        self._attr_unique_id = eintrag.storage_key + "_vorabversionen"
        self._attr_name = eintrag.anzeigename + " — Vorabversionen"

    @property
    def is_on(self) -> bool:
        return self._staende.stand(self._eintrag.storage_key).vorabversionen

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"kategorie": self._eintrag.kategorie}

    async def _drehen(self, an: bool) -> None:
        await self._staende.setzen(self._eintrag.storage_key, vorabversionen=an)
        self.async_write_ha_state()
        # Sofort neue Runde: die Vorab-Entscheid aendert die neueste Version.
        await self._aktualisierer.async_request_refresh()
        _LOGGER.info(
            "Vorabversionen fuer %s: %s",
            self._eintrag.anzeigename,
            "mitgenommen" if an else "weggelassen",
        )

    async def async_turn_on(self, **_: object) -> None:
        await self._drehen(True)

    async def async_turn_off(self, **_: object) -> None:
        await self._drehen(False)
