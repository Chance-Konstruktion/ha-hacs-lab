"""Auslieferung (M10): der Pruefstand fuer den Release-ZIP.

Drei Dinge muessen hier bewiesen werden:

* **Form** -- der ZIP spiegelt das Lager so, dass Entpacken im
  Home-Assistant-Konfigurationsverzeichnis jeden Ordner an seinen Ort
  legt. In der alten Form sind das zwei Ordner (Integration + Kern an
  der Wurzel), in der neuen Form (M0.5) nur noch die Integration.
* **Determinismus** -- zwei Bauten aus demselben Stand ergeben
  dieselben Bytes. Ohne das ist ein SHA-256 neben dem Anhang nur
  Dekoration und die Reproduktion eines Releases ein Gluecksspiel.
* **Dogfooding** -- die eigene ``hacs.json`` und ``manifest.json``
  bestehen die Validierung, die HACS*lab von fremden Repositorys
  verlangt. Wer andere prueft, muss selbst bestehen.

Dazu die Fehlerfaelle als Klartext: fehlende Integration, fehlende
manifest.json, Versionen, die nicht uebereinstimmen. Ein Release, das
im Namen eine andere Version nennt als in der manifest.json, waere
eine Falle fuer den, der ihn installiert -- gebaut wird er deshalb
nicht.
"""

import json
import zipfile
from pathlib import Path

import pytest
from hacs_lab.core.validierung import pruefe_hacs_json, pruefe_manifest

from auslieferung.release_bauen import (
    BauFehler,
    baue_release,
    dateien_fuer,
    fingerabdruck,
    form,
    haupt,
    lies_version,
)

#: Die Wurzel des ausgecheckten Standes -- zwei Ebenen ueber diesem Test.
WURZEL = Path(__file__).resolve().parents[1]

#: Das MS-DOS-Epoch als Vergleichswert fuer feste Zeitstempel.
FESTE_ZEIT = (1980, 1, 1, 0, 0, 0)


# ------------------------------------------------------------- Hilfsbau


def baue_test_lager(
    wurzel: Path, integration_dateien: dict[str, str], kern_an_wurzel: bool
) -> Path:
    """Ein Mini-Lager in einem Temporerverzeichnis, wie der Bau es vorfindet.

    ``integration_dateien`` mappt Pfade (relativ zur Integration) auf
    Inhalte. ``kern_an_wurzel`` entscheidet die Form: True baut die
    alte Form mit Kern daneben, False die neue Form (Kern in der
    Integration). Muell (``tests/``, ``__pycache__``) kommt in beide
    -- gerade der muss draussen bleiben.
    """
    integration = wurzel / "custom_components" / "hacs_lab"
    for relativ, inhalt in integration_dateien.items():
        datei = integration / relativ
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(inhalt, encoding="utf-8")
    if kern_an_wurzel:
        kern = wurzel / "hacs_lab" / "core"
        kern.mkdir(parents=True, exist_ok=True)
        (kern / "forge.py").write_text("# Kern-Attrappe\n", encoding="utf-8")
    muell = wurzel / "tests"
    muell.mkdir(exist_ok=True)
    (muell / "test_attrappe.py").write_text(
        "# gehoert nicht in den ZIP\n", encoding="utf-8"
    )
    cache = integration / "__pycache__"
    cache.mkdir(exist_ok=True)
    (cache / "ablage.cpython-312.pyc").write_bytes(b"\x00\x01")
    return wurzel


MINIMAL_MANIFEST = json.dumps(
    {
        "domain": "hacs_lab",
        "name": "HACS*lab",
        "version": "0.1.1",
        "codeowners": ["@chance-konstruktion", "@super-z"],
        "config_flow": True,
        "iot_class": "cloud_polling",
        "requirements": [],
    }
)


def zip_namen(pfad: Path) -> list[str]:
    """Die Dateinamen eines ZIP, sortiert -- die duenne Sicht fuer Asserts."""
    with zipfile.ZipFile(pfad) as archiv:
        return sorted(archiv.namelist())


# ------------------------------------------------- Form: was drin ist


