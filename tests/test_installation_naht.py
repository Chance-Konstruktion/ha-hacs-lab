"""Die M4b-Naht: Anhang-Auswahl, Beschaffung, Zielweg, Deinstallation.

Vier Dinge muessen hier bewiesen werden:

* **Auswahl** -- genau EIN Zip-Anhang zaehlt; null oder mehrere bedeuten
  Rueckfall aufs Tag-Archiv. Raterei zwischen Zips ist keine Auswahl.
* **Beschaffung** -- Anhang zuerst, Tag-Archiv sonst; auch dann, wenn
  die Release-Frage selbst scheitert (der Anhang ist Bevorzugung,
  keine Pflicht).
* **Zielweg** -- die Installation meldet den Weg relativ zur
  Konfiguration; genau dieser Weg geht in das Protokoll.
* **Deinstallation** -- der verzeichnete Weg wird geprueft (Ablagen
  lassen sich von Hand veraendern), das Ziel in einem Zug wegbenannt,
  nie halbe Zustaende.

Die Attrappe fuer den HTTP-Zugang des Kerns wohnt in
``tests/attrappe_kern.py``; der Forge hier ist eine kleine Klasse, kein
Netz.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from hacs_lab.core.forge import Release
from hacs_lab.core.zielpfade import ist_zielpfad
from hacs_lab.installation import (
    InstallationsFehler,
    _deinstalliere_sync,
    beschaffe_archiv,
    lese_archiv_datei,
    waehle_anhang,
)

# ---------------------------------------------------- Anhang-Auswahl


class TestWaehleAnhang:
    def test_genau_ein_zip_liefert_die_adresse(self):
        assert waehle_anhang({"paket.zip": "https://x/paket.zip"}) == (
            "https://x/paket.zip"
        )

    def test_grossschreibung_zaehlt_nicht(self):
        assert waehle_anhang({"Paket.ZIP": "https://x/p"}) == "https://x/p"

    def test_kein_zip_kein_treffer(self):
        assert waehle_anhang({"paket.tar.gz": "https://x/t"}) is None
        assert waehle_anhang({"sha256": "https://x/s"}) is None
        assert waehle_anhang({}) is None

    def test_zwei_zips_kein_treffer(self):
        """Zwischen zwei Zips wuerfeln ist Raterei -- also: keiner."""
        assert waehle_anhang({"a.zip": "https://x/a", "b.zip": "https://x/b"}) is None

    def test_zip_mit_leerer_adresse_zaehlt_nicht(self):
        assert waehle_anhang({"paket.zip": ""}) is None

    def test_zip_neben_zusaetzen_nimmt_das_zip(self):
        """Signaturen sind Zusatz, nicht Konkurrenz."""
        assert (
            waehle_anhang({"paket.zip": "https://x/p", "paket.zip.sha256": "https://x/s"})
            == "https://x/p"
        )


# ----------------------------------------------------- Beschaffung


class ForgeAttrappe:
    """Ein Forge, der alles aus dem Regal kennt -- ohne Netz."""

    def __init__(
        self,
        releases: list[Release] | None = None,
        anhaenge: dict[str, bytes] | None = None,
        versagt_bei_releases: bool = False,
    ) -> None:
        self.releases_antwort = releases or []
        self.anhaenge = anhaenge or {}
        self.versagt_bei_releases = versagt_bei_releases
        self.verlangte_url: str | None = None
        self.verlangtes_archiv: tuple[str, str] | None = None

    async def releases(self, pfad: str) -> list[Release]:
        if self.versagt_bei_releases:
            raise RuntimeError("Release-Frage gescheitert")
        return self.releases_antwort

    async def anhang(self, url: str) -> bytes:
        self.verlangte_url = url
        return self.anhaenge[url]

    async def archiv(self, pfad: str, ref: str) -> bytes:
        self.verlangtes_archiv = (pfad, ref)
        return b"ARCHIV:" + ref.encode()


def _release(tag: str, anhaenge: dict[str, str]) -> Release:
    return Release(tag=tag, name=tag, anhaenge=anhaenge)


class TestBeschaffeArchiv:
    async def test_anhang_geht_vor(self):
        forge = ForgeAttrappe(
            releases=[_release("v1", {"p.zip": "https://x/p.zip"})],
            anhaenge={"https://x/p.zip": b"ZIP-BYTES"},
        )
        archiv, herkunft = await beschaffe_archiv(forge, "foo/bar", "v1")
        assert archiv == b"ZIP-BYTES"
        assert herkunft == "anhang"
        assert forge.verlangtes_archiv is None  # Archiv nie angefasst

    async def test_ohne_anhang_das_tag_archiv(self):
        forge = ForgeAttrappe(releases=[_release("v1", {})])
        archiv, herkunft = await beschaffe_archiv(forge, "foo/bar", "v1")
        assert archiv == b"ARCHIV:v1"
        assert herkunft == "archiv"

    async def test_mehrdeutiger_anhang_das_tag_archiv(self):
        forge = ForgeAttrappe(
            releases=[_release("v1", {"a.zip": "u1", "b.zip": "u2"})],
            anhaenge={"u1": b"x", "u2": b"y"},
        )
        _, herkunft = await beschaffe_archiv(forge, "foo/bar", "v1")
        assert herkunft == "archiv"

    async def test_anderer_tag_das_tag_archiv(self):
        forge = ForgeAttrappe(
            releases=[_release("v2", {"p.zip": "https://x/p.zip"})],
            anhaenge={"https://x/p.zip": b"ZIP"},
        )
        _, herkunft = await beschaffe_archiv(forge, "foo/bar", "v1")
        assert herkunft == "archiv"

    async def test_versagende_release_frage_das_tag_archiv(self):
        """Der Anhang ist Bevorzugung -- sein Scheitern ist kein Abbruch."""
        forge = ForgeAttrappe(versagt_bei_releases=True)
        archiv, herkunft = await beschaffe_archiv(forge, "foo/bar", "v1")
        assert archiv == b"ARCHIV:v1"
        assert herkunft == "archiv"


# --------------------------------------------------------- Zielweg


class TestIstZielpfad:
    def test_bekannte_wurzeln_zaehlen(self):
        assert ist_zielpfad("custom_components/beispiel")
        assert ist_zielpfad("themes")
        assert ist_zielpfad("www/community/beispiel")

    def test_fremde_wurzel_zaehlt_nicht(self):
        assert not ist_zielpfad("homeassistant/components")
        assert not ist_zielpfad("configuration.yaml")

    def test_absolut_und_flucht_zaehlen_nicht(self):
        assert not ist_zielpfad("/etc")
        assert not ist_zielpfad("custom_components/../x")
        assert not ist_zielpfad("")
        assert not ist_zielpfad("..")


# ---------------------------------------------------- Deinstallation


class TestDeinstallation:
    def test_entfernt_das_verzeichnete_ziel(self, tmp_path: Path):
        ziel = tmp_path / "custom_components" / "beispiel"
        ziel.mkdir(parents=True)
        (ziel / "manifest.json").write_text("{}", encoding="utf-8")

        _deinstalliere_sync("custom_components/beispiel", tmp_path)

        assert not ziel.exists()
        zwischen = tmp_path / ".hacs_lab_zwischenlager"
        assert not list(zwischen.glob("*.weg"))  # auch das Lager ist leer

    def test_untauglicher_weg_wird_abgewiesen(self, tmp_path: Path):
        """Die Ablage ist eine Datei -- Vertrauen ist keine Pruefung."""
        (tmp_path / "wichtig.txt").write_text("bleib", encoding="utf-8")
        for boese in (
            "../wichtig",
            "/etc",
            "homeassistant/components",
            "custom_components/../../wichtig",
            "",
        ):
            with pytest.raises(InstallationsFehler):
                _deinstalliere_sync(boese, tmp_path)
        assert (tmp_path / "wichtig.txt").read_text(encoding="utf-8") == "bleib"

    def test_fehlendes_ziel_ist_klartext(self, tmp_path: Path):
        with pytest.raises(InstallationsFehler, match="nichts installiert"):
            _deinstalliere_sync("custom_components/weg_damit", tmp_path)

    def test_alte_weg_rest_werden_mit_geraeumt(self, tmp_path: Path):
        """Ein frueherer Abbruch darf beim naechsten Lauf kein Hindernis sein."""
        zwischen = tmp_path / ".hacs_lab_zwischenlager"
        zwischen.mkdir()
        (zwischen / "beispiel.weg").mkdir()
        (zwischen / "beispiel.weg" / "muell.txt").write_text("x", encoding="utf-8")

        ziel = tmp_path / "custom_components" / "beispiel"
        ziel.mkdir(parents=True)
        _deinstalliere_sync("custom_components/beispiel", tmp_path)
        assert not ziel.exists()


# ------------------------------------------------------ Archiv-Lesen


class TestLeseArchivDatei:
    def test_kein_zip_ist_klartext(self):
        """Ein Release-Anhang, der kein ZIP ist, wird nicht installiert."""
        with pytest.raises(InstallationsFehler, match="kein ZIP"):
            lese_archiv_datei(b"definitiv kein zip", "manifest.json")
