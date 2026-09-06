# HACS*lab — Der Stand

> Stand: 2026-09-06, Flug 2097 (hacs-lab-intern) — alles Wichtige auf einer Seite.

## Das Projekt in einem Satz

HACS-Erweiterung für self-hosted GitLab + Gitea/Codeberg/Forgejo: Custom-Repos
installieren, Updates erkennen — ein echtes Produkt für den Imker-Server
(`gitlab.schanz.ipv64.net`, Projekt `chance-konstruktion/hacs-lab`, ID 107).

## Was wo liegt

| Ort | Inhalt |
|---|---|
| `main` (00dbc8a) | Amtssprache Deutsch: README + PROPOSAL + Wiki (MR !32 gemergt) |
| **MR !33** (offen) | **Die drei Wunden aus dem 3-System-Test** — Zweig `flug-2096-drei-wunden` (b65a08d), Pipeline 4038 GRÜN, `can_be_merged` |
| **MR !34** (neu, Flug 2097) | **Das Markenbild** — original.png wird das eine Icon (Panel, Avatar) + diese STAND.md |
| Version | manifest `0.2.0`; Release-Tag-Pipeline baut ZIP deterministisch + Paket-Registry |
| Tests | 340 Kern- (tests/) + 115 HA-Tests (tests_ha/), ruff + Struktur-Wächter in CI |

## Was bewiesen ist

- **Generalprobe (Flug 2095/2096 WABEN): ALLES GRÜN** auf echter Bühne —
  HA 2026.2.3 Kaltstart, ZWEI echte Server (10 GitLab-Funde + 7 Codeberg-Funde),
  bienentanz v1.2.0 sauber installiert, Panel/Fußzeile/Suche/Detail bewiesen
  (Screenshots `flug2095-*.png`).
- **Die drei Wunden (MR !33)** — aus dem Imker-Praxistest auf 3 Systemen:
  1. README-Tabellen als Rohtext → Kleinstrenderer (DOMParser, Whitelist, Tabellen-CSS)
  2. Repos doppelt/dreifach im Laden → _gruppen() prüft vorhanden-Flag + host+full_name: jede Repo genau EIN Gesicht, EIN Platz
  3. Installation nicht 100 % → drei Heilungen (erster Fund reist mit, flacher ZIP-Anhang, filename-Fallback)
  E2E-Folter gegen echte Server: **espeasy-p2p ✓ powerline ✓ vistapool ✓ (vorher 0/3)**,
  Speisetisch 3 installiert + 14 neu ohne Schnitt (Screenshots `flug2096-*.png`).

## Nächste Schritte (Reihenfolge)

1. **MR !33 mergen** → HA neu starten → 3 Systeme erneut wagen.
2. **MR !34 mergen** (Markenbild + STAND.md) — danach trägt das Panel das neue Icon.
3. Wenn alle 3 Systeme grün sind: **v0.3.0-Schnitt** (Imker-Entscheidung; Tag-Pipeline
   baut und veröffentlicht den Release selbst).

## ⚠ Termine, die wehtun

- **GitLab-Token (id 44) stirbt 2026-09-08 — ÜBERMORGEN.** CI, Pages, Issues und
  alle Pushes hängen daran. Vor Ablauf: neuen Token anlegen, Runner-/CI-Variablen
  austauschen, alten entziehen.

## Arbeitsplatz (Biene)

- `repos/hacs-lab` — Arbeitskopie (Zweig liegt auf `flug-2096-drei-wunden`, sauber)
- `repos/ha-bienentanz` — Beispiel-Integration für den Laden (v1.2.0)
- `repos/stock/WABEN.md` — Flugbuch des ganzen Volks
- `e2e/` — echte HA-Testinstanz 2026.2.3 (VENV fällt Sandbox-Resets zum Opfer;
  Neubau: `uv venv --python /usr/bin/python3.13 venv && uv pip install homeassistant==2026.2.3`)
- `scripts/` — verbliebene Werkzeuge nach dem Aufräumflug (E2E-Treiber, HA-Start/Login)
- `repos/bienentanz` — NEU: LXM-Multi-Agent-Mesh (Flug 2101, siehe eigenes README dort)

## Offene Wunden

Keine bekannten Code-Wunden mehr offen — MR !33 heilt alle drei gemeldeten.
Nächste Erkenntnisse kommen aus dem 3-System-Retest nach dem Merge.
