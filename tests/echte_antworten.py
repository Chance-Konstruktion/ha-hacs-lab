"""Aufgezeichnete Antworten einer echten GitLab-Instanz: gitlab.com.

Quelle (2026-09-03, curl, ohne Token -- die Abfrage ist oeffentlich)::

    GET https://gitlab.com/api/v4/projects?topic=hacs&per_page=3&archived=false
    GET https://gitlab.com/api/v4/projects?topic=hacs&per_page=3&archived=false&page=2

Vier Treffer auf zwei Seiten. Die Koerper in ``aufzeichnungen/`` sind
unveraendert, bytegenau wie die Instanz sie geschickt hat -- ebenso die
Kopfzeilen unten. Damit faellt auch auf, was echte Projekt-Datensaetze
an Feldern mitbringen (20 Stueck, inklusive verschachteltem
``namespace``), was handgebaute Attrappen nie zeigen. Die abgefragten
Projekte stehen in der oeffentlichen Projektleiste der Instanz.

Ausserdem aufgezeichnet: der vierte Abruf derselben ersten Seite mit
``If-None-Match`` auf ihren ETag ergab HTTP 304. Die zweite Seite ist
die letzte (``X-Next-Page`` ohne Wert) und traegt ihren eigenen ETag --
der Fall, den der Zwischenspeicher uebernehmen darf.
"""

from __future__ import annotations

import json
from pathlib import Path

_ORDNER = Path(__file__).parent / "aufzeichnungen"


def _lade(name: str):
    with open(_ORDNER / name, encoding="utf-8") as datei:
        return json.load(datei)


#: Kopfzeilen der ersten Seite, wie geliefert (ETag inklusive).
KOPFZEILEN_SEITE_1 = {
    "etag": 'W/"053215982b68de4713459d865d7f9cb6"',
    "x-page": "1",
    "x-next-page": "2",
    "x-total": "4",
    "x-total-pages": "2",
}

#: Koerper der ersten Seite: drei Projekte, unveraendert.
SEITE_1 = _lade("projekte-topic-hacs-seite-1.json")

#: Kopfzeilen der zweiten Seite: die letzte Seite, leere Folge-Seite,
#: eigener ETag.
KOPFZEILEN_SEITE_2 = {
    "etag": 'W/"ed7208eb3e0151f5427817e9a93392cd"',
    "x-page": "2",
    "x-next-page": "",
    "x-total": "4",
    "x-total-pages": "2",
}

#: Koerper der zweiten Seite: das vierte Projekt.
SEITE_2 = _lade("projekte-topic-hacs-seite-2.json")
