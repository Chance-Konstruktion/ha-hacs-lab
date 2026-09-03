"""GitLab-Client -- geprueft gegen eine Attrappe, ohne Netz."""

import json

import pytest

from hacs_lab.core.forge import NichtGefunden
from hacs_lab.core.gitlab_forge import GitLabForge
from tests.attrappe import FakeHttp, projekt

HOST = "gitlab.example.net"


def forge(**rest):
    return GitLabForge(FakeHttp(**rest), HOST)


@pytest.mark.asyncio
async def test_pfad_wird_kodiert_und_das_suffix_vorher_entfernt():
    http = FakeHttp({"/projects/": projekt()})
    f = GitLabForge(http, "https://" + HOST + "/")
    await f.repository("foo/bar*lab")
    url = http.aufrufe[0][0]
    assert "foo%2Fbar" in url
    assert "*lab" not in url
    assert f.host == HOST


@pytest.mark.asyncio
async def test_stammdaten_kommen_vollstaendig_an():
    info = await forge(json_antworten={"/projects/": projekt()}).repository("foo/bar")
    assert info.provider_id == "789012"
    assert info.full_name == "foo/bar"
    assert info.sterne == 7
    assert info.offene_tickets == 2
    assert info.topics == ("hacs",)


@pytest.mark.asyncio
async def test_identitaet_traegt_host_und_id():
    ident = await forge(json_antworten={"/projects/": projekt()}).identitaet("foo/bar")
    assert ident.uid == "gitlab:789012"
    assert ident.display_full_name == "foo/bar*lab"
    assert ident.host == HOST


@pytest.mark.asyncio
async def test_fehlendes_projekt_wird_als_solches_gemeldet():
    with pytest.raises(NichtGefunden):
        await forge().repository("gibt/es/nicht")


@pytest.mark.asyncio
async def test_releases_werden_uebersetzt():
    antwort = [
        {
            "tag_name": "v1.2.0",
            "name": "Version 1.2.0",
            "released_at": "2026-09-01T10:00:00Z",
            "assets": {"links": [{"name": "paket.zip", "url": "https://x/paket.zip"}]},
        },
        {"name": "ohne Tag"},
    ]
    releases = await forge(json_antworten={"/releases": antwort}).releases("foo/bar")
    assert len(releases) == 1
    assert releases[0].tag == "v1.2.0"
    assert releases[0].anhaenge["paket.zip"] == "https://x/paket.zip"


@pytest.mark.asyncio
async def test_datei_wird_am_richtigen_ref_geholt():
    http = FakeHttp(dateien={"hacs.json": {"name": "Bar"}})
    f = GitLabForge(http, HOST)
    roh = await f.datei("foo/bar", "hacs.json", "v1.2.0")
    assert json.loads(roh)["name"] == "Bar"
    assert "ref=v1.2.0" in http.aufrufe[0][0]
    assert "hacs.json" in http.aufrufe[0][0]


@pytest.mark.asyncio
async def test_archiv_url_zeigt_auf_den_tag():
    url = await forge().archiv_url("foo/bar", "v1.2.0")
    assert url.endswith("/repository/archive.zip?sha=v1.2.0")


@pytest.mark.asyncio
async def test_gruppensuche_nimmt_untergruppen_mit():
    http = FakeHttp({"/groups/": [projekt(), projekt(pid=2, full_name="foo/baz")]})
    treffer = await GitLabForge(http, HOST).suche_nach_topic("hacs", gruppe="foo")
    assert [t.full_name for t in treffer] == ["foo/bar", "foo/baz"]
    params = http.aufrufe[0][1]
    assert params["topic"] == "hacs"
    assert params["include_subgroups"] == "true"
    assert params["archived"] == "false"


@pytest.mark.asyncio
async def test_instanzweite_suche_geht_ohne_gruppe():
    http = FakeHttp({"/api/v4/projects": [projekt()]})
    treffer = await GitLabForge(http, HOST).suche_nach_topic("hacs")
    assert len(treffer) == 1
    assert "include_subgroups" not in http.aufrufe[0][1]
