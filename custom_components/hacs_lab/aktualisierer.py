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
from homeassistant.helpers import issue_registry
from homeassistant.helpers.issue_registry import IssueSeverity
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


def _kennung(schluessel: str) -> str:
    """Macht aus einem Speicherschluessel eine Issue-Kennung (a-z, 0-9, _)."""
    gesaeubert = "".join(
        zeichen if zeichen.isalnum() and zeichen.isascii() else "_"
        for zeichen in schluessel.lower()
    )
    return gesaeubert.strip("_") or "eintrag"


#: Wortbruchstuecke, die auf ein Token-Problem deuten (M1-Klartexte).
_TOKEN_HINWEISE = ("token", "berechtigung", "401", "403")


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
            self._melde_token_problem(str(fehler))
            raise UpdateFailed(str(fehler)) from fehler
        except Exception as fehler:
            raise UpdateFailed(f"unerwarteter Fehler: {fehler}") from fehler

        fehlerfunde = [fund for fund in funde.values() if fund.fehler]
        for fund in fehlerfunde:
            _LOGGER.warning(
                "Update-Pruefung gescheitert fuer %s: %s", fund.schluessel, fund.fehler
            )
        if fehlerfunde and len(fehlerfunde) == len(funde):
            self._melde_token_problem(fehlerfunde[0].fehler or "")
            raise UpdateFailed(fehlerfunde[0].fehler or "alle Eintraege gescheitert")

        self._reparaturen_ableiten(funde)
        return funde

    def _melde_token_problem(self, grund: str) -> None:
        """Stufe M8: ein Token-Problem ist eine Reparatur-Meldung wert.

        Aufgeraeumt wird sie beim naechsten erfolgreichen Lauf --
        :func:`_reparaturen_ableiten` loescht sie mit.
        """
        if not any(hinweis in grund.lower() for hinweis in _TOKEN_HINWEISE):
            return
        issue_registry.async_create_issue(
            self.hass,
            DOMAIN,
            "token_problem",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="token_problem",
            translation_placeholders={"host": self.forge.host},
        )

    def _reparaturen_ableiten(self, funde: dict[str, Fund]) -> None:
        """Je Fund eine Reparatur-Spur: verschwunden, krank oder gesund.

        Ein 404-Fund heisst verschwunden (geloesscht oder verschoben);
        alles andere Fehlerhafte bekommt die allgemeine Meldung. Gesunde
        Eintraege raeumen ihre Meldung weg -- ein Problem, das weg ist,
        soll nicht auf dem Brett bleiben. Der erfolgreiche Lauf nimmt
        auch das Token-Problem mit.
        """
        for schluessel, fund in funde.items():
            kennung = _kennung(schluessel)
            krank = "repo_krank_" + kennung
            verschwunden = "repo_verschwunden_" + kennung
            if fund.fehler is None:
                issue_registry.async_delete_issue(self.hass, DOMAIN, krank)
                issue_registry.async_delete_issue(self.hass, DOMAIN, verschwunden)
            elif "nicht gefunden" in fund.fehler:
                issue_registry.async_delete_issue(self.hass, DOMAIN, krank)
                issue_registry.async_create_issue(
                    self.hass,
                    DOMAIN,
                    verschwunden,
                    is_fixable=False,
                    severity=IssueSeverity.WARNING,
                    translation_key="repo_verschwunden",
                    translation_placeholders={"name": schluessel, "grund": fund.fehler},
                )
            else:
                issue_registry.async_delete_issue(self.hass, DOMAIN, verschwunden)
                issue_registry.async_create_issue(
                    self.hass,
                    DOMAIN,
                    krank,
                    is_fixable=False,
                    severity=IssueSeverity.WARNING,
                    translation_key="repo_krank",
                    translation_placeholders={"name": schluessel, "grund": fund.fehler},
                )
        issue_registry.async_delete_issue(self.hass, DOMAIN, "token_problem")


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
