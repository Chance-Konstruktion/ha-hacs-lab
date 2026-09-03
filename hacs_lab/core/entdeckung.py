"""Entdeckung: vom Topic zum geprueften Repository.

Ablauf, bewusst zweistufig:

    Topic ``hacs``  ->  Kandidat gefunden
                    ->  hacs.json gelesen und geprueft
                    ->  Kategorie plausibel
                    ->  erst dann aufgenommen

Ein Topic allein nimmt nichts auf. Es sagt nur, dass der Besitzer
gefunden werden moechte.
"""

from __future__ import annotations

from dataclasses import dataclass

from .forge import NichtGefunden, RepositoryInfo
from .identity import GITLAB, RepositoryIdentity
from .validierung import Befund, pruefe_hacs_json


@dataclass
class Fund:
    """Ein Kandidat mitsamt Pruefergebnis."""

    identitaet: RepositoryIdentity
    info: RepositoryInfo
    befund: Befund

    @property
    def uebernehmen(self) -> bool:
        return self.befund.gueltig

    @property
    def anzeigename(self) -> str:
        return self.identitaet.display_full_name


def _kategorie_aus_topics(topics: tuple[str, ...]) -> str:
    """Erlaubt ``hacs-plugin`` & Co. als Zusatz-Topic zur Kategorie."""
    for topic in topics:
        klein = topic.lower()
        if klein.startswith("hacs-") and klein != "hacs-development":
            return klein[len("hacs-") :]
    return "integration"


async def entdecke(
    forge,
    gruppe: str | None = None,
    topic: str = "hacs",
    mit_vorab: bool = False,
) -> list[Fund]:
    """Sucht Projekte mit dem Topic und prueft jedes einzeln.

    ``mit_vorab`` nimmt zusaetzlich Projekte auf, die sich selbst als
    ``hacs-development`` gekennzeichnet haben.
    """
    funde: list[Fund] = []
    for info in await forge.suche_nach_topic(topic, gruppe=gruppe):
        if not mit_vorab and "hacs-development" in info.topics:
            continue
        funde.append(await pruefe_kandidat(forge, info))
    return funde


async def pruefe_kandidat(forge, info: RepositoryInfo) -> Fund:
    """Liest ``hacs.json`` im Standardzweig und bewertet den Kandidaten."""
    identitaet = RepositoryIdentity(
        provider=getattr(forge, "provider", GITLAB),
        host=forge.host,
        provider_id=info.provider_id,
        full_name=info.full_name,
    )
    kategorie = _kategorie_aus_topics(info.topics)
    try:
        roh = await forge.datei(info.full_name, "hacs.json", info.standardzweig)
    except NichtGefunden:
        return Fund(
            identitaet,
            info,
            Befund(False, kategorie=kategorie, fehler=["hacs.json fehlt"]),
        )
    return Fund(identitaet, info, pruefe_hacs_json(roh, kategorie))
