# Architektur

Vier Entscheidungen, die alles Weitere bestimmen. Wer eine davon
umwerfen will: gern, aber im Ticket und mit Begruendung -- nicht
nebenbei im Code.

## 1. Kein Fork

HACS*lab steht **neben** HACS, nicht darin. Kein kopierter HACS-Code,
keine gepatchte Kopie, keine Abhaengigkeit auf HACS-Interna.

*Warum:* Ein Fork muss jeder HACS-Version hinterherlaufen und bleibt
trotzdem etwas, das nur wir benutzen. Wir bauen die Faehigkeit lieber
so, dass HACS sie spaeter uebernehmen **koennte** (siehe M10).

## 2. Identitaet ist nicht der Name

```python
RepositoryIdentity(
    provider="gitlab",
    host="gitlab.example.net",
    provider_id="789012",
    full_name="foo/bar",
)
```

Daraus abgeleitet:

| Feld | Wert | wofuer |
|---|---|---|
| `uid` | `gitlab:789012` | Schluessel innerhalb einer Instanz |
| `storage_key` | `gitlab@gitlab.example.net:789012` | Schluessel in der Ablage |
| `display_full_name` | `foo/bar*lab` | alles, was ein Mensch sieht |

Drei Folgen, die genau so gewollt sind:

* Ein umbenanntes Projekt bleibt derselbe Eintrag -- die ID traegt.
* Dieselbe Projekt-ID auf zwei GitLab-Instanzen sind zwei Eintraege --
  darum steckt der Host in `storage_key` und nicht in `uid`.
* Ein GitHub-Repo namens `foo/bar-lab` wird nie mit einem
  GitLab-Eintrag verwechselt, weil der Anbieter ein Feld ist und kein
  Namensbestandteil.

`strip_suffix()` gibt es, damit ein Anzeigename nie versehentlich in
eine Abfrage geraet: `foo/bar*lab` existiert im GitLab nicht.

## 3. Eine Schnittstelle je Anbieter, kein Sonderpfad

`core/forge.py` beschreibt, was HACS*lab braucht: Stammdaten,
Releases, eine Datei, eine Archiv-Adresse, eine Topic-Suche. Mehr
nicht. `gitlab_forge.py` ist die erste Umsetzung, `forgejo_forge.py`
(M9, Codeberg als Referenzinstanz) die zweite -- ohne dass der Ablauf,
der Speicher oder die Oberfläche dazwischen etwas vom Anbieter wissen.

Ein `if provider == "gitlab":` ausserhalb der Anbieterklassen gilt als
Fehler. M9 hat die Probe bestanden: der dritte Anbieter ist eine
weitere Klasse und sonst nichts.

Der HTTP-Zugang wird hineingereicht (`HttpClient`), nicht importiert.
Deshalb laeuft der ganze Kern in Tests ohne Netz, und Home Assistant
gibt spaeter einfach seine aiohttp-Sitzung hinein.

## 4. Topic ist Absicht, nicht Aufnahme

```
kein Topic          -> gar nicht erst ansehen
hacs                -> Kandidat, jetzt pruefen
hacs + development  -> Kandidat, aber nur auf Wunsch
```

Danach erst: `hacs.json` lesen, Kategorie bestimmen, validieren. Ein
falsch gesetztes Topic soll nichts kaputtmachen koennen, und "baut
etwas fuer Home Assistant" ist nicht dasselbe wie "gehoert in HACS".

Die Zusatz-Topics `hacs-integration`, `hacs-plugin`, `hacs-theme`,
`hacs-template`, `hacs-appdaemon`, `hacs-python_script` bestimmen die
Kategorie. Ohne Zusatz-Topic gilt `integration`.

## Was der Kern nicht darf

* Home Assistant importieren
* eine HTTP-Bibliothek importieren
* Dateien schreiben (das macht ab M4 die HA-Schicht)
* auf der Forge schreiben -- HACS*lab liest, immer