class TestForm:
    def test_eigene_form_packt_den_kern_mit(self, tmp_path: Path):
        """Echter Stand seit M0.5: der Kern wandert IN der Integration.

        Der ZIP enthaelt keine ``hacs_lab``-Wurzel mehr -- entpackt im
        Konfigurationsverzeichnis entsteht genau ein Ordner, und der
        Kern liegt dort, wo die Integration ihn per relativem Import
        findet.
        """
        ziel = baue_release(WURZEL, tmp_path)
        namen = zip_namen(ziel)
        assert "custom_components/hacs_lab/manifest.json" in namen
        assert "custom_components/hacs_lab/__init__.py" in namen
        assert "custom_components/hacs_lab/core/forge.py" in namen
        assert "custom_components/hacs_lab/core/validierung.py" in namen
        assert "custom_components/hacs_lab/core/http_aiohttp.py" in namen
        assert "custom_components/hacs_lab/frontend/panel.js" in namen
        assert "custom_components/hacs_lab/translations/de.json" in namen
        assert not any(n.startswith("hacs_lab/") for n in namen)

    def test_eigene_form_wird_erkannt(self):
        """Das Lager kennt sich selbst -- die Form nach M0.5 ist verbindlich."""
        assert form(WURZEL) == "neue Form (Kern in der Integration)"

    def test_kein_muell_im_zip(self, tmp_path: Path):
        """Tests, Caches und Bytecode haben im Release nichts verloren."""
        ziel = baue_release(WURZEL, tmp_path)
        namen = zip_namen(ziel)
        assert not any(n.startswith("tests") for n in namen)
        assert not any(".pyc" in n for n in namen)
        assert not any("__pycache__" in n for n in namen)
        assert not any(n.startswith(".git") for n in namen)

    def test_neue_form_packt_nur_die_integration(self, tmp_path: Path):
        """Form nach M0.5: kein Kern an der Wurzel, nur die Integration."""
        lager = baue_test_lager(
            tmp_path / "neu",
            {
                "manifest.json": MINIMAL_MANIFEST,
                "__init__.py": "# Schicht\n",
                "core/forge.py": "# Kern in der Integration\n",
            },
            kern_an_wurzel=False,
        )
        ziel = baue_release(lager, tmp_path / "zip")
        namen = zip_namen(ziel)
        assert namen == [
            "custom_components/hacs_lab/__init__.py",
            "custom_components/hacs_lab/core/forge.py",
            "custom_components/hacs_lab/manifest.json",
        ]
        assert not any(n.startswith("hacs_lab/") for n in namen)

    def test_dateien_sind_sortiert(self):
        """Sortierte Eintraege gehoeren zum Determinismus-Vertrag.

        Verglichen wird in Pfad-Ordnung, nicht als Zeichenkette: fuer
        ``frontend.py`` und ``frontend/panel.js`` streiten sich die
        beiden ueber den Vortritt -- entscheidend ist nur, dass die
        Ordnung fest liegt, nicht welche es ist.
        """
        eintraege = dateien_fuer(WURZEL)
        assert eintraege == sorted(eintraege)


# ------------------------------------------------- Determinismus


class TestDeterminismus:
    def test_zwei_bauten_gleiche_bytes(self, tmp_path: Path):
        erster = baue_release(WURZEL, tmp_path / "eins")
        zweiter = baue_release(WURZEL, tmp_path / "zwei")
        assert erster.read_bytes() == zweiter.read_bytes()

    def test_feste_zeitstempel_und_rechte(self, tmp_path: Path):
        """Jeder Eintrag: dieselbe Stunde, schlichte Leserechte, Unix-System."""
        ziel = baue_release(WURZEL, tmp_path)
        with zipfile.ZipFile(ziel) as archiv:
            for info in archiv.infolist():
                assert info.date_time == FESTE_ZEIT
                assert info.create_system == 3
                assert info.external_attr == 0o644 << 16

    def test_fingerabdruck_ist_sha256(self, tmp_path: Path):
        import hashlib

        ziel = baue_release(WURZEL, tmp_path)
        erwartet = hashlib.sha256(ziel.read_bytes()).hexdigest()
        assert fingerabdruck(ziel) == erwartet

    def test_manifest_im_zip_unveraendert(self, tmp_path: Path):
        """Der ZIP spiegelt -- er schreibt nichts um. Das manifest.json im
        ZIP ist byte-identisch mit dem der Integration."""
        ziel = baue_release(WURZEL, tmp_path)
        orig = (WURZEL / "custom_components" / "hacs_lab" / "manifest.json").read_bytes()
        with zipfile.ZipFile(ziel) as archiv:
            assert archiv.read("custom_components/hacs_lab/manifest.json") == orig


