"""Der Einrichtungsdialog auf der Attrappe -- der echte Weg, ohne Netz."""

from __future__ import annotations

import json

from homeassistant.config_entries import SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.hacs_lab.const import CONF_HOST, CONF_TOKEN, DOMAIN
from tests.attrappe import Aufzeichnung, projekt


def antwort(anzahl: int = 1) -> Aufzeichnung:
    """Eine Topic-Suche, die ``anzahl`` Projekte meldet."""
    return Aufzeichnung(
        text=json.dumps([projekt() for _ in range(anzahl)]), kopfzeilen={}
    )


async def test_dialog_erscheint(hass: HomeAssistant) -> None:
    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert ergebnis["type"] is FlowResultType.FORM
    assert ergebnis["step_id"] == "user"
    assert ergebnis["errors"] == {}


async def test_verbindung_gelingt(hass: HomeAssistant, sitzung_einpflanzen) -> None:
    # Zwei Antworten: eine fuer die Pruefung im Dialog, eine fuer den
    # ersten Herzschlag -- Home Assistant richtet den Eintrag nach dem
    # Dialog sofort ein.
    attrappe = sitzung_einpflanzen([antwort(), antwort()])

    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.CREATE_ENTRY
    assert ergebnis["title"] == "gitlab.example.net"
    assert ergebnis["data"] == {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""}
    assert len(attrappe.abrufe) == 2
    assert attrappe.abrufe[0][0].startswith("https://gitlab.example.net/api/v4/projects")
    # Ohne Token reist keine Berechtigungskopfzeile.
    assert "Authorization" not in (attrappe.abrufe[0][2] or {})
    # Der Eintrag steht: Dialog und erster Herzschlag sind beide durch.
    eintraege = hass.config_entries.async_entries(DOMAIN)
    assert len(eintraege) == 1
    assert eintraege[0].state is ConfigEntryState.LOADED


async def test_token_reist_als_kopfzeile(
    hass: HomeAssistant, sitzung_einpflanzen
) -> None:
    attrappe = sitzung_einpflanzen([antwort(0)])

    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: "geheimes-ding"},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.CREATE_ENTRY
    assert attrappe.abrufe[0][2]["Authorization"] == "Bearer geheimes-ding"


async def test_eingefuegter_link_wird_zum_host(
    hass: HomeAssistant, sitzung_einpflanzen
) -> None:
    sitzung_einpflanzen([antwort()])

    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "https://GitLab.Example.Net/gruppe/projekt", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.CREATE_ENTRY
    assert ergebnis["data"][CONF_HOST] == "gitlab.example.net"


async def test_token_fehlt_gibt_verstaendliche_meldung(
    hass: HomeAssistant, sitzung_einpflanzen
) -> None:
    sitzung_einpflanzen(
        [
            Aufzeichnung(
                status=401,
                text=json.dumps({"message": "401 Unauthorized"}),
                kopfzeilen={},
            )
        ]
    )

    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.FORM
    assert ergebnis["errors"] == {"base": "token_reicht_nicht"}


async def test_anderer_fehler_gibt_verstaendliche_meldung(
    hass: HomeAssistant, sitzung_einpflanzen
) -> None:
    sitzung_einpflanzen([Aufzeichnung(status=500, text="kaputt", kopfzeilen={})])

    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.FORM
    assert ergebnis["errors"] == {"base": "verbindung_fehlgeschlagen"}


async def test_toter_host_gibt_verstaendliche_meldung(
    hass: HomeAssistant, tote_sitzung
) -> None:
    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.FORM
    assert ergebnis["errors"] == {"base": "host_nicht_erreichbar"}


async def test_derselbe_host_nur_einmal(hass: HomeAssistant, sitzung_einpflanzen) -> None:
    sitzung_einpflanzen([antwort()])
    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()
    assert ergebnis["type"] is FlowResultType.CREATE_ENTRY

    sitzung_einpflanzen([antwort()])
    ergebnis = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    ergebnis = await hass.config_entries.flow.async_configure(
        ergebnis["flow_id"],
        {CONF_HOST: "gitlab.example.net", CONF_TOKEN: ""},
    )
    await hass.async_block_till_done()

    assert ergebnis["type"] is FlowResultType.ABORT
    assert ergebnis["reason"] == "already_configured"
