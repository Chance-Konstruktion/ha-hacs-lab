"""Der Stand eines Eintrags: installierte Version, Vorab-Entscheid.

Stufe M5 braucht je Eintrag zwei Dinge, die ueberleben muessen: welche
Version als installiert gilt, und ob Vorabversionen mitgezaehlt werden
duerfen (der Schalter in der Oberflaeche). Beides liegt in der Ablage
unter dem Feld ``stand`` -- bewusst getrennt von der Eintrags-Liste,
weil es sich unabhaessig von ihr aendert und hauefiger.

Die Form je Eintrag: ``{"installiert": "1.2.0", "vorabversionen": false}``.
Fehlende Felder heissen Leere bzw. Nein -- gleiches tolerante Lesen wie
ueberall in der Ablage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ablage import Ablage

#: Feldname in der Ablage.
FELD = "stand"


class Stand:
    """Unveraenderlicher Zustand eines Eintrags."""

    def __init__(self, installiert: str = "", vorabversionen: bool = False) -> None:
        self.installiert = installiert
        self.vorabversionen = vorabversionen

    def as_dict(self) -> dict[str, str | bool]:
        return {"installiert": self.installiert, "vorabversionen": self.vorabversionen}

    def __eq__(self, andere: object) -> bool:
        if not isinstance(andere, Stand):
            return NotImplemented
        return (
            self.installiert == andere.installiert
            and self.vorabversionen == andere.vorabversionen
        )

    def __repr__(self) -> str:
        return (
            f"Stand(installiert={self.installiert!r},"
            f" vorabversionen={self.vorabversionen!r})"
        )


#: Der leere Stand -- nichts installiert, keine Vorabversionen.
LEER = Stand()


def _aus_dict(roh: object) -> Stand:
    if not isinstance(roh, dict):
        return Stand()
    return Stand(
        installiert=str(roh.get("installiert") or ""),
        vorabversionen=bool(roh.get("vorabversionen")),
    )


class Staende:
    """Alle Staelle auf einen Blick, persistiert in der Ablage."""

    def __init__(self, ablage: Ablage) -> None:
        self._ablage = ablage
        self._karte: dict[str, Stand] = {}

    async def laden(self) -> None:
        """Liest die Karte aus der Ablage; mehrfach aufrufbar, ergaenzt nur.

        ``aus_ablage`` gibt es bewusst nicht: die Staelle entstehen
        lazily beim ersten Anlegen der M5-Waben, nicht beim Richten des
        Eintrags -- wer sie zuerst braucht, laedt sie einmal.
        """
        daten = await self._ablage.laden()
        roh = daten.get(FELD)
        if isinstance(roh, dict):
            for schluessel, wert in roh.items():
                if isinstance(schluessel, str):
                    self._karte.setdefault(schluessel, _aus_dict(wert))

    def stand(self, schluessel: str) -> Stand:
        """Der Stand eines Eintrags -- unbekannt heisst leer."""
        return self._karte.get(schluessel) or Stand()

    async def setzen(
        self,
        schluessel: str,
        installiert: str | None = None,
        vorabversionen: bool | None = None,
    ) -> Stand:
        """Aendert Felder eines Standes und sichert sofort.

        Nur die genannten Felder aendern sich; ``None`` laesst ein Feld,
        wie es ist. Der neue Stand kommt zurueck.
        """
        alt = self.stand(schluessel)
        neu = Stand(
            installiert=alt.installiert if installiert is None else installiert,
            vorabversionen=(
                alt.vorabversionen if vorabversionen is None else vorabversionen
            ),
        )
        self._karte[schluessel] = neu
        await self._ablage.sicher_teil(
            FELD, {schluss: wert.as_dict() for schluss, wert in self._karte.items()}
        )
        return neu
