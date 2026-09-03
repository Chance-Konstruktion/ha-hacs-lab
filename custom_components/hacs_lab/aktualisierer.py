"""Der Aktualisierer: periodischer Lauf der Update-Erkennung.

Stufe M5 haengt die echten Update-Laeufe an den Takt des Herzschlags
(siehe ``__init__.py``): gleicher Abstand, gleiche Einstelloption
``abstand_minuten``, gleiches Verhalten bei Ausfällen -- Home
Assistant wiederholt, statt umzufallen.

Warum eine eigene Datei und kein Ausbau des M2-Koordinators: die
Geruest-Datei gehoert Bahn C (Stufe M0.5, #11), die Bahnen aus #13
fassen getrennte Dateien an. Der M2-Koordinator bleibt, was er ist --
Herzschlag -- und dieser hier fuehrt die Eintraege-Liste je Takt durch
den Kern-Lauf. Die Verschmelzung beider ist eine spaeteren Stufe
ueberlassen.

Der Zugriff erfolgt ueber :func:`hole_aktualisierer`: die Waben (update,
switch) holen sich hier ihre gemeinsame Spur, beim ersten Mal entsteht
sie und haengt sich an die Laufzeit des Eintrags. ``Laufzeit`` ist eine
Datenklasse ohne eigene Felder dafuer -- das dynamische Anhaengen ist
die bewusste Naht, bis M0.5 die Form der Laufzeit geklaert hat.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from hacs_lab.core.aktualisierungen import Fund, Pruefauftrag, lauf
from hacs_lab.core.forge import ForgeFehler

from .const import (
    CONF_ABSTAND_MINUTEN,
    DOMAIN,
    STANDARD_ABSTAND_MINUTEN,
)
from .stand import Staende

if TYPE_CHECKING:
    from hacs_lab.core.gitlab_forge import GitLabForge

    from . import Laufzeit
    from .eintraege import Eintraege

_LOGGER = logging.getLogger(__name__)


class HacsLabAktualisierer(DataUpdateCoordinator[dict[str, Fund]]):
    """Fuehrt die Liste je Takt durch den Kern-Lauf der Stufe M5."""

    def __init__(
        self,
        hass: HomeAssistant,
        eintrag: ConfigEntry,
        forge: GitLabForge,
        eintraege: Eintraege,
        staende: Staende,
    ) -> None:
        minuten = int(
            eintrag.options.get(CONF_ABSTAND_MINUTEN) or STANDARD_ABSTAND_MINUTEN
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=eintrag,
            name=f"{DOMAIN}_aktualisierer_{forge.host}",
            update_interval=timedelta(minutes=minuten),
        )
        self.forge = forge
        self.eintraege = eintraege
        self.staende = staende

    async def _async_update_data(self) -> dict[str, Fund]:
        """Alle Eintraege pruefen; Instanz-Fehler werden Wiederholung.

        Ein fehlerhaftes Repository bleibt ein Fund mit Fehlertext --
        genau das verlangt die Roadmap (der Lauf der anderen bricht
        nicht ab). Scheitert ALLES, liegt es an der Instanz oder am
        Netz, und der Takt versuch es erneut wie der Herzschlag auch.
        """
        auftraege = [
            Pruefauftrag(
                schluessel=eintrag.storage_key,
                pfad=eintrag.identitaet.full_name,
                installiert=self.staende.stand(eintrag.storage_key).installiert,
                mit_vorabversionen=(
                    self.staende.stand(eintrag.storage_key).vorabversionen
                ),
            )
            for eintrag in self.eintraege.alle()
        ]
        if not auftraege:
            return {}

        try:
            funde = await lauf(self.forge, auftraege)
        except ForgeFehler as fehler:
            raise UpdateFailed(str(fehler)) from fehler
        except Exception as fehler:
            raise UpdateFailed(f"unerwarteter Fehler: {fehler}") from fehler

        fehlerfunde = [fund for fund in funde.values() if fund.fehler]
        for fund in fehlerfunde:
            _LOGGER.warning(
                "Update-Pruefung gescheitert fuer %s: %s", fund.schluessel, fund.fehler
            )
        if fehlerfunde and len(fehlerfunde) == len(funde):
            raise UpdateFailed(fehlerfunde[0].fehler or "alle Eintraege gescheitert")
        return funde


async def _takt_geaendert(hass: HomeAssistant, eintrag: ConfigEntry) -> None:
    """Optionswechsel: der Aktualisierer laeuft im selben Takt weiter."""
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).get(eintrag.entry_id)
    aktualisierer = getattr(laufzeit, "aktualisierer", None) if laufzeit else None
    if aktualisierer is None:
        return
    minuten = int(eintrag.options.get(CONF_ABSTAND_MINUTEN) or STANDARD_ABSTAND_MINUTEN)
    aktualisierer.update_interval = timedelta(minutes=minuten)
    _LOGGER.info(
        "Aktualisierer-Takt fuer %s auf %s Minuten gesetzt",
        getattr(laufzeit, "forge", None) and laufzeit.forge.host,
        minuten,
    )


def hole_aktualisierer(
    hass: HomeAssistant, eintrag: ConfigEntry
) -> HacsLabAktualisierer | None:
    """Die M5-Spur eines Eintrags -- entsteht beim ersten Griff.

    Idempotent und synchron mit Absicht: die Waben-Plattformen richten
    nacheinander, niemand wartet dazwischen. Der Takt-Beobachter wird
    genau einmal angemeldet, naemlich mit dem Aktualisierer selbst.
    """
    laufzeit: Laufzeit | None = hass.data.get(DOMAIN, {}).get(eintrag.entry_id)
    if laufzeit is None:
        return None

    staende = getattr(laufzeit, "staende", None)
    if staende is None:
        staende = Staende(laufzeit.ablage)
        laufzeit.staende = staende  # noqa: B010 - die Naht, s. Moduldoku

    aktualisierer = getattr(laufzeit, "aktualisierer", None)
    if aktualisierer is None:
        aktualisierer = HacsLabAktualisierer(
            hass, eintrag, laufzeit.forge, laufzeit.eintraege, staende
        )
        laufzeit.aktualisierer = aktualisierer  # noqa: B010 - die Naht
        eintrag.async_on_unload(eintrag.add_update_listener(_takt_geaendert))
    return aktualisierer
