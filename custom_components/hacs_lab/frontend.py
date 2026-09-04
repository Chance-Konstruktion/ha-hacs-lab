"""Das Panel von HACS*lab -- Stufe M7: Bedienung ohne YAML.

Zwei Schritte, beide ohne Eintrag in ``configuration.yaml``:

* die JavaScript-Datei wird ueber einen statischen Weg ausgeliefert
  (``/hacs_lab/panel.js``)
* das Panel selbst meldet sich ueber die oeffentliche Hilfe von
  ``panel_custom`` an -- dieselbe Stelle, die sonst die YAML-Sektion
  ``panel_custom:`` bedient, nur eben aus der Integration heraus

Sichtbar wird der Eintrag, sobald die erste Instanz eingerichtet ist
(eine Integration laedt nur mit Konfigurationseintrag). Die Web-
Oberflaeche laedt die Datei als ES-Modul und findet darin das
Element ``hacs-lab-panel``; der Rest des Bedienens laeuft ueber die
WebSocket-Befehle aus :mod:`.websocket_api` und die ganz normalen
Home-Assistant-Dienste.
"""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

#: Der Weg, unter dem der Browser die Panel-Datei bekommt.
PANEL_URL = "/hacs_lab/panel.js"

#: Der Name des Web-Components -- muss zur Definition in panel.js passen.
PANEL_ELEMENT = "hacs-lab-panel"

#: Die Adresse im Frontend (Sidebar): ``/hacs-lab``.
PANEL_PFAD = "hacs-lab"

#: Wie das Panel in der Sidebar heisst -- ein Name, kein uebersetzbarer Satz.
PANEL_TITEL = "HACS*lab"

#: Waben-Piktogramm -- der Bienen-Welt des Stocks geschuldet.
PANEL_ICON = "mdi:hexagon-multiple"


async def richten(hass: HomeAssistant) -> None:
    """Statischen Weg anlegen und das Panel in die Sidebar setzen.

    Wird aus ``async_setup`` gerufen, also genau einmal pro Laden der
    Komponente -- das Panel ueberlebt das Entfernen einzelner
    Instanz-Eintraege (die Liste kann dann leer sein, das Panel
    bleibt ehrlich und zeigt das).
    """
    datei = Path(__file__).parent / "frontend" / "panel.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_URL, str(datei), cache_headers=False)]
    )
    await async_register_panel(
        hass,
        frontend_url_path=PANEL_PFAD,
        webcomponent_name=PANEL_ELEMENT,
        module_url=PANEL_URL,
        sidebar_title=PANEL_TITEL,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
    )
    _LOGGER.info("Oberflaeche angemeldet: /%s laedt %s", PANEL_PFAD, PANEL_URL)
