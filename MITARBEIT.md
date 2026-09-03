# Mitarbeit

Dieses Repo gehoert Chris (`chance-konstruktion`). Es arbeiten mit:
Claude (Opus) und Super Z. Das Repo ist **internal** -- jeder
angemeldete Nutzer der Instanz kann hineinsehen.

## Ablauf

1. Aufgabe ist ein Ticket. Ohne Ticket kein Zweig.
2. Zweig aus `main`, Name `m3-repo-hinzufuegen` (Stufe + Sache).
3. Merge Request anlegen, sobald etwas Vorzeigbares steht -- lieber
   frueh und als Entwurf als spaet und fertig.
4. **Gemergt wird von jemand anderem als dem Autor.** Auch dann, wenn
   es offensichtlich richtig aussieht.
5. Die ausfuehrliche Begruendung gehoert in den MR, nicht in den Chat.

## Was ein MR mitbringen muss

* Tests fuer das, was neu ist -- und zwar auch fuer den Fall, der
  schiefgeht, nicht nur fuer den, der klappt
* `python -m pytest -q` gruen, Pipeline gruen
* Keine Netzanfrage in der CI. Antworten von echten Instanzen werden
  als Aufzeichnung abgelegt, nicht live geholt
* Kein Token, kein Host aus einer Privatinstanz im Code oder in
  Testdaten. `gitlab.example.net` ist der Platzhalter
* Deutsche Kommentare, deutsche Bezeichner im Kern. Was Home Assistant
  vorgibt (`async_setup_entry`, `hass`, `manifest.json`), bleibt
  englisch

## Was ohne Ruecksprache nicht passiert

* HACS-Code kopieren oder HACS forken
* Eine der vier Entscheidungen aus [ARCHITEKTUR.md](ARCHITEKTUR.md)
  umwerfen
* Abhaengigkeiten hinzufuegen. Der Kern soll ohne auskommen, die
  HA-Schicht nutzt, was Home Assistant ohnehin mitbringt
* Schreibende Zugriffe auf eine Forge

## Fuer Super Z im Besonderen

* Alles hier ist absichtlich oeffentlich genug fuer dich: **arbeite
  nicht in privaten Repos** von Chris und nimm nichts Privates als
  Abnahmekriterium. Wenn eine Aufgabe dich dorthin zwingt, sag es im
  Ticket, statt es zu umgehen
* Testdaten baust du dir selbst (siehe `tests/attrappe.py`), nicht aus
  fremden Bestaenden
* Widerspruch ist erwuenscht. Wenn der Zuschnitt einer Stufe falsch
  ist, schreib das ins Ticket, bevor du sie baust
