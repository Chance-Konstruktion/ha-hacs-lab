"""Ablage eines Eintrags: Home-Assistant-Speicher, Version 1.

Warum ein duenner Mantel: die Roadmap verlangt fuer die Ablage von
Anfang an eine Migrationsfunktion. Formate aendern sich spaeter gern,
Datenverluste sollen dabei nicht entstehen -- also liegt die Form der
Daten in genau einer Datei, und jede Aenderung daran bekommt hier ihren
eigenen Zweig in :func:`migriere`.

Version 1 kennt genau ein Feld: ``eintraege`` (eine Liste). Gefuellt
wird sie erst in Stufe M3 -- das Geruest steht heute, damit die
Eintraege morgen keinen neuen Speicher brauchen.
"""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.storage import Store

#: Die leere Form von Version 1.
LEERE_DATEN: dict[str, Any] = {"eintraege": []}


def migriere(roh: dict[str, Any] | None) -> dict[str, Any]:
    """Bringt eine gespeicherte Form auf den Stand von Version 1.

    Reine Funktion ohne Store: alle Faelle -- nichts gespeichert, alte
    Form, kaputte Form -- landen in der Form von Version 1. Spaeteres
    Format bekommt hier einen eigenen Zweig, *bevor* die Versionszahl
    steigt.
    """
    if not isinstance(roh, dict):
        return {"eintraege": []}
    eintraege = roh.get("eintraege")
    if not isinstance(eintraege, list):
        return {"eintraege": []}
    return {"eintraege": eintraege}


class Ablage:
    """Duenner Mantel um :class:`homeassistant.helpers.storage.Store`."""

    def __init__(self, store: Store) -> None:
        self._store = store

    async def laden(self) -> dict[str, Any]:
        """Laedt und wandelt auf Version 1; nur bei Aenderung wird gespeichert."""
        roh = await self._store.async_load()
        daten = migriere(roh)
        if daten != roh:
            await self.sichern(daten)
        return daten

    async def sichern(self, daten: dict[str, Any]) -> None:
        await self._store.async_save(daten)
