"""Der Neustart-Hinweis fuer Integrationen (Stufe M4b).

Home Assistant laedt ``custom_components`` beim Start -- Dateien, die
danach erscheinen oder verschwinden, aendern am laufenden nichts.
Darum landet nach jeder Installation oder Deinstallation einer
Integration ein Hinweis auf dem Reparatur-Brett; er verschwindet, sobald
der Neustart passiert ist (das Laden der Komponente raeumt jeden
Neustart-Hinweis ab, siehe ``__init__.py``).

Andere Kategorien (Themes, Plugins, Skripte) brauchen keinen Neustart
-- dort bleibt das Brett still. Das ist Physik, nicht Nachlaessigkeit.

Ein eigenes Modul, weil zwei Stellen ihn rufen (update-Entities und der
WebSocket-Befehl zum Deinstallieren) und die HA-Schicht des Pakets
selbst ihn beim Aufraeumen nicht importieren darf -- ein Import aus
``__init__`` waere ein Kreis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import issue_registry
from homeassistant.helpers.issue_registry import IssueSeverity

from .aktualisierer import _kennung
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .eintraege import Eintrag


def neustart_hinweis(
    hass: HomeAssistant, eintrag: Eintrag, version: str, aktion: str
) -> None:
    """Stellt den Hinweis fuer eine Integration aufs Reparatur-Brett.

    ``aktion`` ist fuer Menschen ``"installation"`` oder
    ``"deinstallation"`` -- die Uebersetzung baelt daraus den Satz.
    """
    if eintrag.kategorie != "integration":
        return
    issue_registry.async_create_issue(
        hass,
        DOMAIN,
        "neustart_" + _kennung(eintrag.storage_key),
        is_fixable=False,
        severity=IssueSeverity.WARNING,
        translation_key="neustart_nach_installation",
        translation_placeholders={
            "name": eintrag.anzeigename,
            "version": version,
            "aktion": aktion,
        },
    )
