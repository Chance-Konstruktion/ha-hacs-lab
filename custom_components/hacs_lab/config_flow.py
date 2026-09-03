"""Einrichtungsdialog: Host, optionaler Token, Pruefverbindung.

Die Pruefung geht durch den echten Weg -- Klient, Forge, Kern -- und
nicht durch eine Sonderleitung: schlaegt sie fehl, zeigt der Dialog
genau das, was der Kern zu sagen hat (401/403 → «Token fehlt oder
reicht nicht», alles andere → Klartext). Ein Stacktrace erreicht den
Menschen nie.

Dafuer eignet sich die Topic-Suche am besten: sie ist dasselbe Mittel,
mit dem spaeter die Entdeckung laeuft (M6), und sie klappt ohne Token
auf oeffentlichen Instanzen genauso wie mit Token auf eigenen.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from hacs_lab.core.forge import ForgeFehler
from hacs_lab.core.gitlab_forge import GitLabForge
from hacs_lab.http_aiohttp import AiohttpClient

from .const import (
    CONF_ABSTAND_MINUTEN,
    CONF_HOST,
    CONF_TOKEN,
    DOMAIN,
    STANDARD_ABSTAND_MINUTEN,
    host_normalisieren,
)


async def verbindung_pruefen(
    hass: HomeAssistant, host: str, token: str | None
) -> list[Any]:
    """Ein echter Abruf ueber die Instanz -- beweist Host, API und Token.

    Gelingt er, kommt die Antwort zurueck (der Dialog meldet ihre
    Groesse). Gelingt er nicht, wirft der Kern seine Fehlerarten -- und
    genau die werden im Dialog uebersetzt.
    """
    sitzung = async_get_clientsession(hass)
    klient = AiohttpClient(sitzung, token)
    forge = GitLabForge(klient, host)
    return await forge.suche_nach_topic()


class HacsLabFluss(config_entries.ConfigFlow, domain=DOMAIN):
    """Einrichten einer GitLab-Instanz."""

    VERSION = 1

    async def async_step_user(
        self, benutzereingabe: dict[str, Any] | None = None
    ) -> FlowResult:
        fehler: dict[str, str] = {}
        platzhalter: dict[str, str] = {}

        if benutzereingabe is not None:
            host = host_normalisieren(benutzereingabe[CONF_HOST])
            token = (benutzereingabe.get(CONF_TOKEN) or "").strip() or None
            try:
                funde = await verbindung_pruefen(self.hass, host, token)
            except ForgeFehler as fehlgeschlag:
                fehler["base"] = (
                    "token_reicht_nicht"
                    if "Token fehlt oder reicht nicht" in str(fehlgeschlag)
                    else "verbindung_fehlgeschlagen"
                )
                platzhalter["grund"] = str(fehlgeschlag)
            except Exception as fehlgeschlag:
                # Breit mit Absicht: ob der DNS-, TLS- oder Timeout-Fall
                # eintritt, ist fuer den Menschen einer -- die Instanz
                # ist nicht erreichbar, und mehr steht nicht im Dialog.
                fehler["base"] = "host_nicht_erreichbar"
                platzhalter["grund"] = f"{type(fehlgeschlag).__name__}"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=host,
                    data={CONF_HOST: host, CONF_TOKEN: token or ""},
                    description="verbunden",
                    description_placeholders={
                        "host": host,
                        "anzahl": str(len(funde)),
                    },
                )

            if not host:
                fehler["base"] = "host_leer"

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=(benutzereingabe or {}).get(CONF_HOST, "gitlab.com"),
                ): str,
                vol.Optional(CONF_TOKEN, description={"hint": "token_hint"}): str,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=fehler,
            description_placeholders=platzhalter,
        )

    @staticmethod
    def async_get_options_flow(
        eintrag: config_entries.ConfigEntry,
    ) -> HacsLabOptionen:
        return HacsLabOptionen()


class HacsLabOptionen(config_entries.OptionsFlow):
    """Abstand des Herzschlags, ohne Neustart einstellbar."""

    async def async_step_init(
        self, benutzereingabe: dict[str, Any] | None = None
    ) -> FlowResult:
        if benutzereingabe is not None:
            return self.async_create_entry(
                title="",
                data={CONF_ABSTAND_MINUTEN: int(benutzereingabe[CONF_ABSTAND_MINUTEN])},
            )

        aktuell = self.config_entry.options.get(
            CONF_ABSTAND_MINUTEN, STANDARD_ABSTAND_MINUTEN
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ABSTAND_MINUTEN, default=aktuell): vol.All(
                        int, vol.Range(min=1)
                    )
                }
            ),
        )
