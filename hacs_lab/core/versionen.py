"""Versionsvergleich und Update-Erkennung.

Absichtlich ohne ``packaging``: die Erweiterung soll in Home Assistant
ohne zusaetzliche Abhaengigkeit laufen. Verglichen wird nach Zahlen,
alles Uebrige bleibt Text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .forge import Release

#: Der Zahlenkopf einer Version: 1, 1.2, 1.2.3 ...
_KOPF = re.compile(r"^\d+(?:\.\d+)*")


def normalisiere(version: str) -> str:
    """Nimmt fuehrende ``v`` und Leerzeichen weg."""
    v = (version or "").strip()
    if v[:1] in ("v", "V") and v[1:2].isdigit():
        v = v[1:]
    return v


def ist_vorabversion(version: str) -> bool:
    """Erkennt ``1.2.0-rc1``, ``2.0b3`` und Verwandte.

    Geprueft wird nur, was hinter dem Zahlenkopf steht -- ``1.0.0+build``
    ist damit keine Vorabversion, ``1.0.0-beta`` schon.
    """
    rest = _KOPF.sub("", normalisiere(version).lower()).lstrip("-._+")
    if not rest:
        return False
    if re.match(r"^(alpha|beta|rc|dev|pre)", rest):
        return True
    return bool(re.match(r"^[ab]\d*$", rest))


def _schluessel(version: str) -> tuple:
    """Sortierschluessel: Zahlenkopf zuerst, Vorabversion danach kleiner.

    Die Zahlen kommen ausschliesslich aus dem Kopf. Sonst wuerde die
    ``1`` aus ``1.0.0-rc1`` mitzaehlen und die Vorabversion vor die
    fertige Fassung schieben.
    """
    v = normalisiere(version)
    kopf = _KOPF.match(v)
    zahlen = tuple(int(z) for z in kopf.group(0).split(".")[:4]) if kopf else ()
    zahlen = zahlen + (0,) * (4 - len(zahlen))
    return (zahlen, 0 if ist_vorabversion(v) else 1, v)


def vergleiche(links: str, rechts: str) -> int:
    """-1, 0 oder 1 -- wie ein Dreiwegevergleich."""
    a, b = _schluessel(links), _schluessel(rechts)
    return (a > b) - (a < b)


def neuer_als(kandidat: str, installiert: str) -> bool:
    """Ist ``kandidat`` eine echte Aktualisierung gegenueber ``installiert``?"""
    if not installiert:
        return bool(kandidat)
    return vergleiche(kandidat, installiert) > 0


@dataclass(frozen=True)
class Aktualisierung:
    """Was ein Update-Lauf herausgefunden hat."""

    verfuegbar: bool
    installiert: str
    neueste: str
    tag: str = ""

    def __bool__(self) -> bool:
        return self.verfuegbar


def waehle_version(
    releases: list[Release],
    installiert: str = "",
    mit_vorabversionen: bool = False,
) -> Aktualisierung:
    """Sucht die hoechste passende Version aus einer Release-Liste."""
    kandidaten = [
        r
        for r in releases
        if mit_vorabversionen or not (r.vorabversion or ist_vorabversion(r.tag))
    ]
    if not kandidaten:
        return Aktualisierung(False, installiert, normalisiere(installiert))

    beste = max(kandidaten, key=lambda r: _schluessel(r.tag))
    neueste = normalisiere(beste.tag)
    return Aktualisierung(
        verfuegbar=neuer_als(neueste, normalisiere(installiert)),
        installiert=normalisiere(installiert),
        neueste=neueste,
        tag=beste.tag,
    )
