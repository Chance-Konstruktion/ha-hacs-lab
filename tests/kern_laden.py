"""Meldet den Kern zum Import an -- ohne die HA-Schicht auszufuehren.

Seit der Form-Entscheidung zu #11 wohnt der Kern in der Integration
(``custom_components/hacs_lab/core``). Die reine Kern-Suite
(``tests/``) importiert ihn weiterhin unter ``hacs_lab`` -- aber ohne
das Paket ``custom_components.hacs_lab`` anzufassen: dessen
``__init__.py`` ist die Home-Assistant-Schicht und bliebe ohne Home
Assistant schon im ersten Import stecken.

Darum wird das Integrationsverzeichnis hier als Paket ``hacs_lab``
ANGEMELDET -- registriert in ``sys.modules``, nicht auf den Suchpfad
gestellt. Das ist der entscheidende Unterschied zum alten Fallback:
kein Verzeichnis rutsckt vor die Standardbibliothek, nichts kann
beschattet werden, und der Name ``hacs_lab`` gehoert allein uns.

In der Home-Assistant-Bahn (``tests_ha/``) passiert nichts von alledem:
dort laeuft der Kern unter seinem echten Namen
``custom_components.hacs_lab.core`` -- geladen von Home Assistant
selbst. Beide Bahnen teilen sich deshalb keine Kern-Objekte, und genau
darauf achtet die Aufteilung der Attrappen: ``tests/attrappe.py`` ist
kernfrei (beide Bahnen), ``tests/attrappe_kern.py`` (FakeHttp) gehoert
allein der reinen Bahn.

Aufrufer: ``tests/conftest.py`` (jeder Kern-Testlauf) und der
CI-Waechter ``kern-ohne-homeassistant`` -- beide beweisen so, dass der
Kern ohne Home Assistant importierbar bleibt.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

#: Das Zuhause des Kerns seit der Form-Entscheidung (Issue #11).
INTEGRATION = Path(__file__).resolve().parents[1] / "custom_components" / "hacs_lab"

if "hacs_lab" not in sys.modules:
    _kern = types.ModuleType("hacs_lab")
    _kern.__path__ = [str(INTEGRATION)]
    sys.modules["hacs_lab"] = _kern
