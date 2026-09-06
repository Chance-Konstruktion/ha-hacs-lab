"""Das Markenbild (Flug 2097): original.png ist das eine Icon.

Der Imker hat gesprochen: EIN Bild ueberall, wo ein Logo gebraucht
wird. Diese Pruefungen halten die Zusage gegen den Stand:

* die Quelle steht an der Wurzel (original.png)
* logo.png ist die 512er-Form derselben Quelle (Avatar, exe, Verpackung)
* das Panel traegt das Bild in der Leiste und auf der Ladeseite --
  eingebettet als Daten-URI, damit das Panel ohne zweite Datei lebt

Absichtlich ohne Bildbibliothek: der CI-Raum hat keine, und die Form
(PNG-Kopf, Groesse, Zeichen im panel.js) sagt genug. Getrocknet wie
alle Tests -- keine Netzanfrage, keine Instanz.
"""

from __future__ import annotations

from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
PANEL = WURZEL / "custom_components" / "hacs_lab" / "frontend" / "panel.js"
PNG_KOPF = b"\x89PNG\r\n\x1a\n"


def _ist_png(pfad: Path) -> bool:
    return pfad.read_bytes()[:8] == PNG_KOPF


def test_die_quelle_steht_an_der_wurzel():
    quelle = WURZEL / "original.png"
    assert quelle.exists(), "original.png fehlt an der Wurzel"
    assert _ist_png(quelle)
    assert quelle.stat().st_size > 500_000, "die Quelle ist das volle Bild"


def test_die_512er_form_ist_die_gleiche_marke():
    form = WURZEL / "logo.png"
    assert form.exists(), "logo.png fehlt -- die Avatar-/exe-Form der Marke"
    assert _ist_png(form)
    groesse = form.stat().st_size
    assert 20_000 < groesse < 200_000, (
        f"logo.png wiegt {groesse} Bytes -- GitLims Avatarlimit (200 KiB) "
        "und Ladezeit zugleich"
    )


def test_das_panel_traegt_die_marke_in_leiste_und_ladeseite():
    text = PANEL.read_text(encoding="utf-8")
    assert 'const LOGO_DATAURI = "data:image/png;base64,' in text, (
        "das Markenbild muss als Daten-URI eingebettet sein (kein Netzruft)"
    )
    assert 'class="hl-logo"' in text, "die Leiste zeigt das Markenbild"
    assert 'class="hl-lade-logo"' in text, "die Ladeseite zeigt das Markenbild"
    assert text.count("LOGO_DATAURI") >= 3, (
        "Marke und beide Verwendungen haengen an derselben Konstanten"
    )
    assert "${LOGO_DATAURI}" in text


def test_die_marke_ersetzt_nicht_die_fusszeile():
    """Der Fusszeilen-Fuchs bleibt Fuchs -- nur die Marke ist das neue Bild."""
    text = PANEL.read_text(encoding="utf-8")
    assert 'tanuki_svg("hl-fuss-tanuki")' in text
    assert "hl-logo" in text
