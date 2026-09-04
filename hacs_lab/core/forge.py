"""Die Schnittstelle, an der spaeter jeder Anbieter haengt.

Absicht: kein ``if provider == "gitlab":`` irgendwo im Ablauf. Wer einen
dritten Anbieter anschliessen will (Codeberg, Forgejo), schreibt eine
weitere Klasse und sonst nichts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class ForgeFehler(Exception):
    """Der Anbieter konnte nicht beantworten, was gefragt wurde."""


class NichtGefunden(ForgeFehler):
    """Das Repository gibt es nicht, oder der Zugang reicht nicht."""


@dataclass(frozen=True)
class Release:
    """Eine veroeffentlichte Version."""

    tag: str
    name: str = ""
    beschreibung: str = ""
    veroeffentlicht_am: str = ""
    vorabversion: bool = False
    anhaenge: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RepositoryInfo:
    """Was ein Anbieter ueber ein Repository verraet.

    ``tickets_url`` und ``releases_url`` sind die Web-Ansichten von
    Tickets und Releases -- pures Anbieterwissen, darum gehoert das
    Fuellen in die Anbieterklasse (und nirgendwo sonst, Stufe M7).
    Ein Anbieter ohne solche Ansichten laesst beide leer; die
    Oberflaeche versteckt die Verweise dann stillschweigend.
    """

    provider_id: str
    full_name: str
    beschreibung: str = ""
    standardzweig: str = "main"
    topics: tuple[str, ...] = ()
    sterne: int = 0
    offene_tickets: int = 0
    archiviert: bool = False
    web_url: str = ""
    tickets_url: str = ""
    releases_url: str = ""


class HttpClient(Protocol):
    """Minimaler HTTP-Zugang, damit der Kern ohne Netz testbar bleibt.

    Vereinbarung: bei 404 wirft die Umsetzung :class:`NichtGefunden`,
    bei allem anderen Unerwarteten :class:`ForgeFehler`. Der Kern kennt
    keine Statuscodes und keine HTTP-Bibliothek.
    """

    async def get_json(self, url: str, params: dict[str, str] | None = None): ...

    async def get_bytes(self, url: str) -> bytes: ...


class Forge(Protocol):
    """Was HACS*lab von einem Anbieter braucht -- mehr nicht."""

    provider: str
    host: str

    async def repository(self, pfad: str) -> RepositoryInfo:
        """Stammdaten zu ``gruppe/projekt``."""

    async def releases(self, pfad: str) -> list[Release]:
        """Veroeffentlichte Versionen, neueste zuerst."""

    async def tags(self, pfad: str) -> list[str]:
        """Tags als Rueckfallebene, wenn ein Projekt keine Releases pflegt.

        Stufe M5: die Update-Erkennung greift darauf zurueck. Wer einen
        Anbieter anbindet, liefert hier einfach die Tagnamen.
        """

    async def datei(self, pfad: str, datei: str, ref: str) -> bytes:
        """Inhalt einer Datei auf einem Zweig oder Tag."""

    async def archiv(self, pfad: str, ref: str) -> bytes:
        """Das Quell-Archiv einer Version als Bytes.

        Stufe M5: der Installations-Dienst der update-Entities holt hier
        das Archiv -- die Adresse kennt nur der Anbieter, sie bleibt
        hinter dieser Naht.
        """

    async def archiv_url(self, pfad: str, ref: str) -> str:
        """Adresse des Quell-Archivs fuer eine Version."""

    async def suche_nach_topic(
        self, topic: str, gruppe: str | None = None, mit_untergruppen: bool = True
    ) -> list[RepositoryInfo]:
        """Alle Projekte, deren Besitzer sie mit ``topic`` gekennzeichnet hat."""
