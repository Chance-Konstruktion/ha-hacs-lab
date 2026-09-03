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

M0 (Fundament) steht und ist getestet. Alles Weitere steht in
[ROADMAP.md](ROADMAP.md). Wer mitarbeitet: [MITARBEIT.md](MITARBEIT.md).
Warum es so geschnitten ist: [ARCHITEKTUR.md](ARCHITEKTUR.md).

## Aufbau

```
hacs_lab/core/            reines Python, ohne Home Assistant, ohne Netz testbar
  identity.py             wer ist dieses Repository
  forge.py                die Schnittstelle je Anbieter
  gitlab_forge.py         GitLab REST v4
  validierung.py          hacs.json, manifest.json
  versionen.py            Vergleich und Update-Entscheidung
  entdeckung.py           Topic -> Kandidat -> Pruefung
custom_components/hacs_lab/   die duenne Home-Assistant-Schicht (ab M2)
tests/                    pytest, keine Netzanfrage
```

## Tests

```bash
python -m pytest -q
```

Unter Windows davor `PYTHONUTF8=1` setzen, sonst melden heile Tests
Fehler, die es nicht gibt.

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
