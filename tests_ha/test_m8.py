"""Stufe M8, erster Bauabschnitt: Diagnose, Reparaturen, Ausfall-Festigkeit.

Diagnose ohne Token im Klartext (die Abnahme greift das ganze
Diagnose-Woerterbuch ab), Reparatur-Meldungen je Fehlerfall mit
Aufraeumen, Instanz-Ausfall ohne Datenverlust, und die Migrations-Faelle
der Ablage.
"""

from __future__ import annotations

import json
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.hacs_lab.ablage import migriere
from custom_components.hacs_lab.const import CONF_HOST, CONF_TOKEN, DOMAIN
from custom_components.hacs_lab.diagnostics import (
    async_get_config_entry_diagnostics,
)
from hacs_lab.core.identity import RepositoryIdentity

from .test_m5 import (
    STORAGE_KEY,
    eintrag_daten,
    herzschlag,
    mock_eintrag,
    nicht_gefunden,
    release_objekt,
    releases,
    richten,
    speichern,
    zustand,
)

GEHEIM = "GANZ-GEHEIM-123"


def mock_eintrag_mit_token(token: str) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        title="gitlab.example.net",
        data={CONF_HOST: "gitlab.example.net", CONF_TOKEN: token},
        unique_id="gitlab.example.net",
    )


def token_problem(status: int = 401):
    from tests.attrappe import Aufzeichnung

    return Aufzeichnung(status=status, text='{"message": "unauthorized"}', kopfzeilen={})


def kennung_fuer(pid: str) -> str:
    return "gitlab_gitlab_example_net_" + pid


def laufzeit_von(hass: HomeAssistant):
    return hass.data[DOMAIN][hass.config_entries.async_entries(DOMAIN)[0].entry_id]


async def test_diagnose_ohne_token_im_klartext(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage
) -> None:
    speichern(
        hass_storage,
        [eintrag_daten()],
        stand={STORAGE_KEY: {"installiert": "1.1.0", "vorabversionen": False}},
    )
    sitzung_einpflanzen([herzschlag(), releases(release_objekt("v1.2.0", "Die Notizen"))])
    mock = mock_eintrag_mit_token(GEHEIM)
    await richten(hass, mock)

    bericht = await async_get_config_entry_diagnostics(hass, mock)

    # Die Abnahme: kein Token im Klartext, nirgends -- ueber das ganze
    # Wörterbuch suchen, nicht nur an der erwarteten Stelle.
    flach = json.dumps(bericht)
    assert GEHEIM not in flach
    assert bericht["einrichtung"]["token"] == "**REDACTED**"
    assert bericht["einrichtung"]["host"] == "gitlab.example.net"

    # Der Rest IST da: Ablage, Stand des Laufs, Fund je Eintrag.
    assert bericht["ablage"]["eintraege"][0]["full_name"] == "foo/bar"
    assert bericht["ablage"]["stand"][STORAGE_KEY]["installiert"] == "1.1.0"
    assert bericht["letzte_laeufe_erfolgreich"] is True
    fund = bericht["funde"][STORAGE_KEY]
    assert fund["neueste"] == "1.2.0"
    assert fund["fehler"] == ""


async def test_reparatur_fuers_verschwundene_repository(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage
) -> None:
    kaputt = eintrag_daten(full_name="kaputt/bar", pid="111")
    speichern(
        hass_storage,
        [eintrag_daten(), kaputt],
        stand={STORAGE_KEY: {"installiert": "1.1.0", "vorabversionen": False}},
    )
    sitzung_einpflanzen(
        [
            herzschlag(),
            releases(release_objekt("v1.2.0")),
            nicht_gefunden(),
            nicht_gefunden(),
        ]
    )
    await richten(hass, mock_eintrag())

    register = issue_registry.async_get(hass)
    verschwunden = register.async_get_issue(
        DOMAIN, "repo_verschwunden_" + kennung_fuer("111")
    )
    assert verschwunden is not None
    assert register.async_get_issue(DOMAIN, "repo_krank_" + kennung_fuer("111")) is None
    # Das gesunde Repo bekommt keine Meldung.
    assert (
        register.async_get_issue(DOMAIN, "repo_verschwunden_" + kennung_fuer("789012"))
        is None
    )
    assert register.async_get_issue(DOMAIN, "token_problem") is None


async def test_reparatur_raeumt_auf_wenn_es_wieder_geht(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage
) -> None:
    kaputt = eintrag_daten(full_name="kaputt/bar", pid="111")
    speichern(hass_storage, [eintrag_daten(), kaputt])
    attrappe = sitzung_einpflanzen(
        [
            herzschlag(),
            releases(release_objekt("v1.2.0")),
            nicht_gefunden(),
            nicht_gefunden(),
        ]
    )
    await richten(hass, mock_eintrag())

    register = issue_registry.async_get(hass)
    assert (
        register.async_get_issue(DOMAIN, "repo_verschwunden_" + kennung_fuer("111"))
        is not None
    )

    # Naechster Lauf: beide gesund -- die Meldung muss weg.
    attrappe.aufzeichnungen.extend(
        [releases(release_objekt("v1.2.1")), releases(release_objekt("v1.0.0"))]
    )
    laufzeit = laufzeit_von(hass)
    await laufzeit.aktualisierer.async_request_refresh()
    await hass.async_block_till_done()

    assert (
        register.async_get_issue(DOMAIN, "repo_verschwunden_" + kennung_fuer("111"))
        is None
    )


