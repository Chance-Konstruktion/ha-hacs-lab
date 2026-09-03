"""GitLab als Anbieter (REST API v4).

Bewusst ohne feste HTTP-Bibliothek: der :class:`HttpClient` wird
hineingereicht. In Home Assistant ist das die aiohttp-Sitzung, in den
Tests eine Attrappe mit vorbereiteten Antworten.
"""

from __future__ import annotations

from urllib.parse import quote

from .forge import ForgeFehler, HttpClient, NichtGefunden, Release, RepositoryInfo
from .identity import GITLAB, RepositoryIdentity, strip_suffix

#: Das Topic, mit dem ein Besitzer sagt: dieses Projekt darf gefunden werden.
TOPIC = "hacs"


def _kodiere(pfad: str) -> str:
    """Aus ``gruppe/projekt`` wird ``gruppe%2Fprojekt`` fuer die Projects API."""
    return quote(strip_suffix(pfad).strip("/"), safe="")


def _zu_info(roh: dict) -> RepositoryInfo:
    return RepositoryInfo(
        provider_id=str(roh["id"]),
        full_name=roh["path_with_namespace"],
        beschreibung=roh.get("description") or "",
        standardzweig=roh.get("default_branch") or "main",
        topics=tuple(roh.get("topics") or ()),
        sterne=int(roh.get("star_count") or 0),
        offene_tickets=int(roh.get("open_issues_count") or 0),
        archiviert=bool(roh.get("archived")),
        web_url=roh.get("web_url") or "",
    )


class GitLabForge:
    """Umsetzung von :class:`~hacs_lab.core.forge.Forge` fuer GitLab."""

    provider = GITLAB

    def __init__(self, http: HttpClient, host: str) -> None:
        self.http = http
        self.host = host.rstrip("/").removeprefix("https://").removeprefix("http://")
        self.api = "https://" + self.host + "/api/v4"

    # -- Stammdaten ---------------------------------------------------
    async def repository(self, pfad: str) -> RepositoryInfo:
        roh = await self._json(self.api + "/projects/" + _kodiere(pfad))
        if not isinstance(roh, dict) or "id" not in roh:
            raise NichtGefunden("kein Projekt unter " + pfad + " auf " + self.host)
        return _zu_info(roh)

    async def identitaet(self, pfad: str) -> RepositoryIdentity:
        info = await self.repository(pfad)
        return RepositoryIdentity(
            provider=self.provider,
            host=self.host,
            provider_id=info.provider_id,
            full_name=info.full_name,
        )

    # -- Versionen ----------------------------------------------------
    async def releases(self, pfad: str) -> list[Release]:
        roh = await self._json(
            self.api + "/projects/" + _kodiere(pfad) + "/releases",
            {"per_page": "30"},
        )
        ergebnis: list[Release] = []
        for eintrag in roh or []:
            tag = eintrag.get("tag_name")
            if not tag:
                continue
            links = (eintrag.get("assets") or {}).get("links") or []
            anhaenge = {a.get("name", ""): a.get("url", "") for a in links}
            ergebnis.append(
                Release(
                    tag=tag,
                    name=eintrag.get("name") or tag,
                    veroeffentlicht_am=eintrag.get("released_at") or "",
                    vorabversion=bool(eintrag.get("upcoming_release")),
                    anhaenge=anhaenge,
                )
            )
        return ergebnis

    async def tags(self, pfad: str) -> list[str]:
        """Rueckfallebene: Projekte ohne Releases, aber mit Tags."""
        roh = await self._json(
            self.api + "/projects/" + _kodiere(pfad) + "/repository/tags",
            {"per_page": "30"},
        )
        return [t["name"] for t in roh or [] if t.get("name")]

    # -- Inhalte ------------------------------------------------------
    async def datei(self, pfad: str, datei: str, ref: str) -> bytes:
        url = (
            self.api
            + "/projects/"
            + _kodiere(pfad)
            + "/repository/files/"
            + quote(datei, safe="")
            + "/raw?ref="
            + quote(ref, safe="")
        )
        return await self.http.get_bytes(url)

    async def archiv_url(self, pfad: str, ref: str) -> str:
        return (
            self.api
            + "/projects/"
            + _kodiere(pfad)
            + "/repository/archive.zip?sha="
            + quote(ref, safe="")
        )

    # -- Entdeckung ---------------------------------------------------
    async def suche_nach_topic(
        self,
        topic: str = TOPIC,
        gruppe: str | None = None,
        mit_untergruppen: bool = True,
    ) -> list[RepositoryInfo]:
        params = {"topic": topic, "per_page": "100", "archived": "false"}
        if gruppe:
            url = self.api + "/groups/" + _kodiere(gruppe) + "/projects"
            if mit_untergruppen:
                params["include_subgroups"] = "true"
        else:
            url = self.api + "/projects"
        roh = await self._json(url, params)
        return [_zu_info(p) for p in roh or [] if "id" in p]

    # -- intern -------------------------------------------------------
    async def _json(self, url: str, params: dict[str, str] | None = None):
        antwort = await self.http.get_json(url, params)
        if isinstance(antwort, dict) and "message" in antwort and "id" not in antwort:
            meldung = str(antwort["message"])
            if "404" in meldung:
                raise NichtGefunden(meldung)
            raise ForgeFehler(meldung)
        return antwort
