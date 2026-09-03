# HACS*lab

HACS-Bedienung fuer GitLab-Repositories: hinzufuegen, entdecken,
aktualisieren -- so wie HACS es mit GitHub tut.

**Kein Fork.** HACS*lab ist eine eigene Home-Assistant-Integration, die
neben HACS laeuft. Wir aendern keinen HACS-Code und kopieren keinen.
Das hat einen Grund: ein Fork muesste jeder HACS-Version hinterherlaufen,
und niemand ausser uns wuerde ihn benutzen.

## Das Problem

HACS kennt als Quelle ausschliesslich GitHub. Ein Custom-Repository mit
einer GitLab-Adresse wird abgewiesen; einen Schalter dafuer gibt es
nicht. Wer seine Integrationen im eigenen GitLab hat, installiert von
Hand und merkt neue Versionen gar nicht.

## Die Loesung in einem Bild

```
GitLab
   |
   v
Topic = hacs                 <- der Besitzer sagt: darf gefunden werden
   |
   v
Repository gefunden
   |
   v
hacs.json pruefen            <- Absicht reicht nicht, der Inhalt zaehlt
   |
   v
HACS*lab-Repository          -> foo/bar*lab
```

## Die `*lab`-Kennzeichnung

Ein Repository wird nicht ueber seinen Namen identifiziert, sondern
ueber **Anbieter + Host + Anbieter-ID**. Der Name ist Anzeige.

```
GitHub                       GitLab
------                       ------
foo/bar                      foo/bar*lab
uid: github:123456           uid: gitlab:789012
full_name: foo/bar           full_name: foo/bar
provider: github             provider: gitlab
```

Damit sind das zwei vollstaendig verschiedene Eintraege, die
nebeneinander installiert sein duerfen. Das Suffix erzeugt
**ausschliesslich HACS*lab**; im GitLab wird nichts umbenannt, die
echte Adresse bleibt `https://gitlab.example.net/foo/bar`.

Wichtig ist die Trennung von Identitaet und Anzeige: ein GitHub-Repo,
das wirklich `irgendwas-lab` heisst, wird deshalb nie gegen ein GitLab
gefragt -- die Quelle steht als eigenes Feld im Datensatz, nicht im
Namen.

## Stand

M0 (Fundament), M1 (HTTP-Zugang) und M2 (Home-Assistant-Geruest)
stehen und sind getestet. Einrichten in Home Assistant: Integration
hinzufuegen, Host der GitLab-Instanz angeben (ein eingefuegter Link
wird auf den Host gekuerzt), optional einen Lesetoken -- der Dialog
prueft die Verbindung und meldet sich verstaendlich, wenn sie nicht
kommt. Mehrere Instanzen nebeneinander sind moeglich, der Abstand des
Herzschlags ist pro Eintrag einstellbar. Alles Weitere steht in
[ROADMAP.md](ROADMAP.md). Wer mitarbeitet:
[MITARBEIT.md](MITARBEIT.md). Warum es so geschnitten ist:
[ARCHITEKTUR.md](ARCHITEKTUR.md).

## Aufbau

```
hacs_lab/core/            reines Python, ohne Home Assistant, ohne Netz testbar
  identity.py             wer ist dieses Repository
  forge.py                die Schnittstelle je Anbieter
  gitlab_forge.py         GitLab REST v4
  validierung.py          hacs.json, manifest.json
  versionen.py            Vergleich und Update-Entscheidung
  entdeckung.py           Topic -> Kandidat -> Pruefung
hacs_lab/http_aiohttp.py  der HTTP-Zugang, auf einer hereingereichten
                           aiohttp-Sitzung (importiert sie nicht)
custom_components/hacs_lab/   die duenne Home-Assistant-Schicht
  manifest.json           Domain, Version, Konfigurationsdialog
  __init__.py             richten und abmelden: Sitzung, Forge,
                         Ablage, Herzschlag (DataUpdateCoordinator)
  config_flow.py          Einrichtungsdialog mit Pruefverbindung
  ablage.py               Speicher Version 1 mit Migrationsfunktion
  const.py                Namen, Normalisierung, Speicherschluessel
  strings.json, translations/  Texte fuer den Dialog
tests/                    pytest, keine Netzanfrage
tests/aufzeichnungen/    aufgezeichnete Koerper echter Antworten
tests_ha/                 Home-Assistant-Bahn: Einrichtungsdialog,
                         Herzschlag, Ablage -- offline auf der Attrappe
```

## Tests

Zwei Bahnen, ein Befund: der Kern laeuft schlank, das Geruest braucht
Home Assistant (Python 3.13, requirements-ha.txt).

```bash
python -m pytest -q                       # Kern: ohne HA, ohne Netz
python -m pytest tests_ha -q -p pytest_homeassistant_custom_component
```

Unter Windows davor `PYTHONUTF8=1` setzen, sonst melden heile Tests
Fehler, die es gibt, nicht.

## Fuer Repository-Besitzer

Damit ein GitLab-Projekt von HACS*lab gefunden wird:

1. In GitLab unter *Settings -> General -> Topics* das Topic `hacs`
   setzen.
2. Eine gueltige `hacs.json` im Standardzweig ablegen.
3. Versionen als Release oder wenigstens als Tag veroeffentlichen.

Optional: `hacs-plugin`, `hacs-theme` usw. als zweites Topic setzen,
dann stimmt die Kategorie ohne Nachfrage. `hacs-development` markiert
ein Repository als Entwicklungsstand -- es wird nur gefunden, wenn man
danach sucht.