async def test_token_problem_wird_meldung_und_heilt(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage
) -> None:
    speichern(hass_storage, [])
    attrappe = sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())

    laufzeit = laufzeit_von(hass)
    identitaet = RepositoryIdentity(
        provider="gitlab",
        host="gitlab.example.net",
        provider_id="789012",
        full_name="foo/bar",
    )
    attrappe.aufzeichnungen.extend([token_problem(), token_problem()])
    await laufzeit.eintraege.hinzufuegen(identitaet, "integration")
    await hass.async_block_till_done()

    register = issue_registry.async_get(hass)
    assert register.async_get_issue(DOMAIN, "token_problem") is not None
    # Der Ausfall bleibt ohne Folgen fuer die Daten: Entity da, Fund leer.
    assert zustand(hass, "update").state == "unavailable"

    # Heilung: naechster Lauf gesund -> Meldung weg, Entity lebt. Der
    # Vorlauf um den Takt umgeht den Debounce der soeben gescheiterten
    # Runde (im M5-Test erprobt).
    attrappe.aufzeichnungen.extend([releases(release_objekt("v1.2.0", "Wieder da"))])
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=12))
    await hass.async_block_till_done()

    assert register.async_get_issue(DOMAIN, "token_problem") is None
    geheilt = zustand(hass, "update")
    assert geheilt.state == "unknown"  # noch nichts installiert
    assert geheilt.attributes["latest_version"] == "1.2.0"


async def test_instanz_weg_behaelt_alte_daten(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage
) -> None:
    """Der Roadmap-Satz: alte Daten behalten, Fehler melden, nicht loeschen."""
    speichern(
        hass_storage,
        [eintrag_daten()],
        stand={STORAGE_KEY: {"installiert": "1.1.0", "vorabversionen": False}},
    )
    attrappe = sitzung_einpflanzen([herzschlag(), releases(release_objekt("v1.2.0"))])
    await richten(hass, mock_eintrag())
    assert zustand(hass, "update").state == "on"

    laufzeit = laufzeit_von(hass)
    # Keine Aufzeichnung mehr: der Lauf scheitert komplett.
    await laufzeit.aktualisierer.async_request_refresh()
    await hass.async_block_till_done()

    assert laufzeit.aktualisierer.last_update_success is False
    assert zustand(hass, "update").state == "unavailable"
    # Die alten Funds bleiben im Koordinator UNVERAENDERT stehen -- der
    # Koordinator wirft die gescheiterte Runde weg, nicht die letzte gute.
    fund = laufzeit.aktualisierer.data[STORAGE_KEY]
    assert fund.neueste == "1.2.0"
    assert fund.fehler is None

    # Es geht wieder: alles kehrt zurueck, nichts ging verloren. Auch hier
    # der Takt-Vorlauf (Debounce), nicht die direkte Bitte.
    attrappe.aufzeichnungen.append(releases(release_objekt("v1.2.0")))
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=12))
    await hass.async_block_till_done()
    assert zustand(hass, "update").state == "on"


def test_migration_der_ablage_je_form() -> None:
    """Migrations-Faelle der Ablage: alt, Schrott, kaputt -- nichts geht verloren."""
    eintrag = {"provider": "gitlab", "full_name": "foo/bar"}

    # Alte Form (M3-Zeiten): kein stand-Feld -> wird ergaenzt.
    alt = migriere({"eintraege": [eintrag]})
    assert alt == {"eintraege": [eintrag], "stand": {}}

    # Stand als Muell -> geleert, Eintraege bleiben.
    muell = migriere({"eintraege": [eintrag], "stand": "quatsch"})
    assert muell == {"eintraege": [eintrag], "stand": {}}

    # Einzelne Stand-Werte ohne Kartenform fallen weg, gueltige bleiben.
    gemischt = migriere(
        {"eintraege": [], "stand": {"gut": {"installiert": "1.0"}, "schlecht": 7}}
    )
    assert gemischt == {
        "eintraege": [],
        "stand": {"gut": {"installiert": "1.0"}},
    }

    # Ganz kaputte Formen landen im Leerzustand.
    assert migriere(None) == {"eintraege": [], "stand": {}}
    assert migriere({"eintraege": "keine Liste"}) == {"eintraege": [], "stand": {}}
    assert migriere("gar nichts") == {"eintraege": [], "stand": {}}