# ------------------------------------------------- Version


class TestVersion:
    def test_version_aus_manifest(self):
        assert lies_version(WURZEL) == "0.1.1"

    def test_name_traegt_version(self, tmp_path: Path):
        ziel = baue_release(WURZEL, tmp_path)
        assert ziel.name == "hacs-lab-v0.1.1.zip"

    def test_tag_wird_normalisiert(self, tmp_path: Path):
        ziel = baue_release(WURZEL, tmp_path, version="v0.1.1")
        assert ziel.name == "hacs-lab-v0.1.1.zip"

    def test_abweichende_version_wird_verweigert(self, tmp_path: Path):
        """Tag und manifest.json muessen dasselbe sagen. Ein Release, der im
        Namen v0.9.0 verspricht und als 0.1.1 installiert, ist eine Falle."""
        with pytest.raises(BauFehler, match="0.9.0.*0.1.1|0.1.1.*0.9.0"):
            baue_release(WURZEL, tmp_path, version="v0.9.0")


# ------------------------------------------------- Klartext-Fehler


class TestFehler:
    def test_integration_fehlt(self, tmp_path: Path):
        with pytest.raises(BauFehler, match="Integration fehlt"):
            baue_release(tmp_path, tmp_path / "zip")

    def test_manifest_fehlt(self, tmp_path: Path):
        lager = baue_test_lager(
            tmp_path / "lager",
            {"__init__.py": "# ohne manifest\n"},
            kern_an_wurzel=False,
        )
        with pytest.raises(BauFehler, match="manifest.json fehlt"):
            baue_release(lager, tmp_path / "zip")

    def test_manifest_unlesbar(self, tmp_path: Path):
        lager = baue_test_lager(
            tmp_path / "lager",
            {"manifest.json": "{kein json"},
            kern_an_wurzel=False,
        )
        with pytest.raises(BauFehler, match="unlesbar"):
            baue_release(lager, tmp_path / "zip")

    def test_manifest_ohne_version(self, tmp_path: Path):
        lager = baue_test_lager(
            tmp_path / "lager",
            {"manifest.json": '{"domain": "hacs_lab"}'},
            kern_an_wurzel=False,
        )
        with pytest.raises(BauFehler, match="keine Version"):
            baue_release(lager, tmp_path / "zip")


# ------------------------------------------------- Kommandozeile


class TestKommandozeile:
    def test_baut_in_zielverzeichnis(self, tmp_path: Path, capsys):
        ergebnis = haupt(["--version", "v0.1.1", str(tmp_path)])
        assert ergebnis == 0
        assert (tmp_path / "hacs-lab-v0.1.1.zip").is_file()
        ausgabe = capsys.readouterr().out
        assert "SHA-256" in ausgabe
        assert "Dateien" in ausgabe

    def test_version_ohne_angabe(self, tmp_path: Path):
        assert haupt(["--version"]) == 2

    def test_zu_viele_ziele(self, tmp_path: Path):
        assert haupt([str(tmp_path), "noch-eins"]) == 2


# ------------------------------------------------- Dogfooding


class TestDogfooding:
    def test_eigene_hacs_json_besteht_die_eigene_pruefung(self):
        """HACS*lab verlangt von fremden Repositorys eine gueltige hacs.json
        -- die eigene muss dasselbe bestehen."""
        roh = (WURZEL / "hacs.json").read_bytes()
        befund = pruefe_hacs_json(roh, kategorie="integration")
        assert befund, "; ".join(befund.fehler)

    def test_eigene_manifest_besteht_die_eigene_pruefung(self):
        roh = (WURZEL / "custom_components" / "hacs_lab" / "manifest.json").read_bytes()
        befund = pruefe_manifest(roh)
        assert befund, "; ".join(befund.fehler)
