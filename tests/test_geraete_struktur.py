"""Flug 2098 -- die Struktur des Zustands-Chips im Panel.

Das Panel ist eine Datei fuer den Browser; was davon in Python pruefbar
ist, sind die Verdrahtungen: die Klassen, die Knopf-Aktion, der Weg in
den Einrichtungsdialog und die Texte beider Sprachen. Dasselbe Mittel
wie bei Markenbild und Fusszeile (Flug 2092, 2097) -- gelesen wird die
Datei, nicht geraten.
"""

from __future__ import annotations

from pathlib import Path

PANEL = Path(__file__).resolve().parents[1] / (
    "custom_components/hacs_lab/frontend/panel.js"
)


def panel_text() -> str:
    return PANEL.read_text(encoding="utf-8")


def test_der_chip_kennt_alle_zustaende() -> None:
    """Jeder Zustand hat sein Wort in beiden Sprachen."""
    text = panel_text()
    for zustand in (
        "neustart",
        "nicht_geladen",
        "eingerichtet",
        "hinzufuegen",
        "yaml",
        "ungewiss",
    ):
        assert "hl-zustand-${i.zustand}" in text, zustand
        assert f'{zustand}: "' in text, zustand


def test_hinzufuegen_ist_ein_knopf_mit_weg() -> None:
    """Der einrichtbare Zustand ist der einzige KNOPF der Chips."""
    text = panel_text()
    assert 'data-aktion="geraete"' in text
    # Der Weg: die Seite von Geräte & Dienste -- der Einrichtungsdialog
    # des Frontend laesst sich von aussen nicht vorbelegen (der Router
    # kuerzt /add?domain= still, bewiesen in Flug 2098).
    assert '/config/integrations/dashboard"' in text


def test_die_klassen_der_farben() -> None:
    """Gold fuer Neustart, Rot fuer nicht geladen, gestrichelt fuer YAML."""
    text = panel_text()
    for klasse in (
        "hl-zustand-neustart",
        "hl-zustand-nicht_geladen",
        "hl-zustand-eingerichtet",
        "hl-zustand-yaml",
        "hl-zustand-ungewiss",
        "hl-zustand-knopf",
    ):
        assert klasse in text, klasse


def test_die_ikonen_der_zustaende() -> None:
    """Jedem Zustand steht ein Zeichen bei, wie den Sternen der Karten."""
    text = panel_text()
    for ikon in (
        "mdi:restart",
        "mdi:alert-circle-outline",
        "mdi:check-circle-outline",
        "mdi:cog-outline",
        "mdi:help-circle-outline",
        "mdi:plus-circle-outline",
    ):
        assert ikon in text, ikon


def test_die_karte_traegt_den_chip() -> None:
    """Die Eintrags-Karte ruft den Chip in ihrer Unterzeile auf."""
    assert "${this._html_zustand(e)}" in panel_text()


def test_die_texte_nennen_geraete_und_dienste() -> None:
    """Beide Sprachen sagen den Ort, wo die Integration zu finden ist."""
    text = panel_text()
    assert "In Geräte & Dienste einrichten" in text
    assert "Set up in Devices & services" in text
    assert "configuration.yaml" in text
