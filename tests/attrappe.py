"""Eine HTTP-Attrappe: liefert vorbereitete Antworten, geht nie ins Netz."""

from __future__ import annotations

import json

from hacs_lab.core.forge import NichtGefunden


class FakeHttp:
    """Antworten werden ueber ein Praefix der URL zugeordnet."""

    def __init__(self, json_antworten: dict | None = None, dateien: dict | None = None):
        self.json_antworten = json_antworten or {}
        self.dateien = dateien or {}
        self.aufrufe: list[tuple[str, dict]] = []

    async def get_json(self, url: str, params: dict | None = None):
        self.aufrufe.append((url, params or {}))
        for schluessel, wert in self.json_antworten.items():
            if schluessel in url:
                return wert
        return {"message": "404 Project Not Found"}

    async def get_bytes(self, url: str) -> bytes:
        self.aufrufe.append((url, {}))
        for schluessel, wert in self.dateien.items():
            if schluessel in url:
                if isinstance(wert, bytes):
                    return wert
                if isinstance(wert, str):
                    return wert.encode("utf-8")
                return json.dumps(wert).encode("utf-8")
        # Wie ein echter Anbieter bei 404: der Aufrufer soll nur eine
        # Fehlerart kennen muessen.
        raise NichtGefunden(url)


def projekt(
    pid: int = 789012,
    full_name: str = "foo/bar",
    topics: tuple[str, ...] = ("hacs",),
    **rest,
) -> dict:
    daten = {
        "id": pid,
        "path_with_namespace": full_name,
        "description": "ein Testprojekt",
        "default_branch": "main",
        "topics": list(topics),
        "star_count": 7,
        "open_issues_count": 2,
        "archived": False,
        "web_url": "https://gitlab.example.net/" + full_name,
    }
    daten.update(rest)
    return daten
