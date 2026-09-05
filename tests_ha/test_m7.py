"""Stufe M7 in Home Assistant: das Panel und seine Befehle.

Die Abnahme von Stufe M7 -- «Ein Durchgang ohne YAML: hinzufuegen,
installieren, aktualisieren, entfernen, alles ueber die Oberflaeche»
-- ist hier ein einziger Test, der genau diese Reihenfolge faehrt:
die Befehle des Panels (WebSocket) fuer Hinzufuegen und Entfernen,
der install-Dienst der update-Entities aus Stufe M5 fuer Installieren
und Aktualisieren. Keine Zeile YAML wird dabei beruehrt.

Das Panel selbst ist eine Datei fuer den Browser; was davon in
Python pruefbar ist, wird hier geprueft: die Anmeldung ohne
panel_custom-YAML und der statische Weg, der die Datei liefert.
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import timedelta
from pathlib import Path

import homeassistant.util.dt as dt_util
from homeassistant.components import frontend
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.hacs_lab.const import CONF_HOST, CONF_TOKEN, DOMAIN
from tests.attrappe import Aufzeichnung

from .test_m5 import (
    eintrag_daten,
    release_objekt,
    speichern,
    stammdaten,
)

HOST = "gitlab.example.net"
STORAGE_KEY = "gitlab@gitlab.example.net:789012"


def mock_eintrag() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        title=HOST,
        data={CONF_HOST: HOST, CONF_TOKEN: ""},
        unique_id=HOST,
    )


def herzschlag() -> Aufzeichnung:
    return Aufzeichnung(text="[]", kopfzeilen={})


def projekt_antwort(
    full_name: str = "foo/bar", pid: str = "789012", **rest
) -> Aufzeichnung:
    daten = {
        "id": pid,
        "path_with_namespace": full_name,
        "description": "ein Testprojekt",
        "default_branch": "main",
        "topics": ["hacs"],
        "star_count": 7,
        "open_issues_count": 2,
        "archived": False,
        "web_url": "https://" + HOST + "/" + full_name,
    }
    daten.update(rest)
    return Aufzeichnung(text=json.dumps(daten), kopfzeilen={})


def releases_objekt(tag: str, beschreibung: str = "") -> dict:
    return {
        "tag_name": tag,
        "name": "Version " + tag,
        "description": beschreibung,
        "released_at": "2026-09-01T10:00:00Z",
        "assets": {},
    }


def releases(*objekte: dict) -> Aufzeichnung:
    return Aufzeichnung(text=json.dumps(list(objekte)), kopfzeilen={})


def nicht_gefunden() -> Aufzeichnung:
    return Aufzeichnung(
        status=404, text='{"message": "404 Project Not Found"}', kopfzeilen={}
    )


def datei_antwort(inhalt: str | bytes) -> Aufzeichnung:
    if isinstance(inhalt, str):
        inhalt = inhalt.encode("utf-8")
    return Aufzeichnung(rohbytes=inhalt, kopfzeilen={})


def zip_aufzeichnung(version: str = "v1.2.0") -> Aufzeichnung:
    archiv = io.BytesIO()
    with zipfile.ZipFile(archiv, "w") as zip_datei:
        zip_datei.writestr(
            "foo-bar-" + version + "/manifest.json",
            json.dumps(
                {
                    "domain": "beispiel_integration",
                    "name": "Beispiel",
                    "version": version,
                    "documentation": "https://example.net",
                }
            ),
        )
        zip_datei.writestr("foo-bar-" + version + "/__init__.py", "# die Integration\n")
    return Aufzeichnung(rohbytes=archiv.getvalue(), kopfzeilen={})


async def richten(hass: HomeAssistant, mock: MockConfigEntry) -> None:
    # Wie im richtigen Haus: http und websocket_api stehen bereit, bevor
    # irgendeine Integration laeuft. Die Testumgebung richtet sie erst auf
    # Anfrage -- die Reihenfolge wird hier handgestellt, wie sie das
    # Hochfahren von Home Assistant ohnehin einhaelt.
    assert await async_setup_component(hass, "websocket_api", {})
    mock.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock.entry_id)
    await hass.async_block_till_done()


async def frage(client, kennung: int, typ: str, **felder) -> dict:
    """Eine WebSocket-Nachricht hin und die Antwort zurueck."""
    await client.send_json({"id": kennung, "type": typ, **felder})
    return await client.receive_json()


# ----------------------------------------------------------------------
# Panel-Anmeldung ohne YAML


async def test_panel_ist_ohne_yaml_angemeldet(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client, hass_client
) -> None:
    """Sidebar-Eintrag und Datei-Lieferung -- ohne eine Zeile YAML."""
    sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())

    karten = hass.data[frontend.DATA_PANELS]
    assert "hacs-lab" in karten
    karte = karten["hacs-lab"]
    assert karte.sidebar_title == "HACS*lab"
    assert karte.sidebar_icon == "hacs-lab:tanuki"
    assert karte.require_admin is True
    angepasst = karte.config["_panel_custom"]
    assert angepasst["name"] == "hacs-lab-panel"
    assert angepasst["module_url"] == "/hacs_lab/panel.js"

    client = await hass_client()
    antwort = await client.get("/hacs_lab/panel.js")
    assert antwort.status == 200
    koerper = await antwort.text()
    assert "customElements.define" in koerper
    assert "hacs-lab-panel" in koerper
    # Die Sprachen, die das Panel kennt, stehen in der Datei selbst.
    assert '"de"' in koerper or "de:" in koerper

    # Flug 2083: der Laden traegt GitLabs Tracht -- der Tanuki im Balken
    # (vier farbige Pfade), der Rueckhalt fuer die Seitenleiste, die
    # einklappbaren Abschnitte und das Erneuern beim Betreten.
    assert "#E24329" in koerper
    assert "#FC6D26" in koerper
    assert "customIconsets" in koerper
    assert "hacs_lab/erneuern" in koerper
    for schlussel in ("aktualisierbar", "installierbar", "neu", "downloadbar"):
        assert schlussel in koerper

    # Das Iconset wird neben der Panel-Datei eigenen Weg geliefert.
    antwort = await client.get("/hacs_lab/iconset.js")
    assert antwort.status == 200
    iconset = await antwort.text()
    assert "customIconsets" in iconset
    assert '"hacs-lab"' in iconset
    assert "#E24329" not in iconset  # die Silhouette traegt keine Farbe


async def test_iconset_haengt_an_jeder_seite(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client
) -> None:
    """Die Seitenleiste kennt den Tanuki, bevor jemand das Panel oeffnet.

    add_extra_js_url haengt das Iconset an das Grundgeruest des Frontends
    -- dieselbe Stelle, deren sich HACS fuer sein eigenes Zeichen bedient.
    Das Testhaus richtet das Frontend hier von Hand (wie das Hochfahren
    es ohnehin vor den Custom-Integrationen tut).
    """
    assert await async_setup_component(hass, "frontend", {})
    sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())

    urls = hass.data[frontend.DATA_EXTRA_MODULE_URL].urls
    assert "/hacs_lab/iconset.js" in urls


async def test_erneuern_auf_leerer_instanz(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    """Leere Liste: der Befehl legt den ersten Aktualisierer an, ruft aber nichts.

    Instanzen ohne Eintraege hatten nie eine update-Entity -- also auch
    keinen Aktualisierer. ``erneuern`` legt ihn idempotent an; der Lauf
    ueber eine leere Liste fragt keine Aufzeichnung.
    """
    hass_storage["hacs_lab." + HOST.replace(".", "_")] = {
        "version": 1,
        "data": {"eintraege": [], "stand": {}},
    }
    attrappe = sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/erneuern")
    assert antwort["success"]
    assert antwort["result"]["eintraege"] == []
    assert antwort["result"]["gescheitert"] == {}
    # Kein einziger Ruf ging ueber die Reihe hinaus -- der Lauf war leer.
    assert len(attrappe.abrufe) == 1  # der Herzschlag beim Richten


async def test_erneuern_liefert_den_frischen_fund(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    """Der Betritt frischt auf: neuer Release, ohne auf den Takt zu warten.

    Die Liste haengt sonst am Takt des Aktualisierers -- Minuten oder
    Stunden. ``erneuern`` dreht jeden herum: der Fund aus dem frischen
    Lauf ist sofort da, und die scheiternde Instanz steht in der Antwort.
    """
    speichern(
        hass_storage,
        [eintrag_daten()],
        stand={STORAGE_KEY: {"installiert": "1.1.0", "vorabversionen": False}},
    )
    attrappe = sitzung_einpflanzen(
        [
            herzschlag(),  # Herzschlag beim Richten
            stammdaten(),  # M8-2: Stammdaten zum ersten Lauf ueber die ID
            releases(release_objekt("v1.2.0")),  # erster Lauf: 1.2.0 ist oben
            stammdaten(),  # Liste zeigen (eintraege) -- noch der alte Fund
            stammdaten(),  # erneuern: Stammdaten ueber die ID
            releases(release_objekt("v1.3.0", "Frisch")),  # erneuern: neuer Release
            stammdaten(),  # erneuern: die Liste danach bauen
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    # Vorher: die Liste sagt 1.2.0 -- der Takt hat noch nicht geschlagen.
    antwort = await frage(client, 1, "hacs_lab/eintraege")
    assert antwort["result"]["eintraege"][0]["neueste"] == "1.2.0"

    # Der Betritt: frischer Lauf, neuer Fund sofort.
    antwort = await frage(client, 2, "hacs_lab/erneuern")
    assert antwort["success"]
    zeile = antwort["result"]["eintraege"][0]
    assert zeile["neueste"] == "1.3.0"
    assert zeile["installiert"] == "1.1.0"
    assert antwort["result"]["gescheitert"] == {}

    # Die update-Entity hat den frischen Fund auch schon uebernommen.
    ids = hass.states.async_entity_ids("update")
    frisch = hass.states.get(ids[0])
    assert frisch.attributes["latest_version"] == "1.3.0"
    assert frisch.state == "on"
    assert len(attrappe.abrufe) == 7  # alle Aufzeichnungen, keine mehr, keine weniger


async def test_erneuern_meldet_die_gescheiterte_instanz(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    """Scheitert der frische Lauf, kommt die Liste trotzdem -- mit Grund.

    Die Antwort reisst nicht um: der letzte erfolgreiche Fund bleibt
    stehen, die Instanz steht mit Klartext in ``gescheitert``.
    """
    speichern(
        hass_storage,
        [eintrag_daten()],
        stand={STORAGE_KEY: {"installiert": "1.1.0", "vorabversionen": False}},
    )
    sitzung_einpflanzen(
        [
            herzschlag(),  # Herzschlag beim Richten
            stammdaten(),  # M8-2: Stammdaten zum ersten Lauf ueber die ID
            releases(release_objekt("v1.2.0")),  # erster Lauf
            stammdaten(),  # erneuern: Stammdaten ueber die ID
            Aufzeichnung(  # erneuern: der Lauf scheitert an der Instanz
                status=500, text='{"message": "overloaded"}', kopfzeilen={}
            ),
            stammdaten(),  # erneuern: die Liste danach bauen
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/erneuern")
    assert antwort["success"]
    assert HOST in antwort["result"]["gescheitert"]
    assert "500" in antwort["result"]["gescheitert"][HOST]
    # Der letzte erfolgreiche Fund bleibt -- die Liste kam trotzdem.
    zeile = antwort["result"]["eintraege"][0]
    assert zeile["neueste"] == "1.2.0"


async def test_eintraege_nennt_instanzen_und_kategorien(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    """Leere Liste, aber Instanz und Kategorien sind brauchbar."""
    hass_storage["hacs_lab." + HOST.replace(".", "_")] = {
        "version": 1,
        "data": {"eintraege": [], "stand": {}},
    }
    sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/eintraege")
    assert antwort["success"]
    assert antwort["result"]["eintraege"] == []
    assert antwort["result"]["instanzen"] == [HOST]
    assert "integration" in antwort["result"]["kategorien"]
    assert "plugin" in antwort["result"]["kategorien"]


# ----------------------------------------------------------------------
# Die Abnahme: ein voller Durchgang ohne YAML


async def test_voller_durchgang_ohne_yaml(
    hass: HomeAssistant,
    sitzung_einpflanzen,
    hass_storage,
    hass_ws_client,
) -> None:
    """Hinzufuegen, installieren, aktualisieren, entfernen -- alles vom Panel.

    Genau die Reihenfolge der Abnahme aus dem Ticket: was die
    Oberflaeche kann, sind die Befehle hier plus die Dienste der
    update-Entities. Kein YAML, kein Neustart, kein Zutun dazwischen.
    """
    hass_storage["hacs_lab." + HOST.replace(".", "_")] = {
        "version": 1,
        "data": {"eintraege": [], "stand": {}},
    }
    attrappe = sitzung_einpflanzen(
        [
            herzschlag(),  # Herzschlag beim Richten
            projekt_antwort(),  # Hinzufuegen: Identitaet klaeren
            projekt_antwort(),  # M8-2: Stammdaten zum frischen Lauf ueber die ID
            releases(releases_objekt("v1.2.0")),  # frischer Fund zum frischen Eintrag
            projekt_antwort(),  # Liste frisch zeigen
            releases(releases_objekt("v1.2.0")),  # M4b: Installationsquelle zuerst
            zip_aufzeichnung("v1.2.0"),  # Installieren
            projekt_antwort(),  # M8-2: Stammdaten im Takt-Lauf ueber die ID
            releases(releases_objekt("v1.3.0", "Frisch")),  # neuer Release im Takt
            releases(releases_objekt("v1.3.0", "Frisch")),  # M4b: Installationsquelle
            zip_aufzeichnung("v1.3.0"),  # Aktualisieren
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    # -- Hinzufuegen ueber die Oberflaeche --------------------------
    antwort = await frage(
        client,
        1,
        "hacs_lab/hinzufuegen",
        host=HOST,
        pfad="foo/bar",
        kategorie="integration",
    )
    assert antwort["success"]
    eintrag = antwort["result"]["eintrag"]
    assert eintrag["name"] == "foo/bar*lab"
    assert eintrag["storage_key"] == STORAGE_KEY
    assert eintrag["entity_id"] is not None
    await hass.async_block_till_done()

    update_ids = hass.states.async_entity_ids("update")
    assert len(update_ids) == 1
    update_id = update_ids[0]

    # -- Die Liste zeigt den Eintrag mit allem ---------------------
    antwort = await frage(client, 2, "hacs_lab/eintraege")
    assert antwort["success"]
    zeile = antwort["result"]["eintraege"][0]
    assert zeile["name"] == "foo/bar*lab"
    assert zeile["entity_id"] == update_id
    assert zeile["installiert"] == ""
    assert zeile["neueste"] == "1.2.0"
    assert zeile["sterne"] == 7
    assert zeile["web_url"] == "https://gitlab.example.net/foo/bar"
    assert zeile["tickets_url"] == "https://gitlab.example.net/foo/bar/-/issues"
    assert zeile["releases_url"] == "https://gitlab.example.net/foo/bar/-/releases"

    # -- Installieren ueber den Dienst der update-Entity ------------
    await hass.services.async_call(
        "update", "install", {"entity_id": update_id}, blocking=True
    )
    await hass.async_block_till_done()

    zustand = hass.states.get(update_id)
    assert zustand.state == "off"
    assert zustand.attributes["installed_version"] == "1.2.0"
    ziel = Path(hass.config.config_dir) / "custom_components" / "beispiel_integration"
    assert (ziel / "manifest.json").exists()
    assert (ziel / "__init__.py").exists()

    # -- Aktualisieren: neuer Release, dann wieder Installieren ------
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=12))
    await hass.async_block_till_done()

    frisch = hass.states.get(update_id)
    assert frisch.attributes["latest_version"] == "1.3.0"
    assert frisch.state == "on"

    await hass.services.async_call(
        "update", "install", {"entity_id": update_id}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get(update_id).attributes["installed_version"] == "1.3.0"

    # -- Entfernen ueber die Oberflaeche ----------------------------
    antwort = await frage(client, 3, "hacs_lab/entfernen", storage_key=STORAGE_KEY)
    assert antwort["success"]
    assert antwort["result"]["entfernt"] == "foo/bar*lab"

    antwort = await frage(client, 4, "hacs_lab/eintraege")
    assert antwort["result"]["eintraege"] == []

    gespeichert = hass_storage["hacs_lab." + HOST.replace(".", "_")]["data"]
    assert gespeichert["eintraege"] == []
    # Alle Aufzeichnungen verbraucht: kein Ruf ging ueber die Reihe hinaus
    # (seit M8-2 fragt jeder Lauf zusaetzlich die Stammdaten ueber die ID).
    assert len(attrappe.abrufe) == 11  # M4b: zwei zusaetzliche Release-Fragen


# ----------------------------------------------------------------------
# Entdeckung: der Scan aus Stufe M6, vom Panel aus angestossen


async def test_entdecken_liefert_die_liste(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    """Gemischte Gruppe: Treffer mit allem, Fehlschuesse mit Gruenden."""
    hass_storage["hacs_lab." + HOST.replace(".", "_")] = {
        "version": 1,
        "data": {"eintraege": [], "stand": {}},
    }
    mit_topic = {
        "id": 789012,
        "path_with_namespace": "foo/bar",
        "description": "das gute",
        "default_branch": "main",
        "topics": ["hacs"],
        "star_count": 7,
        "open_issues_count": 2,
        "archived": False,
        "web_url": "https://gitlab.example.net/foo/bar",
    }
    ohne_json = {
        "id": 111,
        "path_with_namespace": "foo/ohne",
        "description": "hat kein Thema-Tag im Sinne der Pruefung",
        "default_branch": "main",
        "topics": ["hacs"],
        "star_count": 1,
        "open_issues_count": 0,
        "archived": False,
        "web_url": "https://gitlab.example.net/foo/ohne",
    }
    suche = [mit_topic, ohne_json]
    sitzung_einpflanzen(
        [
            herzschlag(),  # Richten
            Aufzeichnung(text=json.dumps(suche), kopfzeilen={}),  # der Scan
            datei_antwort(json.dumps({"name": "Bar", "render_readme": True})),
            releases(releases_objekt("v2.0.0")),  # letzte Version des Treffers
            nicht_gefunden(),  # foo/ohne hat keine hacs.json
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/entdecken", host=HOST, gruppe="foo")
    assert antwort["success"]
    funde = antwort["result"]["funde"]
    assert [f["full_name"] for f in funde] == ["foo/bar", "foo/ohne"]

    bar = funde[0]
    assert bar["name"] == "foo/bar*lab"
    assert bar["letzte_version"] == "2.0.0"
    assert bar["gueltig"] is True
    assert bar["vorhanden"] is False
    assert bar["kategorie"] == "integration"
    assert bar["tickets_url"] == "https://gitlab.example.net/foo/bar/-/issues"

    ohne = funde[1]
    assert ohne["gueltig"] is False
    assert "hacs.json" in ohne["fehler"]

    # Nach der Aufnahme dreht die Flagge -- der Scan bleibt bei der Wahrheit.
    await frage(
        client,
        2,
        "hacs_lab/hinzufuegen",
        host=HOST,
        pfad="foo/bar",
        kategorie="integration",
    )
    await hass.async_block_till_done()
    sitzung_einpflanzen([])  # leer: kein weiterer Abruf erwuenscht
    # (entdecken hier nicht erneut gerufen: Aufzeichnungen sind auf.)


async def test_entdecken_ohne_instanz_meldet_klar(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client
) -> None:
    sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/entdecken", host="gitlab.woanders")
    assert not antwort["success"]
    assert antwort["error"]["code"] == "unbekannte_instanz"


# ----------------------------------------------------------------------
# Detailansicht: README, Releases, Verweise


async def test_detail_liefert_readme_releases_und_verweise(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client
) -> None:
    readme = "# Bar\n\nEin Projekt mit [Link](https://example.net) und **Fett**.\n"
    sitzung_einpflanzen(
        [
            herzschlag(),
            projekt_antwort(),  # Stammdaten
            releases(
                releases_objekt("v1.2.0", "die Notizen"),
                releases_objekt("v1.1.0"),
            ),
            datei_antwort(readme),  # README.md am Standardzweig
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/detail", host=HOST, pfad="foo/bar")
    assert antwort["success"]
    ergebnis = antwort["result"]

    assert ergebnis["info"]["name"] == "foo/bar*lab"
    assert ergebnis["info"]["sterne"] == 7
    assert ergebnis["readme"] == readme
    assert ergebnis["readme_datei"] == "README.md"
    assert [r["tag"] for r in ergebnis["releases"]] == ["v1.2.0", "v1.1.0"]
    assert ergebnis["releases"][0]["beschreibung"] == "die Notizen"
    assert ergebnis["info"]["releases_url"] == (
        "https://gitlab.example.net/foo/bar/-/releases"
    )


async def test_detail_ohne_readme_gnadenvoll(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client
) -> None:
    """Keine lesbare Beschreibung -- der Rest des Details bleibt trotzdem."""
    sitzung_einpflanzen(
        [
            herzschlag(),
            projekt_antwort(),
            releases(releases_objekt("v1.2.0")),
            nicht_gefunden(),  # README.md
            nicht_gefunden(),  # readme.md
            nicht_gefunden(),  # Readme.md
            nicht_gefunden(),  # README.rst
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/detail", host=HOST, pfad="foo/bar")
    assert antwort["success"]
    assert antwort["result"]["readme"] is None
    assert antwort["result"]["readme_datei"] == ""
    assert len(antwort["result"]["releases"]) == 1


# ----------------------------------------------------------------------
# Fehler der Befehle: benannt, nicht als Stacktrace


async def test_hinzufuegen_lehnt_fehler_ab(
    hass: HomeAssistant, sitzung_einpflanzen, hass_storage, hass_ws_client
) -> None:
    hass_storage["hacs_lab." + HOST.replace(".", "_")] = {
        "version": 1,
        "data": {"eintraege": [], "stand": {}},
    }
    sitzung_einpflanzen(
        [
            herzschlag(),
            nicht_gefunden(),  # erster Versuch: gibt es nicht
            projekt_antwort(),  # zweiter Versuch: Kategorie untauglich
            projekt_antwort(),  # dritter Versuch: klappt ...
            projekt_antwort(),  # M8-2: Stammdaten zum frischen Lauf ueber die ID
            releases(
                releases_objekt("v1.0.0")
            ),  # ... und der Beobachter schaut gleich nach
            projekt_antwort(),  # vierter Versuch: schon in der Liste
        ]
    )
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(
        client,
        1,
        "hacs_lab/hinzufuegen",
        host=HOST,
        pfad="gibt/es/nicht",
        kategorie="integration",
    )
    assert not antwort["success"]
    assert antwort["error"]["code"] == "nicht_gefunden"

    antwort = await frage(
        client, 2, "hacs_lab/hinzufuegen", host=HOST, pfad="foo/bar", kategorie="quatsch"
    )
    assert not antwort["success"]
    assert antwort["error"]["code"] == "kategorie_unbekannt"

    antwort = await frage(
        client,
        3,
        "hacs_lab/hinzufuegen",
        host=HOST,
        pfad="foo/bar",
        kategorie="integration",
    )
    assert antwort["success"]

    antwort = await frage(
        client,
        4,
        "hacs_lab/hinzufuegen",
        host=HOST,
        pfad="foo/bar",
        kategorie="integration",
    )
    assert not antwort["success"]
    assert antwort["error"]["code"] == "bereits_vorhanden"


async def test_entfernen_wenn_weg(
    hass: HomeAssistant, sitzung_einpflanzen, hass_ws_client
) -> None:
    sitzung_einpflanzen([herzschlag()])
    await richten(hass, mock_eintrag())
    client = await hass_ws_client(hass)

    antwort = await frage(client, 1, "hacs_lab/entfernen", storage_key="gitlab@x:1")
    assert not antwort["success"]
    assert antwort["error"]["code"] == "nicht_mehr_da"
