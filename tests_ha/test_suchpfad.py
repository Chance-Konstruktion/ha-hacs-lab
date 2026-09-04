"""Der Fallback erweitert den Suchpfad hinten -- nie vorne.

Nachtrag zu #11 (Claude): das Nachbarverzeichnis VORNE an den Suchpfad
gestellt beschattet in einer echten Installation die Standardbibliothek
und Home Assistant. Eine ``types.py`` im Konfigurationsverzeichnis legt
Home Assistant lahm, mit einem Fehlerbild, das niemand mit dieser
Integration in Verbindung bringt.

Der Beweis ist eine Sonde im Unterprozess: ein Haus in der Lage einer
echten Installation (Integration + Kern daneben), bewusst OHNE Eintrag
auf dem Suchpfad, dazu Gift-Dateien, die stdlib-Module vortaeuschen.
Die Integration muss den Kern trotzdem finden, das Haus muss hinten
stehen, und die Gift-Dateien muessen wirkungslos bleiben. Gegen den
alten Stand (``insert(0)``) fliegt jede der drei Pruefungen.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

REPO = Path(__file__).resolve().parent.parent

# stdlib-Module, die ein frischer Interpreter unberuehrt laedt. Die
# Sonde prueft mindestens einen davon gegen die Gift-Datei im Haus.
GIFT_KANDIDATEN = ("tarfile", "wave", "netrc", "fileinput")

SONDE = dedent(
    """
    import importlib.util
    import sys
    import types
    from pathlib import Path

    haus = Path(sys.argv[1]).resolve()
    assert str(haus) not in sys.path, sys.path

    # Das Haus steht bewusst nicht auf dem Suchpfad -- die Lage, in der
    # der Fallback der Integration greifen muss. Der Kern liegt daneben.
    wurzel = types.ModuleType("custom_components")
    wurzel.__path__ = [str(haus / "custom_components")]
    sys.modules["custom_components"] = wurzel

    datei = haus / "custom_components" / "hacs_lab" / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "custom_components.hacs_lab",
        datei,
        submodule_search_locations=[str(datei.parent)],
    )
    modul = importlib.util.module_from_spec(spec)
    sys.modules["custom_components.hacs_lab"] = modul
    spec.loader.exec_module(modul)

    # Der Kern wurde gefunden: der Fallback hat geholfen, nicht gestoert.
    assert "hacs_lab.core.forge" in sys.modules

    # Das Haus steht hinten -- nicht vorne.
    assert sys.path[-1] == str(haus), "Haus steht nicht hinten"
    assert sys.path[0] != str(haus), "Haus steht vorne"

    # Der Giftbecher: stdlib-Module duerfen nicht aus dem Haus kommen.
    geprueft = 0
    for name in ("tarfile", "wave", "netrc", "fileinput"):
        if name in sys.modules:
            continue
        modul = importlib.import_module(name)
        assert str(haus) not in str(modul.__file__), modul.__file__
        print("unschaedlich:", name, modul.__file__)
        geprueft += 1
    assert geprueft >= 1, "keine Gift-Datei mehr zu pruefen"
    """
)


def haus_richten(tmp_path: Path) -> Path:
    """Ein Haus wie eine echte Installation: Integration, Kern daneben."""
    haus = tmp_path / "haus"
    shutil.copytree(REPO / "custom_components", haus / "custom_components")
    shutil.copytree(REPO / "hacs_lab", haus / "hacs_lab")
    for name in GIFT_KANDIDATEN:
        (haus / f"{name}.py").write_text(
            'raise RuntimeError("Beschattung durch " + __file__)\n',
            encoding="utf-8",
        )
    return haus


async def test_fallback_stellt_das_haus_nur_hinten_auf(tmp_path: Path) -> None:
    """Nachtrag zu #11, Befund a: beschattet stdlib und HA nie wieder."""
    haus = haus_richten(tmp_path)
    sonde = tmp_path / "sonde.py"
    sonde.write_text(SONDE, encoding="utf-8")

    umgebung = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    umgebung["PYTHONUTF8"] = "1"
    ergebnis = subprocess.run(
        [sys.executable, str(sonde), str(haus)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env=umgebung,
        timeout=180,
        check=False,
    )
    assert ergebnis.returncode == 0, ergebnis.stdout + "\n" + ergebnis.stderr
