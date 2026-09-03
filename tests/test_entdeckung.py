"""Entdeckung und Validierung: Topic ist Absicht, nicht Aufnahme."""

import json

import pytest

from hacs_lab.core.entdeckung import entdecke
from hacs_lab.core.gitlab_forge import GitLabForge
from hacs_lab.core.validierung import pruefe_hacs_json, pruefe_manifest
from tests.attrappe import FakeHttp, projekt

HOST = "gitlab.example.net"
GUELTIG = json.dumps({"name": "Bar", "render_readme": True})


@pytest.mark.asyncio
async def test_gefunden_geprueft_uebernommen():
    http = FakeHttp({"/groups/": [projekt()]}, {"hacs.json": GUELTIG})
    funde = await entdecke(GitLabForge(http, HOST), gruppe="foo")
    assert len(funde) == 1
    assert funde[0].uebernehmen
    assert funde[0].anzeigename == "foo/bar*lab"


@pytest.mark.asyncio
async def test_topic_allein_reicht_nicht():
    # Projekt traegt das Topic, hat aber keine hacs.json.
    http = FakeHttp({"/groups/": [projekt()]}, {})
    funde = await entdecke(GitLabForge(http, HOST), gruppe="foo")
    assert not funde[0].uebernehmen
    assert "hacs.json fehlt" in funde[0].befund.fehler


@pytest.mark.asyncio
async def test_entwicklungsrepos_bleiben_ohne_wunsch_draussen():
    http = FakeHttp(
        {"/groups/": [projekt(topics=("hacs", "hacs-development"))]},
        {"hacs.json": GUELTIG},
    )
    forge = GitLabForge(http, HOST)
    assert await entdecke(forge, gruppe="foo") == []
    assert len(await entdecke(forge, gruppe="foo", mit_vorab=True)) == 1


@pytest.mark.asyncio
async def test_kategorie_kommt_aus_dem_zusatz_topic():
    http = FakeHttp(
        {"/groups/": [projekt(topics=("hacs", "hacs-plugin"))]},
        {"hacs.json": json.dumps({"name": "Bar", "filename": "bar.js"})},
    )
    funde = await entdecke(GitLabForge(http, HOST), gruppe="foo")
    assert funde[0].befund.kategorie == "plugin"


def test_kaputte_hacs_json_faellt_durch():
    assert not pruefe_hacs_json("{kein json")
    assert not pruefe_hacs_json(json.dumps({"render_readme": True}))
    assert not pruefe_hacs_json(json.dumps(["liste"]))
    assert not pruefe_hacs_json(GUELTIG, kategorie="erfunden")


def test_gueltige_hacs_json_kommt_durch():
    befund = pruefe_hacs_json(GUELTIG)
    assert befund
    assert befund.name == "Bar"
    assert befund.fehler == []


def test_plugin_ohne_dateiname_ist_gueltig_aber_auffaellig():
    befund = pruefe_hacs_json(json.dumps({"name": "Bar"}), kategorie="plugin")
    assert befund.gueltig
    assert befund.hinweise


def test_manifest_braucht_domain_name_version():
    assert not pruefe_manifest(json.dumps({"domain": "bar"}))
    voll = json.dumps({"domain": "bar", "name": "Bar", "version": "1.2.0"})
    befund = pruefe_manifest(voll)
    assert befund.gueltig
    assert befund.hinweise  # documentation fehlt
