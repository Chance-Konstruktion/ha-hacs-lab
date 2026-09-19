# HACS*lab

> 🇩🇪 Deutsch · [🇬🇧 English](README.en.md)

HACS-Verhalten für selbst gehostete Git-Forges: Home-Assistant-Custom-Components,
die auf **GitLab**, **Gitea** oder **Forgejo** ([Codeberg](https://codeberg.org))
leben, hinzufügen, entdecken und aktuell halten — so, wie HACS es für GitHub tut.

**Kein Fork.** HACS\*lab ist eine eigene Home-Assistant-Integration, die *neben*
HACS läuft. Wir ändern keinen HACS-Code und kopieren keinen. Das hat einen
Grund: Ein Fork müsste jedem HACS-Release hinterherjagen, und niemand außer uns
würde ihn je benutzen.

## Das Problem

HACS kennt genau eine Quelle: GitHub. Ein Custom Repository mit GitLab-Adresse
wird abgelehnt; es gibt dafür keinen Schalter. Wohnen deine Integrationen auf
einer eigenen — oder irgendeiner anderen — GitLab-, Gitea- oder
Forgejo-Instanz, installierst du von Hand und erfährst nie, dass es eine neue
Version gibt.

HACS\*lab schließt diese Lücke. Es spricht alle drei Familien direkt an: Es
findet Repositories mit dem Entdeckungs-Topic, liest ihre Metadaten, vergleicht
Versionen, lädt das Versions-Archiv herunter und installiert es sicher.

## Installation

HACS kann HACS\*lab nicht liefern — es kennt nur GitHub —, also ist der ehrliche
Weg der von Hand. Er dauert etwa zwei Minuten.

**Voraussetzungen**

- Home Assistant 2025.2 oder neuer (die Test-Bahn läuft gegen 2026.2)
- Eine GitLab-, Gitea- oder Forgejo-Instanz (Codeberg), die du vom
  Home-Assistant-Host aus erreichen kannst
- Optional: ein Lese-Token — für private Repositories oder um sanfter mit
  Rate-Limits umzugehen (GitLab-Scope `read_api`; ein Gitea/Forgejo-Token mit
  Leserecht)

**Schritte**

1. Lade das Release-Archiv `hacs-lab-vX.Y.Z.zip` von der
   [Release-Seite](https://github.com/Chance-Konstruktion/hacs-lab/releases)
   herunter. Die SHA-256 des Archivs steht in jeder Release-Beschreibung —
   prüfe sie, wenn du magst. Wer einen Account auf
   `gitlab.schanz.ipv64.net` hat, findet dasselbe Archiv
   [dort](https://gitlab.schanz.ipv64.net/chance-konstruktion/hacs-lab/-/releases)
   in der Package-Registry; die Bytes sind dieselben (der Bau ist
   deterministisch).
2. Entpacke das Archiv **in dein Home-Assistant-Konfigurationsverzeichnis**
   (das mit der `configuration.yaml`). Das Archiv enthält genau einen Ordner,
   `custom_components/hacs_lab/` — Kern-Bibliothek inklusive. Ein Ordner zum
   Kopieren, weiter nichts einzurichten; die Integration findet ihren Kern über
   relative Imports und fasst deinen Python-Pfad nie an.
3. Starte Home Assistant neu.
4. Integration hinzufügen: *Einstellungen → Geräte & Dienste → Integration
   hinzufügen*, nach **HACS\*lab** suchen. Trage den Host deiner Instanz ein
   (ein eingefügter Projekt-Link wird auf seinen Host gekürzt) und optional
   dein Lese-Token. Der Anbieter bleibt in den meisten Fällen auf **auto** —
   HACS\*lab fragt die Instanz selbst, welche API sie spricht (funktioniert
   bei gitlab.com, codeberg.org, gitea.com und selbst gehosteten Servern
   gleichermaßen); wähle GitLab, Forgejo oder Gitea von Hand, nur falls die
   Auto-Erkennung nicht entscheiden kann. Der Dialog prüft die Verbindung und
   sagt dir klipp und klar, wenn sie scheitert.
   Mehrere Instanzen sitzen Seite an Seite — eine je Host, jede mit eigenem
   Anbieter, Token und Einträgen.
5. Nach der Einrichtung bekommst du ein Seitenleisten-Panel — nirgendwo YAML.
   Der Seitenleisten-Eintrag trägt den GitLab-Tanuki, geliefert von der
   Integration selbst (`frontend/iconset.js`, auf jeder Frontend-Seite
   registriert).

> Der Einrichtungs-Dialog und das Panel sprechen Deutsch und Englisch —
> Home Assistant wählt die Sprache, die Integration liefert beide mit
> (`translations/de.json`, `translations/en.json`).

> **Umstieg von v0.1.0?** Dieses Archiv schleppte ein Import-Layout mit, das
> den Einrichtungs-Dialog mit `No module named 'hacs_lab'` bricht — der
> Config-Flow griff nach einem Paket auf oberster Ebene, das Home Assistant nie
> bereitstellt. Räume zuerst **beide** Reste aus deinem
> Konfigurationsverzeichnis: `custom_components/hacs_lab/` **und** den
> verschlagenen Ordner `hacs_lab/` auf oberster Ebene, den das alte Archiv
> daneben ablegte. Danach ein aktuelles Archiv entpacken (ein Ordner, Kern
> inklusive) und neu starten. Seit v0.1.1 trägt die Integration auch ein Icon
> auf der Einstellungsseite (`mdi:gitlab`); `original.png` in diesem
> Repository ist **das eine Markenbild** (Flug 2097): der dämonische
> GitLab-Fuchs, der das Home-Assistant-Haus übernimmt — HA-Blau, ein weißes
> Haus und ein Tanuki in Glutfarben mit brennenden GitLab-Nähten, dessen
> Krallen sich in die Fassade graben. `logo.png` ist die quadratische
> 512er-Form derselben Quelle — für den Projekt-Avatar und später die
> exe-/Verpackungs-Form; das Panel trägt das Bild eingebettet in Leiste
> und Ladeseite.

> **Umstieg von v0.1.1?** Entpacke das v0.2.0-Archiv über den alten Ordner und
> starte neu — gleiches Layout, nichts zu säubern. Neu: Ein Repository im
> schlichten HACS-Layout (`custom_components/<domain>/`, im Tag-Quell-Archiv
> beliebig tief verschachtelt) installiert jetzt **ohne vorgebautes
> Attachment** — HACS\*lab findet die Lagerform selbst (Issue #15) — und
> HACS\*lab akzeptiert jetzt die eigene Lieferform, kann sich also selbst
> aktuell halten: Nimm dieses Repository in die eigene Beobachtungsliste auf,
> und das nächste Release bietet sich als Update an.

## HACS\*lab benutzen

> **Handbuch:** das
> [Projekt-Wiki](https://gitlab.schanz.ipv64.net/chance-konstruktion/hacs-lab/-/wikis/Home)
> erklärt alles in der Tiefe — Installation, Provider anbinden (so viele
> Server, wie du magst, GitLab/Gitea/Forgejo in beliebiger Mischung),
> Einstellungen, den Laden, die Anleitung für Repository-Besitzer und eine
> Seite Fehlerbehebung.

- **Das Panel:** eine Seite, einklappbare Bereiche wie im HACS-Laden —
  *Aktualisierbar*, *Installiert*, *Neu* (Suchfunde), *Herunterladbar* —, jede
  Überschrift zählt ihre Karten. Die obere Leiste folgt deinem GitLab:
  Tanuki-Zeichen, ein Feld „Suchen oder springen zu …“, Werkzeuge zum
  Auffrischen und Hinzufügen, Brotkrumen in der Detailansicht. Dieses Suchfeld
  ist DIE eine Suche (bewusst kein zweites Formular unter den Bereichen):
  Tippen grenzt alles ein, **Enter** fragt jede eingerichtete Instanz direkt —
  ein Wort mit Schrägstrich ist ein Gruppen-Pfad, jedes andere ein
  Schlüsselwort, das der Anbieter gegen Name und Beschreibung passt; die Funde
  landen in *Neu*, und ein Wort, das niemand kennt, ergibt schlicht einen
  leeren Bereich statt eines Fehlers. Karten tragen den Avatar ihres Projekts
  (oder einen Buchstaben in GitLabs Pastellfarben, wenn ein Projekt keinen
  hat). Namen folgen der Textfarbe deines Designs — weiß im Dunkelmodus,
  schwarz im Hellmodus. Während der erste Bestand noch unterwegs ist, zeigt
  das Panel eine Ladekarte im Home-Assistant-Stil (Dreher in der Akzentfarbe
  deines Designs) statt eines leeren Ladens. Scrolle ganz nach unten, und der
  Tanuki unterzeichnet die Seite: *„Made for freedom — no GitHub monopoly,
  because one platform is a single point of failure.”* (das deutsche Design
  bleibt derb: *„Für die Freiheit gebaut — kein GitHub-Monopol-Scheiß.“*) —
  die einzeilige Fusszeile, in deiner Sprache, mit einem Fuchs, der einen
  kleinen Tanz macht, wenn der Zeiger ihn streichelt. Die Beschreibung in der
  Detailansicht ist ein Kleinst-Renderer: Markdown wie gehabt, UND die
  HTML-Tabellen und der Emojen-Schmuck vieler HACS-READMEs kommen als echte
  Tabellen ins Bild — hinter einem Whitelist-Sauberer (Skripte, Rahmen und
  `javascript:`-Adressen fallen ganz weg, Text in den Zellen darf weiter
  Markdown sein). Jedes Repository steht im Laden GENAU EINMAL: ein Fund, der
  schon aufgenommen ist, bleibt beim Eintrag — *Installiert/Aktualisierbar*
  oder *Herunterladbar* oder *Neu*, nie doppelt.
- **Grenzenlos Server, beliebige Mischung:** jede Instanz ist ein
  Konfigurationseintrag — richte so viele ein, wie du magst, jede mit eigenem
  Anbieter (GitLab, Forgejo, Gitea), Token und Takt. Der Laden zeigt sie alle
  als klickbare Instanz-Chips — jeder mit seinem Anbieter beschriftet — mit
  einem gestrichelten „+ Instanz hinzufügen“-Knopf, der den Einrichtungs-Dialog
  für die nächste Domain öffnet. Derselbe Knopf sitzt im Erstlings-Hinweis des
  leeren Ladens.
- **Nie ein leerer Laden:** die Liste lebt im *Lager*, einem Zwischenspeicher
  je Instanz im Home-Assistant-Speicher (`hacs_lab.lager.<host>`). Das Panel
  zu öffnen malt sofort aus dem Lager (kein Netz-Umlauf), dann läuft die
  frische Prüfung im Hintergrund und zeichnet neu, sobald sie landet. Nach
  einem Neustart wird das Lager gelesen, während Home Assistant noch
  hochfährt; der erste Hintergrundlauf folgt kurz darauf, und derselbe Takt,
  den du für den Herzschlag eingestellt hast, hält das Lager frisch —
  `hacs_lab_aktualisiert`-Ereignisse streichen das Panel neu, solange es
  offen bleibt. Der Auffrischen-Knopf erzwingt einen Lauf jederzeit.
- **Custom Repository hinzufügen:** Panel öffnen, *Hinzufügen* wählen, die
  Projekt-URL einfügen, eine Kategorie wählen. HACS\*lab liest Metadaten und
  Version und bietet die Installation an.
- **Entdecken:** Repositories, deren Besitzer auf ihrem GitLab-, Gitea- oder
  Forgejo-Projekt das Topic `hacs` gesetzt haben, erscheinen im Bereich *Neu*
  des Panels — mit Beschreibung, Sternen und neuester Version. Ein zweites
  Topic (`hacs-plugin`, `hacs-theme`, …) legt die Kategorie fest, ohne zu
  fragen.
- **Updates:** jeder Eintrag bekommt eine Update-Entity und einen Herzschlag,
  dessen Takt du je Eintrag einstellen kannst. Ein neues Release oder Tag
  hebt das Update, der Installations-Dienst tauscht die Dateien sicher — erst
  im temporären Verzeichnis aufgebaut, dann ein atomarer Wechsel, bei
  Scheitern zurückgerollt.
- **Bevorzugte Quelle:** trägt ein Release genau ein ZIP-Attachment, wird
  dieses gebaute Artefakt installiert statt des automatisch erzeugten
  Tag-Archivs; alles Mehrdeutige fällt auf das Archiv zurück. Dieser Rückfall
  versteht das Repository-Layout: Er findet `custom_components/<domain>/` auf
  jeder Tiefe und installiert genau diesen Teilbaum — die normale
  HACS-Struktur installiert sich also, wie sie ist, ohne gebautes Attachment
  (Issue #15).
- **Deinstallation & Neustart:** jeder Eintrag mit aufgezeichneter
  Installation deinstalliert auch — der aufgezeichnete Zielpfad wird gegen die
  bekannten Kategorie-Wurzeln geprüft und dann in einem Zug entfernt. Das
  Installieren oder Deinstallieren einer **Integration** hebt einen
  Reparatur-Zettel, Home Assistant neu zu starten (Integrationen laden nur
  beim Start); der Zettel verschwindet von selbst, sobald der Neustart
  passiert ist.
- **Wo die Integration bleibt (Flug 2098):** Installieren reicht nicht —
  Home Assistant scannt `custom_components` erst beim Start, und die Karte
  unter *Geräte & Dienste* entsteht erst, wenn du die Integration danach
  selbst hinzufügst. Der Laden sagt das jetzt in drei Stimmen: jede
  installierte Integration trägt einen **Zustands-Chip** auf ihrer Karte
  (Neustart erforderlich / bereit zum Einrichten — ein Knopf, der *Geräte &
  Dienste* öffnet / eingerichtet / Einrichtung über configuration.yaml /
  nicht geladen — Protokoll prüfen), die Installation legt eine
  **dauerhafte Benachrichtigung** mit demselben Rat (denselben Weg, den
  HACS geht), und der Reparatur-Zettel bleibt, wie er war. Integrationen
  ohne Einrichtungsdialog (`config_flow: false` in ihrer manifest.json)
  können unter *Geräte & Dienste* prinzipiell nie erscheinen — der Chip
  nennt dann den YAML-Weg, statt dich raten zu lassen.
- **Robuster Bestand:** ein umbenanntes Projekt wird an seiner ID erkannt, und
  der Name folgt still; ein erreichbares, aber verändertes Repository wird
  gemeldet, nie geraten; Diagnosen drucken dein Token nie im Klartext.

## Für Repository-Besitzer

Damit HACS\*lab ein Projekt findet und installieren kann (auf GitLab, Gitea
und Forgejo/Codeberg gleichermaßen):

1. Setze das Topic `hacs` unter *Einstellungen → Allgemein → Topics*.
2. Lege ein gültiges `hacs.json` auf den Standard-Zweig. Kleinstform:

   ```json
   {
     "name": "Meine Integration",
     "render_readme": true,
     "homeassistant": "2025.2.0"
   }
   ```

   Repositories mit anderem Layout setzen `content_in_root`, `zip_release`
   oder `filename` — dieselben Konventionen, die HACS etabliert hat.
3. Veröffentliche Versionen als Releases oder zumindest als Tags. Releases
   gewinnen; Tags sind der Rückfall. Kein gebautes Artefekt nötig: das
   automatisch erzeugte Tag-Archiv genügt — HACS\*lab erkennt den Ordner
   `custom_components/<domain>/` darin und installiert genau diesen
   Teilbaum; Dateien der Repository-Wurzel (README, CI-Konfiguration) bleiben
   außen vor. Ein Release mit gebautem ZIP-Attachment (der Domain-Ordner als
   Wurzel) bleibt die genaueste Lieferform und gewinnt weiterhin, wenn
   vorhanden. Und drei Formen, die seit dem 3-System-Test ebenfalls gehen:

   - **flache ZIP-Attachments** — der Inhalt von
     `custom_components/<domain>/` ohne jeden Ordner (so bauen es viele
     HACS-Repos; die `manifest.json` an der Wurzel genügt als Ausweis),
   - **`filename` ohne Attachment** — nennt die `hacs.json` eine Datei wie
     `powerline.zip`, die zum gebauten Release-Anhang gehört, und fehlt der
     Anhang, fällt die Installation still auf die Lagerform des Tag-Archivs
     zurück, statt an einer Datei zu scheitern, die nie im Archiv lag,
   - **Versions-Namen wie `github/260801`** — Tags mit Schrägstrich und
     Datumscodes sortieren mit und installieren mit.

`hacs-development` als zweites Topic markiert ein Repository als
Entwicklungs-Zustand — es wird nur gefunden, wenn ausdrücklich danach gesucht
wird.

## Sicherheit

Code von einer Forge zu installieren ist eine Vertrauensentscheidung, keine
technische. HACS\*lab nimmt den technischen Teil ernst: Versions-Archive
werden mit Wächtern gegen Pfad-Flucht, Größe, Anzahl und Symlinks entpackt —
vier böswillige Test-Archive (Pfad-Traversal, Riesen-Datei, Symlink-Angriff,
Zip-Bombe) gehören zur Testsuite und müssen abgelehnt werden, *bevor*
irgendetwas geschrieben wird. Die Unversehrtheit einer abgebrochenen
Installation lügt nie: erst aufgebaut, dann atomar gewechselt, bei Scheitern
zurückgerollt.

## Repository-Aufbau

```
logo.png, original.png        das eine Markenbild — Quelle (original.png) und
                              512er-Form (logo.png): Panel, Avatar, exe
hacs.json                     Repository-Konventionen für HACS*lab selbst
custom_components/hacs_lab/   die Integration — dünne Home-Assistant-Schicht
  manifest.json               Domain, Version, Config-Flow, Icon
  config_flow.py              Einrichtungs-Dialog mit Verbindungsprüfung
  lager.py                    der Laden-Cache: gehaltene Liste + Bestandslauf,
                              Hintergrund-Takt, `hacs_lab_aktualisiert`
  frontend/panel.js           das Seitenleisten-Panel (ohne YAML) — GitLab-Stil
  frontend/iconset.js         der Tanuki als Seitenleisten-Icon (eigene
                              Icon-Sammlung `hacs-lab`, auf jeder Seite)
  translations/               Dialog-Texte
  core/                       der Kern — reines Python, ohne Home Assistant,
                              ohne Netz in den Tests; liegt hier seit der
                              Entscheidung zur Lieferform (Issue #11)
    forge.py                  die Anbieter-Schnittstelle (GitLab, Forgejo, Gitea, …)
    gitlab_forge.py           GitLab REST v4
    forgejo_forge.py          Forgejo (Codeberg-Aufzeichnungen)
    gitea_forge.py            Gitea — die Forgejo-Schwester (Topic-Suche)
    schmiede.py               die Schmiede-Fabrik + Anbieter-Auto-Erkennung
    http_aiohttp.py           HttpClient auf aiohttp (Sitzung kommt von außen)
    validierung.py            hacs.json, manifest.json
    versionen.py              Versions-Vergleich und Update-Entscheidung
    entdeckung.py             Topic → Kandidat → Validierung
    entpacken.py              bewachtes Entpacken, atomare Installation
auslieferung/release_bauen.py deterministischer Release-Archiv-Bau
tests/                        Kern-Suite — pytest, ohne Netz
tests_ha/                     Home-Assistant-Bahn — offline, am Prüf-Doppel
```

## Entwicklung

Zwei Bahnen, ein Urteil: der Kern läuft schlank, die Framework-Schicht braucht
Home Assistant (Python 3.13, `requirements-ha.txt`).

```bash
python -m pytest -q                       # Kern: kein HA, kein Netz
python -m pytest tests_ha -q -p pytest_homeassistant_custom_component
```

Die Härtungs-Suiten (`*_hart.py` in beiden Bahnen) fahren den Code gegen
feindliche Eingaben: UTF-8-BOM in `hacs.json` (Windows-Editoren lassen eines
da), fünfteilige Versionen, wo `.10` gegen `.9` gewinnen muss, Suchwörter, die
wie Skript-Einschleusungen aussehen, zehntausend Zeichen lange Schlüsselwörter,
Speicher, der nicht hält, was das Schema versprach, Captive Portals, die mit
HTML statt JSON antworten, und 500er, wo vorher ein GitLab aus dem Nichts
behauptet wurde. Die DOM-Seite ist im Browser-Harness bewiesen
(`scripts/schaufenster2093/`): feindliche Repository-Namen, Beschreibungen,
Avatare (`javascript:`-URLs fallen auf den Buchstaben zurück) und Suchwörter
kommen als *Text* an, nie als lebende Elemente — nie führt ein
eingeschleustes Tag etwas aus.

Unter Windows zuerst `PYTHONUTF8=1` setzen — sonst melden gesunde Tests
Fehler, die keine sind.

Releases baut `auslieferung/release_bauen.py` deterministisch: feste
Zeitstempel, sortierte Einträge, reproduzierbare Bytes. Eine Tag-Pipeline baut
das Archiv und heftet es an ein GitLab-Release; der Bau verweigert, wenn Tag
und `manifest.json` verschiedene Versionen nennen.

Die Dokumentation hier ist durchgehend deutsch — auf der Forge ist Deutsch
Amtssprache (Issue #16). Das Denken wohnt in
[ARCHITEKTUR.md](ARCHITEKTUR.md) (die fünf Struktur-Entscheidungen),
[ROADMAP.md](ROADMAP.md) (Meilensteine M0–M10 mit ihren Abnahmen) und
[MITARBEIT.md](MITARBEIT.md) (wie man mitarbeitet). Die Schnittstelle für
einen zweiten Forge-Anbieter — und was HACS selbst dafür übernehmen müsste —
steht ausgearbeitet in [PROPOSAL.md](PROPOSAL.md).

**Wo gearbeitet wird.** Entwickelt wird auf dem selbst gehosteten GitLab —
das ist der Sinn des Projekts — und nach
[GitHub](https://github.com/Chance-Konstruktion/hacs-lab) gespiegelt, damit
Fremde das Projekt finden, installieren und Fehler melden können. Auf dem
GitLab kann sich niemand von außen anmelden, deshalb ist
**[GitHub der Ort für Fehlerberichte](https://github.com/Chance-Konstruktion/hacs-lab/issues)**.
Die englische Fassung dieser Seite liegt als [README.en.md](README.en.md)
daneben.

## Lizenz

[MIT](LICENSE) — Copyright (c) 2026 chance-konstruktion und die
HACS\*lab-Beitragenden.
