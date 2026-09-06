# HACS*lab — Der Stand

> Stand: 2026-09-06, Flug 2098 (hacs-lab-intern) — alles Wichtige auf einer Seite.

## Das Projekt in einem Satz

HACS-Erweiterung für self-hosted GitLab + Gitea/Codeberg/Forgejo: Custom-Repos
installieren, Updates erkennen — ein echtes Produkt für den Imker-Server
(`gitlab.schanz.ipv64.net`, Projekt `chance-konstruktion/hacs-lab`, ID 107).

## Was wo liegt

| Ort | Inhalt |
|---|---|
| `main` (7b9f82c) | Amtssprache Deutsch + Härte + drei Wunden + Markenbild — MR !31/!32/!33/!34 alle gemergt |
| **MR !35** (offen, Flug 2098) | **Die Sichtbarkeit installierter Integrationen** — Zustands-Chip je Karte, dauerhafte Benachrichtigung, der Weg zu Geräte & Dienste; Pipeline 4098 GRÜN |
| Version | manifest `0.2.0`; Release-Tag-Pipeline baut ZIP deterministisch + Paket-Registry |
| Tests | 361 Kern- (tests/) + 127 HA-Tests (tests_ha/), ruff + Struktur-Wächter in CI |
| `super-z/ha-bienentanz` | Test-Integration, jetzt **v1.3.0** mit Einrichtungsdialog (Release + Tag) |

## Was bewiesen ist

- **Generalprobe (Flug 2095/2096 WABEN): ALLES GRÜN** auf echter Bühne —
  HA 2026.2.3 Kaltstart, ZWEI echte Server (10 GitLab-Funde + 7 Codeberg-Funde),
  bienentanz v1.2.0 sauber installiert, Panel/Fußzeile/Suche/Detail bewiesen
  (Screenshots `flug2095-*.png`).
- **Die drei Wunden (MR !33, gemergt)** — README-Tabellen als Rohtext, doppelte
  Gesichter, wackelnde Installationen: alle drei geheilt und auf echter Bühne
  bewiesen (espeasy-p2p ✓ powerline ✓ vistapool ✓, Screenshots `flug2096-*.png`).
- **Die Sichtbarkeit (MR !35, Flug 2098)** — der Imker-Befund «installierte Repos
  unter Geräte & Dienste nicht zu finden» ist vollständig seziert und geheilt:
  1. **Physik:** HA scannt `custom_components` erst beim Start; die Karte unter
     Geräte & Dienste entsteht erst durch den Konfigurationseintrag; Integrationen
     ohne `config_flow` (bienentanz v1.2.0!) können dort PRINZIPIELL nie erscheinen.
  2. **Heilung:** Zustands-Chip je Karte (Neustart erforderlich → In Geräte &
     Dienste einrichten [Knopf] → Eingerichtet; dazu YAML-Weg und Rot fürs
     Nichtgeladene), dauerhafte Benachrichtigung mit derselben Anleitung,
     Lager erfährt die Installation sofort (Version + Zielweg).
  3. **Beweis:** 4 Phasen auf echter Bühne mit 2 Neustarts — v1.2.0 unfindbar
     (Chip «yaml», die Wurzel), v1.3.0 mit Dialog → Flow läuft → KARTE LEBT →
     Chip «eingerichtet» (Screenshots `flug2098-1/2/3.png`).

## Nächste Schritte (Reihenfolge)

1. **MR !35 mergen** → HA neu starten (panel.js + Kern laden frisch) →
   installierte Integrationen tragen ihren Chip.
2. Integrationen, die unter Geräte & Dienste fehlen sollen: prüfen, ob ihre
   manifest.json `config_flow: true` sagt (sonst YAML-Weg — der Chip sagt es).
3. Wenn der Praxistest grün bleibt: **v0.3.0-Schnitt** (Imker-Entscheidung;
   Tag-Pipeline baut und veröffentlicht den Release selbst).

## ⚠ Termine, die wehtun

- **GitLab-Token (id 44) stirbt 2026-09-08 — ÜBERMORGEN.** CI, Pages, Issues und
  alle Pushes hängen daran. Vor Ablauf: neuen Token anlegen, Runner-/CI-Variablen
  austauschen, alten entziehen.

## Arbeitsplatz (Biene)

- `repos/hacs-lab` — Arbeitskopie (Zweig `flug-2098-geraete-sichtbar`, sauber)
- `repos/ha-bienentanz` — Beispiel-Integration für den Laden (**v1.3.0**, gepusht + Release)
- `repos/stock/WABEN.md` — Flugbuch des ganzen Volks (WABEN 2106)
- `e2e/` — echte HA-Testinstanz 2026.2.3 (VENV fällt Sandbox-Resets zum Opfer;
  Neubau: `uv venv --python /usr/bin/python3.13 venv && uv pip install homeassistant==2026.2.3`)
- `scripts/` — verbliebene Werkzeuge (E2E-Treiber: `e2e_geraete_sichtbar.py`
  [Phasen eins–vier], `e2e_kalt_2098.py` [Bühne kalt], HA-Start/Login)
- `repos/bienentanz` — LXM-Multi-Agent-Mesh (Flug 2101/2103, siehe eigenes README dort)

## Offene Wunden

Keine bekannten Code-Wunden offen. Die gemeldeten drei Praxistest-Wunden sind
gemergt (!33), die Sichtbarkeits-Wunde liegt in !35 ready. Nächste Erkenntnisse
kommen aus dem Praxistest nach dem Merge.
