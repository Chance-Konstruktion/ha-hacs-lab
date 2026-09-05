/**
 * HACS*lab Panel -- der Laden in GitLab-Hand (Flug 2083).
 *
 * Stufe M7 war das Gesicht: Bedienung ohne YAML, vanilles JavaScript
 * als ES-Modul, geladen ueber ``/hacs_lab/panel.js``. Das Frontend
 * von Home Assistant findet hier das Element ``hacs-lab-panel`` und
 * setzt ihm ``hass`` und ``panel``. Alles weitere laufen die WebSocket-
 * Befehle aus ``websocket_api.py`` und die ganz normalen Dienste
 * (install auf den update-Entities aus Stufe M5).
 *
 * Flug 2083 zieht dem Laden die Tracht des Imkers-Servers an:
 *
 * * der Balken oben sieht aus wie GitLabs Leiste -- dunkel, mit dem
 *   Tanuki (das echte Markenbild, vier Pfade, vom Server geholt), der
 *   Suche in der Mitte (``Suchen oder springen zu …``) und Werkzeugen
 *   rechts (Frischholen, Neu). Brotkrumen im Detail wie dort.
 * * die Liste ist EINE Seite in einklappbaren Abschnitten, wie im
 *   HACS-Laden: Aktualisierbar, Installierbar, Neu, Downloadbar --
 *   jeder Kopf zaehlt seine Karten und laesst sich zuklappen.
 * * der Laden frischt sich selber auf: jedes Betreten laeuft
 *   ``hacs_lab/erneuern`` -- der frische M5-Lauf, nicht der Takt.
 *   Ruht die Bedienung (15 Sekunden), wird kein zweiter Lauf erzwungen.
 *
 * Zwei Sprachen, im File selbst: Deutsch und Englisch, gewaehlt nach
 * der Sprache der Bedienung. Der Kennzeichnungs-Suffix (*lab, *forge)
 * kommt fertig vom Server -- hier wird nichts doppelt gewusst.
 *
 * Sicherheit: Der Markdown-Renderer flieht zuerst JEDES Zeichen und
 * baut danach erst Markup. Links und Bilder werden nur fuer
 * http(s)-Adressen gebaut, alles andere bleibt Text.
 */

const TEXTE = {
  de: {
    titel: "HACS*lab",
    suche: "Suchen oder springen zu …",
    aktualisieren: "Liste aktualisieren",
    neu_knopf: "Neu hinzufügen",
    sortierung: "Sortierung",
    sort: { name: "Name", sterne: "Sterne", datum: "Datum" },
    anzahl: (n) => `${n} Repositor${n === 1 ? "y" : "ies"}`,
    abschnitte: {
      aktualisierbar: "Aktualisierbar",
      installierbar: "Installierbar",
      neu: "Neu",
      downloadbar: "Downloadbar",
    },
    abschnittstexte: {
      aktualisierbar: "Eine neuere Version ist erschienen",
      installierbar: "Beobachtet, aber noch nichts heruntergeladen",
      neu: "Funde der Suche — noch nicht aufgenommen",
      downloadbar: "Heruntergeladen und auf dem neuesten Stand",
    },
    abschnitte_leer: {
      aktualisierbar: "Nichts zu tun — alles auf dem neuesten Stand.",
      installierbar: "Nichts Beobachtetes ohne Download.",
      neu: "Noch keine Funde — starte die Suche.",
      downloadbar: "Noch nichts heruntergeladen.",
    },
    scan: "Suchen",
    quelle: "Quelle",
    gruppe: "Gruppe (leer = ganze Instanz)",
    untergruppen: "mit Untergruppen",
    entwicklung: "auch hacs-development",
    hinzufuegen: "Hinzufügen",
    entfernen: "Entfernen",
    deinstallieren: "Deinstallieren",
    installieren: "Installieren",
    update_install: "Aktualisieren",
    details: "Details",
    zurueck: "Zurück",
    instanzen_leer: "Keine Instanz eingerichtet — zuerst eine Instanz anlegen.",
    installiert_label: "installiert",
    neueste_label: "neueste",
    vorab: "Vorabversion",
    readme: "Beschreibung",
    readme_fehlt: "Dieses Projekt hat keine lesbare Beschreibung.",
    releases: "Releases",
    keine_releases: "Keine Releases — Tags zählen als Fallback.",
    repository: "Repository",
    tickets: "Tickets",
    releases_link: "Releases",
    sterne_ein: "Stern",
    sterne_viele: "Sterne",
    kategorie: "Kategorie",
    schon_da: "schon in der Liste",
    entfernt_hinweis: "Nur die Beobachtung — Dateien bleiben (Deinstallieren ist der eigene Knopf).",
    entfernen_frage: (name) =>
      `${name} entfernen? Installierte Dateien bleiben liegen.`,
    deinstalliert_hinweis:
      "Nimmt die installierten Dateien weg — bei Integrationen steht der nötige Neustart im Reparatur-Brett.",
    deinstallieren_frage: (name) =>
      `${name} deinstallieren? Die installierten Dateien werden entfernt.`,
    fehler: {
      unbekannte_instanz: "Diese Instanz ist nicht (mehr) eingerichtet.",
      nicht_gefunden: "Repository nicht gefunden — Adresse prüfen.",
      forge_fehler: "Die Instanz antwortet nicht richtig.",
      bereits_vorhanden: "Dieses Repository steht schon in der Liste.",
      kategorie_unbekannt: "Diese Kategorie gibt es nicht.",
      nicht_mehr_da: "Der Eintrag ist schon weg.",
      homeassistant_error: "Home Assistant meldet einen Fehler.",
      sonst: "Etwas ist schiefgegangen.",
    },
    scan_laeuft: "Suche läuft …",
    frisch_laeuft: "frischer Lauf …",
  },
  en: {
    titel: "HACS*lab",
    suche: "Search or go to …",
    aktualisieren: "Refresh list",
    neu_knopf: "Add new",
    sortierung: "Sort by",
    sort: { name: "Name", sterne: "Stars", datum: "Date" },
    anzahl: (n) => `${n} repositor${n === 1 ? "y" : "ies"}`,
    abschnitte: {
      aktualisierbar: "Updatable",
      installierbar: "Installable",
      neu: "New",
      downloadbar: "Downloadable",
    },
    abschnittstexte: {
      aktualisierbar: "A newer version has been released",
      installierbar: "Watched, but nothing downloaded yet",
      neu: "Findings of the scan — not added yet",
      downloadbar: "Downloaded and up to date",
    },
    abschnitte_leer: {
      aktualisierbar: "Nothing to do — everything is up to date.",
      installierbar: "Nothing watched without a download.",
      neu: "No findings yet — run the scan.",
      downloadbar: "Nothing downloaded yet.",
    },
    scan: "Scan",
    quelle: "Source",
    gruppe: "Group (empty = whole instance)",
    untergruppen: "include subgroups",
    entwicklung: "include hacs-development",
    hinzufuegen: "Add",
    entfernen: "Remove",
    deinstallieren: "Uninstall",
    installieren: "Install",
    update_install: "Update",
    details: "Details",
    zurueck: "Back",
    instanzen_leer: "No instance configured — set one up first.",
    installiert_label: "installed",
    neueste_label: "latest",
    vorab: "pre-release",
    readme: "Description",
    readme_fehlt: "This project has no readable description.",
    releases: "Releases",
    keine_releases: "No releases — tags count as fallback.",
    repository: "Repository",
    tickets: "Tickets",
    releases_link: "Releases",
    sterne_ein: "star",
    sterne_viele: "stars",
    kategorie: "Category",
    schon_da: "already on the list",
    entfernt_hinweis: "Only the watch — files stay in place (uninstall is its own button).",
    entfernen_frage: (name) => `Remove ${name}? Installed files stay in place.`,
    deinstalliert_hinweis:
      "Takes the installed files away — for integrations the required restart shows up in the repair center.",
    deinstallieren_frage: (name) =>
      `Uninstall ${name}? The installed files will be removed.`,
    fehler: {
      unbekannte_instanz: "This instance is not configured (any more).",
      nicht_gefunden: "Repository not found — check the address.",
      forge_fehler: "The instance did not answer properly.",
      bereits_vorhanden: "This repository is already on the list.",
      kategorie_unbekannt: "Unknown category.",
      nicht_mehr_da: "Already removed.",
      homeassistant_error: "Home Assistant reported an error.",
      sonst: "Something went wrong.",
    },
    scan_laeuft: "Scanning …",
    frisch_laeuft: "fresh run …",
  },
};

/** Sprache der Bedienung -- Deutsch, sonst Englisch. */
function sprache(hass) {
  const code = (hass && hass.locale && hass.locale.language) || "en";
  return String(code).toLowerCase().startsWith("de") ? "de" : "en";
}

/** Flieht jedes Zeichen, das Markup werden koennte. */
function fliehe(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Nur absolute http(s)-Adressen duerfen Links oder Bilder werden. */
function adresse_ok(u) {
  return /^https?:\/\//i.test(String(u));
}

/** Inline-Markdown auf bereits GEFLOHENEM Text. */
function inline_markdown(s) {
  const codes = [];
  let t = String(s).replace(/`([^`]+)`/g, (m, c) => {
    codes.push(c);
    return "\x00" + (codes.length - 1) + "\x00";
  });
  t = t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (m, alt, u) =>
    adresse_ok(u) ? `<img src="${u}" alt="${alt}" loading="lazy">` : alt
  );
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, text, u) =>
    adresse_ok(u)
      ? `<a href="${u}" target="_blank" rel="noopener noreferrer">${text}</a>`
      : text
  );
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  t = t.replace(/\x00(\d+)\x00/g, (m, i) => `<code>${codes[i]}</code>`);
  return t;
}

/**
 * Der Kleinstrenderer: Ueberschriften, Listen, Zitate, Code-Bloecke,
 * Trennlinien, Absaetze plus Inline-Markdown. Kein HTML geht unver-
 * wandelt durch -- alles kommt geflohen rein.
 */
function markdown(text) {
  if (!text) return "";
  const zeilen = fliehe(text).split(/\r?\n/);
  const stueck = [];
  let absatz = [];
  let modus = null; // null | "ul" | "ol" | "blockquote"
  let code = null;

  const absatz_schliessen = () => {
    if (absatz.length) {
      stueck.push(`<p>${inline_markdown(absatz.join(" "))}</p>`);
      absatz = [];
    }
  };
  const liste_schliessen = () => {
    if (modus) {
      stueck.push(`</${modus === "blockquote" ? "blockquote" : modus}>`);
      modus = null;
    }
  };

  for (const zeile of zeilen) {
    if (code !== null) {
      if (/^\s*```/.test(zeile)) {
        stueck.push(`<pre><code>${code.join("\n")}</code></pre>`);
        code = null;
      } else {
        code.push(zeile);
      }
      continue;
    }
    if (/^\s*```/.test(zeile)) {
      absatz_schliessen();
      liste_schliessen();
      code = [];
      continue;
    }
    const kopf = zeile.match(/^(#{1,4})\s+(.*)$/);
    if (kopf) {
      absatz_schliessen();
      liste_schliessen();
      stueck.push(
        `<h${kopf[1].length}>${inline_markdown(kopf[2].trim())}</h${kopf[1].length}>`
      );
      continue;
    }
    if (/^\s*(---+|\*\*\*+)\s*$/.test(zeile)) {
      absatz_schliessen();
      liste_schliessen();
      stueck.push("<hr>");
      continue;
    }
    const zitat = zeile.match(/^&gt;\s?(.*)$/);
    if (zitat) {
      absatz_schliessen();
      if (modus !== "blockquote") {
        liste_schliessen();
        stueck.push("<blockquote>");
        modus = "blockquote";
      }
      stueck.push(`<p>${inline_markdown(zitat[1])}</p>`);
      continue;
    }
    const unsortiert = zeile.match(/^\s*[-*+]\s+(.*)$/);
    if (unsortiert) {
      absatz_schliessen();
      if (modus !== "ul") {
        liste_schliessen();
        stueck.push("<ul>");
        modus = "ul";
      }
      stueck.push(`<li>${inline_markdown(unsortiert[1])}</li>`);
      continue;
    }
    const numeriert = zeile.match(/^\s*\d+[.)]\s+(.*)$/);
    if (numeriert) {
      absatz_schliessen();
      if (modus !== "ol") {
        liste_schliessen();
        stueck.push("<ol>");
        modus = "ol";
      }
      stueck.push(`<li>${inline_markdown(numeriert[1])}</li>`);
      continue;
    }
    liste_schliessen();
    if (!zeile.trim()) {
      absatz_schliessen();
    } else {
      absatz.push(zeile.trim());
    }
  }
  if (code !== null) {
    stueck.push(`<pre><code>${code.join("\n")}</code></pre>`);
  }
  liste_schliessen();
  absatz_schliessen();
  return stueck.join("\n");
}

/** Datumskurzform, falls ISO -- sonst unverandert. */
function datum_kurz(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString();
}

/** Kategorienamen -- der Server schickt sie mit, dies ist nur der Rueckfall. */
const KATEGORIEN = [
  "integration",
  "plugin",
  "theme",
  "template",
  "appdaemon",
  "python_script",
];

/** Die Abschnitte des Ladens, in dieser Reihenfolge. */
const ABSCHNITTE = ["aktualisierbar", "installierbar", "neu", "downloadbar"];

/**
 * Der Tanuki -- das Markenbild von GitLab, vier Pfade aus der Feder
 * des Imkers-Servers (dieselben Zahlen wie in iconset.js, dort nur
 * als Silhouette). Der Kopf zeichnet ihn farbig; die Seitenleiste
 * nimmt die einfarbige Schwester aus dem Iconset.
 */
const TANUKI_PFAD_KOERPER =
  "m49.014 19-.067-.18-6.784-17.696a1.792 1.792 0 0 0-3.389.182l-4.579 14.02H15.651l-4.58-14.02a1.795 1.795 0 0 0-3.388-.182l-6.78 17.7-.071.175A12.595 12.595 0 0 0 5.01 33.556l.026.02.057.044 10.32 7.734 5.12 3.87 3.11 2.351a2.102 2.102 0 0 0 2.535 0l3.11-2.352 5.12-3.869 10.394-7.779.029-.022a12.595 12.595 0 0 0 4.182-14.554Z";
const TANUKI_PFAD_WANGE_RECHTS =
  "m49.014 19-.067-.18a22.88 22.88 0 0 0-9.12 4.103L24.931 34.187l9.485 7.167 10.393-7.779.03-.022a12.595 12.595 0 0 0 4.175-14.554Z";
const TANUKI_PFAD_KINN =
  "m15.414 41.354 5.12 3.87 3.11 2.351a2.102 2.102 0 0 0 2.535 0l3.11-2.352 5.12-3.869-9.484-7.167-9.51 7.167Z";
const TANUKI_PFAD_WANGE_LINKS =
  "M10.019 22.923a22.86 22.86 0 0 0-9.117-4.1L.832 19A12.595 12.595 0 0 0 5.01 33.556l.026.02.057.044 10.32 7.734 9.491-7.167L10.02 22.923Z";

/** Der farbige Tanuki als fertiges SVG-Stueck (Groesse via CSS). */
function tanuki_svg(klassenname) {
  return (
    `<svg class="${klassenname}" viewBox="0 0 50 48" aria-hidden="true" focusable="false">` +
    `<path fill="#E24329" d="${TANUKI_PFAD_KOERPER}"/>` +
    `<path fill="#FC6D26" d="${TANUKI_PFAD_WANGE_RECHTS}"/>` +
    `<path fill="#FCA326" d="${TANUKI_PFAD_KINN}"/>` +
    `<path fill="#FC6D26" d="${TANUKI_PFAD_WANGE_LINKS}"/>` +
    `</svg>`
  );
}

/** Ein einfacher Strich-Chemawinkel (zuklappbare Abschnitte). */
const SPITZE_SVG =
  '<svg class="hl-spitze" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<path d="M5.5 3.5 11 8l-5.5 4.5" fill="none" stroke="currentColor" ' +
  'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

/** Lupe fuer die Suchzeile (GitLabs Werkzeug). */
const LUPE_SVG =
  '<svg class="hl-lupe" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<circle cx="7" cy="7" r="4.5" fill="none" stroke="currentColor" stroke-width="1.7"/>' +
  '<path d="m10.5 10.5 3.5 3.5" stroke="currentColor" stroke-width="1.7" ' +
  'stroke-linecap="round"/></svg>';

/** Der Kreislaufpfeil (Frischholen). */
const KREIS_SVG =
  '<svg class="hl-kreis" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<path d="M13.5 8a5.5 5.5 0 1 1-1.61-3.89" fill="none" stroke="currentColor" ' +
  'stroke-width="1.7" stroke-linecap="round"/><path d="M13.8 1.8v3h-3" fill="none" ' +
  'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
  'stroke-linejoin="round"/></svg>';

/** Das Plus (Neu hinzufuegen). */
const PLUS_SVG =
  '<svg class="hl-plus" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.7" ' +
  'stroke-linecap="round"/></svg>';

/** Warndreieck fuer die Instanz-Meldung. */
const WARN_SVG =
  '<svg class="hl-warn" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<path d="M8 2 15 14H1Z" fill="none" stroke="currentColor" stroke-width="1.5" ' +
  'stroke-linejoin="round"/><path d="M8 6.5v3.2" stroke="currentColor" ' +
  'stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="12" r="0.9" ' +
  'fill="currentColor"/></svg>';

/** Wie lange ein frischer Lauf ruht, bevor der Betritt ihn erneut erzwinge. */
const BETRETEN_RUHE_MS = 15000;

/** Die Klasse des Panels. */
class HacsLabPanel extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._suche = "";
    this._sort = "name";
    this._eintraege = [];
    this._instanzen = [];
    this._funde = null;
    this._kategorien = KATEGORIEN;
    this._scan_host = "";
    this._scan_gruppe = "";
    this._scan_untergruppen = true;
    this._scan_entwicklung = false;
    this._detail = null; // { host, pfad, daten }
    this._fehler = "";
    this._instanz_fehler = {}; // host -> Grund (aus dem frischen Lauf)
    this._beschaeftigt = false;
    this._erneuert_am = 0;
    this._offen = {
      aktualisierbar: true,
      installierbar: true,
      neu: true,
      downloadbar: false,
    };
  }

  set hass(hass) {
    const erste = this._hass === null;
    this._hass = hass;
    if (erste) {
      this._betrete();
    }
  }

  set panel(panel) {
    this._panel = panel;
  }

  set narrow(narrow) {
    this._narrow = narrow;
  }

  connectedCallback() {
    if (!this._gerendert) {
      this._zeichne();
    } else {
      // Jeder Betritt des Ladens frischt auf -- nicht nur der erste.
      this._betrete();
    }
  }

  get _t() {
    return TEXTE[sprache(this._hass)];
  }

  /** Der Betritt: frischer Lauf, es sei denn, er ruht eben noch. */
  _betrete() {
    if (!this._hass) {
      return;
    }
    if (this._erneuert_am && Date.now() - this._erneuert_am < BETRETEN_RUHE_MS) {
      return;
    }
    this._erneuern();
  }

  /** Fehler-Objekt (WebSocket oder Dienst) in Klartext. */
  _fehlertext(fehler) {
    const code = fehler && fehler.code;
    const t = this._t;
    if (code && t.fehler[code] !== undefined) {
      return t.fehler[code];
    }
    if (fehler && fehler.message) {
      return t.fehler.sonst + " (" + fehler.message + ")";
    }
    if (typeof fehler === "string" && fehler) {
      return t.fehler.sonst + " (" + fehler + ")";
    }
    return t.fehler.sonst;
  }

  /** Der frische Lauf: jeder Aktualisierer wird herumgedreht, dann Liste. */
  async _erneuern() {
    if (!this._hass || this._beschaeftigt) {
      return;
    }
    this._beschaeftigt = true;
    this._zeichne();
    try {
      const antwort = await this._hass.callWS({
        type: "hacs_lab/erneuern",
      });
      this._eintraege = antwort.eintraege || [];
      this._instanzen = antwort.instanzen || [];
      this._kategorien = antwort.kategorien || KATEGORIEN;
      this._instanz_fehler = antwort.gescheitert || {};
      if (!this._scan_host && this._instanzen.length) {
        this._scan_host = this._instanzen[0];
      }
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._erneuert_am = Date.now();
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Liste laden (installierte Eintraege + Instanzen) -- der schnelle Griff. */
  async _lade() {
    if (!this._hass) return;
    this._beschaeftigt = true;
    this._zeichne();
    try {
      const antwort = await this._hass.callWS({
        type: "hacs_lab/eintraege",
      });
      this._eintraege = antwort.eintraege || [];
      this._instanzen = antwort.instanzen || [];
      this._kategorien = antwort.kategorien || KATEGORIEN;
      if (!this._scan_host && this._instanzen.length) {
        this._scan_host = this._instanzen[0];
      }
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Entdeckung starten (Stufe M6: der Scan schreibt nichts). */
  async _scan() {
    this._beschaeftigt = true;
    this._zeichne();
    try {
      const antwort = await this._hass.callWS({
        type: "hacs_lab/entdecken",
        host: this._scan_host,
        gruppe: this._scan_gruppe,
        mit_untergruppen: this._scan_untergruppen,
        mit_entwicklung: this._scan_entwicklung,
      });
      this._funde = antwort.funde || [];
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Detailansicht holen: Stammdaten, README, Releases. */
  async _hole_detail(host, pfad) {
    this._beschaeftigt = true;
    this._zeichne();
    try {
      const daten = await this._hass.callWS({
        type: "hacs_lab/detail",
        host: host,
        pfad: pfad,
      });
      this._detail = { host: host, pfad: pfad, daten: daten };
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Aufnehmen -- derselbe Weg wie der Dialog, nur ohne Dialog. */
  async _hinzufuegen(host, pfad, kategorie) {
    this._beschaeftigt = true;
    this._zeichne();
    try {
      await this._hass.callWS({
        type: "hacs_lab/hinzufuegen",
        host: host,
        pfad: pfad,
        kategorie: kategorie,
      });
      this._fehler = "";
      await this._lade();
      if (this._funde) {
        const frisch = this._funde.map((f) =>
          f.full_name === pfad ? { ...f, vorhanden: true } : f
        );
        this._funde = frisch;
      }
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Entfernen -- mit Rueckfrage, Dateien bleiben (Stufe M4). */
  async _entfernen(eintrag) {
    const bestaetigt = window.confirm(
      this._t.entfernen_frage(eintrag.name)
    );
    if (!bestaetigt) {
      return;
    }
    this._beschaeftigt = true;
    this._zeichne();
    try {
      await this._hass.callWS({
        type: "hacs_lab/entfernen",
        storage_key: eintrag.storage_key,
      });
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    await this._lade();
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Deinstallieren -- Dateien weg, den verzeichneten Weg (Stufe M4b). */
  async _deinstallieren(eintrag) {
    const bestaetigt = window.confirm(
      this._t.deinstallieren_frage(eintrag.name)
    );
    if (!bestaetigt) {
      return;
    }
    this._beschaeftigt = true;
    this._zeichne();
    try {
      await this._hass.callWS({
        type: "hacs_lab/deinstallieren",
        storage_key: eintrag.storage_key,
      });
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    await this._lade();
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Installieren oder aktualisieren -- der Dienst der update-Entity. */
  async _installieren(eintrag) {
    if (!eintrag.entity_id) {
      this._fehler = this._t.fehler.sonst;
      this._zeichne();
      return;
    }
    this._beschaeftigt = true;
    this._zeichne();
    try {
      await this._hass.callService("update", "install", {
        entity_id: eintrag.entity_id,
      });
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    await this._lade();
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Suchnadel auf einer Zeile (Name, Beschreibung, Pfad). */
  _passt(zeile) {
    const nadel = this._suche.trim().toLowerCase();
    if (!nadel) {
      return true;
    }
    const heuhaufen = (
      (zeile.name || "") +
      " " +
      (zeile.beschreibung || "") +
      " " +
      (zeile.full_name || zeile.pfad || "")
    ).toLowerCase();
    return heuhaufen.includes(nadel);
  }

  /** Eine Liste nach der gewaehlten Sortierung ordnen. */
  _sortiere(liste) {
    const kopie = [...liste];
    kopie.sort((a, b) => {
      if (this._sort === "sterne") {
        return (
          (b.sterne || 0) - (a.sterne || 0) ||
          String(a.name).localeCompare(String(b.name))
        );
      }
      if (this._sort === "datum") {
        const da = a.veroeffentlicht_am || a.hinzugefuegt_am || "";
        const db = b.veroeffentlicht_am || b.hinzugefuegt_am || "";
        return (
          String(db).localeCompare(String(da)) ||
          String(a.name).localeCompare(String(b.name))
        );
      }
      return String(a.name).localeCompare(String(b.name));
    });
    return kopie;
  }

  /**
   * Die vier Abschnitte des Ladens -- jede Zeile genau einmal:
   * aktualisierbar (installiert, aber neueste weicht ab), installierbar
   * (beobachtet, nichts installiert), downloadbar (installiert und
   * oben), neu (Funde der Suche, noch nicht aufgenommen).
   */
  _gruppen() {
    const aktualisierbar = [];
    const installierbar = [];
    const downloadbar = [];
    for (const e of this._eintraege) {
      if (!this._passt(e)) {
        continue;
      }
      const update_da = e.neueste && e.installiert !== e.neueste;
      if (e.installiert && update_da) {
        aktualisierbar.push(e);
      } else if (!e.installiert) {
        installierbar.push(e);
      } else {
        downloadbar.push(e);
      }
    }
    const neu = (this._funde || []).filter((f) => this._passt(f));
    return {
      aktualisierbar: this._sortiere(aktualisierbar),
      installierbar: this._sortiere(installierbar),
      neu: this._sortiere(neu),
      downloadbar: this._sortiere(downloadbar),
    };
  }

  _zeichne() {
    this._gerendert = true;
    const inhalt = this._detail ? this._html_detail() : this._html_laden();
    this.innerHTML = `
      <style>${STIL}</style>
      <div class="hl-panel">
        ${this._html_balken()}
        <div class="hl-inhalt">
          ${this._fehler ? `<div class="hl-fehler">${fliehe(this._fehler)}</div>` : ""}
          ${inhalt}
        </div>
      </div>`;
    this._binden();
  }

  /** Der Balken oben -- GitLabs Leiste: Marke, Suche, Werkzeuge. */
  _html_balken() {
    const t = this._t;
    const updates = this._gruppen().aktualisierbar.length;
    const marke = `
      <div class="hl-marke">
        ${tanuki_svg("hl-tanuki")}
        <span class="hl-wort">${fliehe(t.titel)}</span>
        ${updates ? `<span class="hl-abzeichen">${fliehe(String(updates))}</span>` : ""}
      </div>`;
    if (this._detail) {
      const name =
        (this._detail.daten && this._detail.daten.info &&
          this._detail.daten.info.name) ||
        this._detail.pfad;
      // Brotkrumen wie im Imker-Server: Marke, Trenner, Projektname.
      return `
      <div class="hl-balken">
        <div class="hl-brotkrumen">
          <button class="hl-ikonknopf" data-aktion="zurueck" title="${fliehe(t.zurueck)}">
            ${'<svg class="hl-spitze-links" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M10.5 3.5 5 8l5.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'}
          </button>
          ${marke}
          <span class="hl-trenner">/</span>
          <span class="hl-brotkrume">${fliehe(name)}</span>
        </div>
        <span class="hl-abstand"></span>
      </div>`;
    }
    return `
      <div class="hl-balken">
        ${marke}
        <div class="hl-suchfeld">
          ${LUPE_SVG}
          <input class="hl-suche" type="search" placeholder="${fliehe(t.suche)}"
                 value="${fliehe(this._suche)}" data-rolle="suche"
                 aria-label="${fliehe(t.suche)}">
        </div>
        <div class="hl-werkzeuge">
          <button class="hl-ikonknopf" data-aktion="aktualisieren" title="${fliehe(t.aktualisieren)}"
                  aria-label="${fliehe(t.aktualisieren)}" ${this._beschaeftigt ? "disabled" : ""}>${KREIS_SVG}</button>
          <button class="hl-ikonknopf" data-aktion="neu" title="${fliehe(t.neu_knopf)}"
                  aria-label="${fliehe(t.neu_knopf)}">${PLUS_SVG}</button>
        </div>
      </div>`;
  }

  /** Der Laden: Werkzeugleiste, Instanz-Meldung, Abschnitte. */
  _html_laden() {
    const t = this._t;
    if (!this._instanzen.length) {
      return `<div class="hl-hinweis">${fliehe(t.instanzen_leer)}</div>`;
    }
    const gruppen = this._gruppen();
    const gesamt =
      gruppen.aktualisierbar.length +
      gruppen.installierbar.length +
      gruppen.downloadbar.length;
    const werkzeug = `
      <div class="hl-werkzeug">
        <label class="hl-sortierung">
          <span class="hl-sortwort">${fliehe(t.sortierung)}</span>
          <select class="hl-sort" data-rolle="sort">
            <option value="name" ${this._sort === "name" ? "selected" : ""}>${fliehe(t.sort.name)}</option>
            <option value="sterne" ${this._sort === "sterne" ? "selected" : ""}>${fliehe(t.sort.sterne)}</option>
            <option value="datum" ${this._sort === "datum" ? "selected" : ""}>${fliehe(t.sort.datum)}</option>
          </select>
        </label>
        <span class="hl-zaehler-zeile">${fliehe(t.anzahl(gesamt))}${this._beschaeftigt ? ` · ${fliehe(t.frisch_laeuft)}` : ""}</span>
      </div>`;
    const meldung = Object.keys(this._instanz_fehler).length
      ? `<div class="hl-banner">${WARN_SVG}<span>${fliehe(
          Object.entries(this._instanz_fehler)
            .map(([host, grund]) => `${host}: ${grund}`)
            .join(" · ")
        )}</span></div>`
      : "";
    return `${werkzeug}${meldung}${ABSCHNITTE.map((schlussel) =>
      this._html_abschnitt(schlussel, gruppen[schlussel])
    ).join("")}`;
  }

  /** Ein einklappbarer Abschnitt mit Kopf, Zaehler und Karten. */
  _html_abschnitt(schlussel, zeilen) {
    const t = this._t;
    const offen = !!this._offen[schlussel];
    const karten =
      schlussel === "neu"
        ? zeilen.map((f) => this._html_zeile_fund(f)).join("")
        : zeilen.map((e) => this._html_zeile_eintrag(e)).join("");
    const scan_form = schlussel === "neu" ? this._html_scan() : "";
    const leer = karten
      ? ""
      : `<div class="hl-abschnitt-leer">${fliehe(t.abschnitte_leer[schlussel])}</div>`;
    return `
      <section class="hl-abschnitt" data-abschnitt="${schlussel}">
        <button class="hl-abschnitt-kopf" data-rolle="abschnitt" data-abschnitt="${schlussel}"
                aria-expanded="${offen}">
          ${SPITZE_SVG}
          <span class="hl-abschnitt-titel">${fliehe(t.abschnitte[schlussel])}</span>
          <span class="hl-abschnitt-text">${fliehe(t.abschnittstexte[schlussel])}</span>
          <span class="hl-zaehler ${schlussel === "aktualisierbar" ? "hl-zaehler-heiss" : ""}">${fliehe(String(zeilen.length))}</span>
        </button>
        ${offen ? `<div class="hl-abschnitt-koerper">${scan_form}${karten}${leer}</div>` : ""}
      </section>`;
  }

  /** Die Suchleiste fuer die Entdeckung -- im Abschnitt Neu zu Hause. */
  _html_scan() {
    const t = this._t;
    return `
      <div class="hl-scan">
        <label>${fliehe(t.quelle)}
          <select data-rolle="scan-host">
            ${this._instanzen
              .map(
                (h) =>
                  `<option value="${fliehe(h)}" ${this._scan_host === h ? "selected" : ""}>${fliehe(h)}</option>`
              )
              .join("")}
          </select>
        </label>
        <label class="hl-gruppe">${fliehe(t.gruppe)}
          <input type="text" value="${fliehe(this._scan_gruppe)}" data-rolle="scan-gruppe" placeholder="gruppe/untergruppe">
        </label>
        <label class="hl-häkchen"><input type="checkbox" data-rolle="scan-untergruppen" ${this._scan_untergruppen ? "checked" : ""}> ${fliehe(t.untergruppen)}</label>
        <label class="hl-häkchen"><input type="checkbox" data-rolle="scan-entwicklung" ${this._scan_entwicklung ? "checked" : ""}> ${fliehe(t.entwicklung)}</label>
        <button class="hl-knopf hl-primaer" data-aktion="scan" ${this._beschaeftigt ? "disabled" : ""}>${fliehe(this._beschaeftigt ? t.scan_laeuft : t.scan)}</button>
      </div>`;
  }

  _html_zeile_eintrag(e) {
    const t = this._t;
    const update_da = e.neueste && e.installiert !== e.neueste;
    const versionszeile = `
      <span class="hl-version ${update_da ? "frisch" : ""}">
        ${fliehe(e.installiert || "—")} ${fliehe(t.installiert_label)}
        · ${fliehe(e.neueste || "—")} ${fliehe(t.neueste_label)}
      </span>`;
    return `
      <div class="hl-karte">
        <div class="hl-karte-haupt">
          <div class="hl-karte-kopf" data-aktion="details" data-host="${fliehe(e.host)}" data-pfad="${fliehe(e.pfad)}" title="${fliehe(t.details)}">
            <span class="hl-name">${fliehe(e.name)}</span>
            <span class="hl-kategorie">${fliehe(e.kategorie)}</span>
          </div>
          <div class="hl-unterzeile">
            ${versionszeile}
            <span class="hl-zahlen">
              ${e.sterne !== undefined ? `<span title="${fliehe(String(e.sterne))} ${fliehe(e.sterne === 1 ? t.sterne_ein : t.sterne_viele)}"><ha-icon icon="mdi:star-outline"></ha-icon> ${fliehe(String(e.sterne))}</span>` : ""}
              ${e.offene_tickets !== undefined ? `<span title="${fliehe(t.tickets)}"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(e.offene_tickets))}</span>` : ""}
            </span>
          </div>
          ${e.beschreibung ? `<div class="hl-beschreibung">${fliehe(e.beschreibung)}</div>` : ""}
          ${e.fehler ? `<div class="hl-klein-fehler">${fliehe(e.fehler)}</div>` : ""}
        </div>
        <div class="hl-knöpfe">
          ${
            e.installiert && update_da && e.entity_id
              ? `<button class="hl-knopf hl-primaer" data-aktion="install" data-key="${fliehe(e.storage_key)}">${fliehe(t.update_install)}</button>`
              : ""
          }
          ${
            !e.installiert && e.neueste && e.entity_id
              ? `<button class="hl-knopf hl-primaer" data-aktion="install" data-key="${fliehe(e.storage_key)}">${fliehe(t.installieren)}</button>`
              : ""
          }
          ${
            e.installiert
              ? `<button class="hl-knopf hl-gefahr" data-aktion="deinstallieren" title="${fliehe(t.deinstalliert_hinweis)}" data-key="${fliehe(e.storage_key)}">${fliehe(t.deinstallieren)}</button>`
              : ""
          }
          <button class="hl-knopf" data-aktion="entfernen" title="${fliehe(t.entfernt_hinweis)}" data-key="${fliehe(e.storage_key)}">${fliehe(t.entfernen)}</button>
        </div>
      </div>`;
  }

  _html_zeile_fund(f) {
    const t = this._t;
    return `
      <div class="hl-karte ${f.vorhanden ? "schon-da" : ""}">
        <div class="hl-karte-haupt">
          <div class="hl-karte-kopf" data-aktion="details" data-host="${fliehe(this._scan_host)}" data-pfad="${fliehe(f.full_name)}" title="${fliehe(t.details)}">
            <span class="hl-name">${fliehe(f.name)}</span>
            <span class="hl-kategorie">${fliehe(f.kategorie)}</span>
          </div>
          <div class="hl-unterzeile">
            <span class="hl-version">${fliehe(f.letzte_version || "—")}</span>
            <span class="hl-zahlen">
              <span title="${fliehe(String(f.sterne))} ${fliehe(f.sterne === 1 ? t.sterne_ein : t.sterne_viele)}"><ha-icon icon="mdi:star-outline"></ha-icon> ${fliehe(String(f.sterne))}</span>
              <span title="${fliehe(t.tickets)}"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(f.offene_tickets))}</span>
            </span>
          </div>
          ${f.beschreibung ? `<div class="hl-beschreibung">${fliehe(f.beschreibung)}</div>` : ""}
          ${!f.gueltig && f.fehler ? `<div class="hl-klein-fehler">${fliehe(f.fehler)}</div>` : ""}
        </div>
        <div class="hl-knöpfe">
          ${
            f.vorhanden
              ? `<span class="hl-schon-da">${fliehe(this._t.schon_da)}</span>`
              : f.gueltig
                ? `<label class="hl-kategorie-wahl">${fliehe(t.kategorie)}
                     <select data-rolle="kategorie" data-pfad="${fliehe(f.full_name)}">
                       ${(this._kategorien || KATEGORIEN).map(
                         (k) =>
                           `<option value="${k}" ${k === f.kategorie ? "selected" : ""}>${k}</option>`
                       ).join("")}
                     </select>
                   </label>
                   <button class="hl-knopf hl-primaer" data-aktion="hinzufuegen" data-host="${fliehe(this._scan_host)}" data-pfad="${fliehe(f.full_name)}" ${this._beschaeftigt ? "disabled" : ""}>${fliehe(t.hinzufuegen)}</button>`
                : `<span class="hl-schon-da">✗</span>`
          }
        </div>
      </div>`;
  }

  _html_detail() {
    const t = this._t;
    const d = this._detail.daten;
    const info = d.info || {};
    const sterne_wort =
      (info.sterne || 0) === 1 ? t.sterne_ein : t.sterne_viele;
    const verweise = [
      info.web_url ? `<a href="${fliehe(info.web_url)}" target="_blank" rel="noopener noreferrer">${fliehe(t.repository)}</a>` : "",
      info.tickets_url ? `<a href="${fliehe(info.tickets_url)}" target="_blank" rel="noopener noreferrer">${fliehe(t.tickets)}</a>` : "",
      info.releases_url ? `<a href="${fliehe(info.releases_url)}" target="_blank" rel="noopener noreferrer">${fliehe(t.releases_link)}</a>` : "",
    ]
      .filter(Boolean)
      .join("");
    const readme = d.readme
      ? `<div class="hl-datei">
           <div class="hl-datei-kopf">${fliehe(d.readme_datei || t.readme)}</div>
           <div class="hl-readme">${markdown(d.readme)}</div>
         </div>`
      : `<div class="hl-hinweis">${fliehe(t.readme_fehlt)}</div>`;
    const releases = (d.releases || []).length
      ? `<h2>${fliehe(t.releases)}</h2>
         <div class="hl-releases">
           ${(d.releases || [])
             .map(
               (r) => `
             <div class="hl-release">
               <div class="hl-release-kopf">
                 <span class="hl-release-tag">${fliehe(r.tag)}</span>
                 ${r.vorabversion ? `<span class="hl-vorab">${fliehe(t.vorab)}</span>` : ""}
                 <span class="hl-release-datum">${fliehe(datum_kurz(r.veroeffentlicht_am))}</span>
               </div>
               ${r.name ? `<div class="hl-release-name">${fliehe(r.name)}</div>` : ""}
               ${r.beschreibung ? `<div class="hl-release-notizen">${markdown(r.beschreibung)}</div>` : ""}
             </div>`
             )
             .join("")}
         </div>`
      : `<h2>${fliehe(t.releases)}</h2><div class="hl-hinweis">${fliehe(t.keine_releases)}</div>`;
    return `
      <div class="hl-detail">
        <div class="hl-karte">
          <div class="hl-karte-kopf">
            <span class="hl-name">${fliehe(info.name || info.full_name)}</span>
          </div>
          ${info.beschreibung ? `<div class="hl-beschreibung">${fliehe(info.beschreibung)}</div>` : ""}
          <div class="hl-unterzeile">
            <span class="hl-zahlen">
              <span title="${fliehe(String(info.sterne))} ${fliehe(sterne_wort)}"><ha-icon icon="mdi:star-outline"></ha-icon> ${fliehe(String(info.sterne))}</span>
              <span title="${fliehe(t.tickets)}"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(info.offene_tickets))}</span>
            </span>
            ${info.archiviert ? `<span class="hl-vorab">⚠</span>` : ""}
          </div>
          ${verweise ? `<div class="hl-verweise">${verweise}</div>` : ""}
        </div>
        ${readme}
        ${releases}
      </div>`;
  }

  /** Ereignisse anknuepfen -- nach jedem Zeichnen frisch. */
  _binden() {
    const wurzel = this;
    const $ = (sel) => wurzel.querySelector(sel);
    const $$ = (sel) => Array.from(wurzel.querySelectorAll(sel));

    // Karten-Koepfe sind keine Buttons -- jeder Traeger mit data-aktion hoert zu.
    for (const knopf of $$('[data-aktion]')) {
      knopf.addEventListener("click", () => {
        const aktion = knopf.dataset.aktion;
        const eintrag = this._eintraege.find((e) => e.storage_key === knopf.dataset.key);
        if (aktion === "aktualisieren") {
          this._erneuern();
        } else if (aktion === "neu") {
          // Der Plus-Knopf oeffnet den Abschnitt Neu und geht dorthin.
          this._offen.neu = true;
          this._zeichne();
          const ziel = $('section[data-abschnitt="neu"]');
          if (ziel) {
            ziel.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        } else if (aktion === "zurueck") {
          this._detail = null;
          this._zeichne();
        } else if (aktion === "scan") {
          this._scan();
        } else if (aktion === "details") {
          this._hole_detail(knopf.dataset.host, knopf.dataset.pfad);
        } else if (aktion === "install" && eintrag) {
          this._installieren(eintrag);
        } else if (aktion === "entfernen" && eintrag) {
          this._entfernen(eintrag);
        } else if (aktion === "deinstallieren" && eintrag) {
          this._deinstallieren(eintrag);
        } else if (aktion === "hinzufuegen") {
          const wahl = wurzel.querySelector(
            `select[data-rolle="kategorie"][data-pfad="${CSS.escape(knopf.dataset.pfad)}"]`
          );
          const kategorie = wahl ? wahl.value : "integration";
          this._hinzufuegen(knopf.dataset.host, knopf.dataset.pfad, kategorie);
        }
      });
    }

    // Einklappbare Abschnitte: der Kopf dreht die Spitze.
    for (const kopf of $$('[data-rolle="abschnitt"]')) {
      kopf.addEventListener("click", () => {
        const schlussel = kopf.dataset.abschnitt;
        this._offen[schlussel] = !this._offen[schlussel];
        this._zeichne();
      });
    }

    const suche = $('input[data-rolle="suche"]');
    if (suche) {
      suche.addEventListener("input", () => {
        this._suche = suche.value;
        const vorher = document.activeElement;
        this._zeichne();
        const frisch = $('input[data-rolle="suche"]');
        if (frisch && vorher === suche) {
          frisch.focus();
          frisch.setSelectionRange(frisch.value.length, frisch.value.length);
        }
      });
    }

    const sort = $('select[data-rolle="sort"]');
    if (sort) {
      sort.addEventListener("change", () => {
        this._sort = sort.value;
        this._zeichne();
      });
    }

    const scan_host = $('select[data-rolle="scan-host"]');
    if (scan_host) {
      scan_host.addEventListener("change", () => {
        this._scan_host = scan_host.value;
      });
    }
    const scan_gruppe = $('input[data-rolle="scan-gruppe"]');
    if (scan_gruppe) {
      scan_gruppe.addEventListener("input", () => {
        this._scan_gruppe = scan_gruppe.value;
      });
    }
    const scan_unter = $('input[data-rolle="scan-untergruppen"]');
    if (scan_unter) {
      scan_unter.addEventListener("change", () => {
        this._scan_untergruppen = scan_unter.checked;
      });
    }
    const scan_entw = $('input[data-rolle="scan-entwicklung"]');
    if (scan_entw) {
      scan_entw.addEventListener("change", () => {
        this._scan_entwicklung = scan_entw.checked;
      });
    }
  }
}

const STIL = `
:host { display: block; }
.hl-panel { --hl-orange: #fc6d26; --hl-rot: #e24329; --hl-gold: #fca326;
  --hl-lila: #6b4fbb; --hl-gefahr: #d64541; --hl-balken: #333238;
  color: var(--primary-text-color); font-size: 14px; }

/* -- GitLabs Leiste: dunkel, Marke links, Suche Mitte, Werkzeuge rechts */
.hl-balken { display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  background: var(--hl-balken); color: #dcdcdc; padding: 9px 16px; }
.hl-marke { display: flex; align-items: center; gap: 8px; }
.hl-tanuki { height: 28px; width: auto; flex: 0 0 auto; }
.hl-wort { font-size: 15px; font-weight: 600; color: #fff; letter-spacing: .2px; }
.hl-abzeichen { background: var(--hl-orange); color: #fff; border-radius: 999px;
  font-size: 11.5px; font-weight: 600; padding: 1px 7px; line-height: 1.5; }
.hl-brotkrumen { display: flex; align-items: center; gap: 10px; min-width: 0; }
.hl-trenner { opacity: .45; }
.hl-brotkrume { font-size: 14.5px; font-weight: 600; color: #fff;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hl-spitze-links { width: 14px; height: 14px; }
.hl-suchfeld { flex: 1 1 300px; max-width: 620px; display: flex;
  align-items: center; gap: 8px; background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .18); border-radius: 4px;
  padding: 0 10px; height: 34px; color: #b9b9b9; }
.hl-suchfeld:focus-within { border-color: rgba(255, 255, 255, .4); }
.hl-lupe { width: 14px; height: 14px; flex: 0 0 auto; }
.hl-suche { flex: 1; background: none; border: none; outline: none;
  color: #f0f0f0; font: inherit; height: 100%; }
.hl-suche::placeholder { color: #8e8e93; }
.hl-werkzeuge { display: flex; gap: 4px; margin-left: auto; }
.hl-ikonknopf { display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border: none; border-radius: 4px; background: none;
  color: #dcdcdc; cursor: pointer; padding: 0; }
.hl-ikonknopf:hover { background: rgba(255, 255, 255, .12); color: #fff; }
.hl-ikonknopf[disabled] { opacity: .55; cursor: default; }
.hl-ikonknopf svg { width: 17px; height: 17px; }
.hl-ikonknopf[disabled] .hl-kreis { animation: hl-drehen .9s linear infinite; }
@keyframes hl-drehen { to { transform: rotate(360deg); } }

/* -- Der Laden darunter */
.hl-inhalt { max-width: 1000px; margin: 0 auto; padding: 12px 16px 48px; }
.hl-fehler { background: var(--error-color, #db4437); color: #fff;
  border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 14px; }
.hl-banner { display: flex; gap: 10px; align-items: flex-start;
  background: rgba(252, 163, 38, .14); border: 1px solid rgba(252, 163, 38, .55);
  border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 13.5px;
  color: var(--primary-text-color); }
.hl-warn { width: 15px; height: 15px; color: var(--hl-gold);
  flex: 0 0 auto; margin-top: 1px; }
.hl-hinweis { opacity: .7; padding: 24px 0; text-align: center; font-size: 14px; }
.hl-werkzeug { display: flex; align-items: center; gap: 12px; padding: 4px 0 12px;
  flex-wrap: wrap; }
.hl-sortierung { display: flex; align-items: center; gap: 8px;
  color: var(--secondary-text-color); font-size: 13px; }
.hl-sort { border: 1px solid rgba(127, 127, 127, .4); border-radius: 4px;
  background: var(--card-background-color, #fff); color: var(--primary-text-color);
  padding: 6px 8px; font: inherit; font-size: 13px; }
.hl-zaehler-zeile { margin-left: auto; color: var(--secondary-text-color);
  font-size: 12.5px; }

/* -- Einklappbare Abschnitte */
.hl-abschnitt { border-bottom: 1px solid rgba(127, 127, 127, .25); }
.hl-abschnitt-kopf { display: flex; align-items: baseline; gap: 10px; width: 100%;
  background: none; border: none; color: var(--primary-text-color); cursor: pointer;
  padding: 12px 4px; font-family: inherit; text-align: left; }
.hl-spitze { width: 12px; height: 12px; flex: 0 0 auto; align-self: center;
  transition: transform .12s ease; color: var(--secondary-text-color); }
.hl-abschnitt-kopf[aria-expanded="true"] .hl-spitze { transform: rotate(90deg); }
.hl-abschnitt-titel { font-size: 15px; font-weight: 600; flex: 0 0 auto; }
.hl-abschnitt-text { font-size: 12.5px; color: var(--secondary-text-color);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hl-zaehler { margin-left: auto; font-size: 12px; font-weight: 500;
  background: rgba(127, 127, 127, .18); border-radius: 999px; padding: 1px 9px;
  color: var(--secondary-text-color); align-self: center; flex: 0 0 auto; }
.hl-zaehler.hl-zaehler-heiss { background: var(--hl-orange); color: #fff; }
.hl-abschnitt-koerper { padding: 2px 0 16px 18px; }
.hl-abschnitt-leer { opacity: .65; padding: 10px 0; font-size: 13.5px; }

/* -- Die Suche der Entdeckung (Abschnitt Neu) */
.hl-scan { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center;
  padding: 10px 12px; margin-bottom: 12px; border: 1px dashed rgba(127, 127, 127, .4);
  border-radius: 4px; font-size: 13px; }
.hl-scan label { display: flex; align-items: center; gap: 6px;
  color: var(--secondary-text-color); }
.hl-scan input[type="text"], .hl-scan select {
  border: 1px solid rgba(127, 127, 127, .4); border-radius: 4px;
  background: var(--card-background-color, #fff); padding: 6px 8px; font: inherit;
  font-size: 13px; color: var(--primary-text-color); }
.hl-gruppe input { width: 220px; }
.hl-häkchen { cursor: pointer; }

/* -- Karten: GitLaws Zeilen -- kompakt, Rand statt Schatten */
.hl-karte { display: flex; gap: 12px; background: var(--card-background-color, #fff);
  border: 1px solid rgba(127, 127, 127, .35); border-radius: 4px;
  padding: 12px 14px; margin-bottom: 8px; flex-wrap: wrap; }
.hl-karte:hover { border-color: rgba(127, 127, 127, .6); }
.hl-karte.schon-da { opacity: .55; }
.hl-karte-haupt { flex: 1 1 340px; min-width: 0; }
.hl-karte-kopf { display: flex; align-items: baseline; gap: 10px; cursor: pointer; }
.hl-name { font-size: 15px; font-weight: 600; color: var(--hl-lila);
  word-break: break-all; }
.hl-karte-kopf:hover .hl-name { text-decoration: underline; }
.hl-kategorie { font-size: 11.5px; color: var(--secondary-text-color);
  border: 1px solid rgba(127, 127, 127, .4); border-radius: 999px; padding: 1px 9px;
  flex: 0 0 auto; }
.hl-unterzeile { display: flex; align-items: center; gap: 12px; padding-top: 6px;
  font-size: 13px; color: var(--secondary-text-color); flex-wrap: wrap; }
.hl-version.frisch { color: var(--hl-orange); font-weight: 600; }
.hl-zahlen { display: flex; gap: 12px; margin-left: auto; align-items: center; }
.hl-beschreibung { font-size: 13px; color: var(--secondary-text-color);
  padding-top: 6px; }
.hl-klein-fehler { font-size: 12px; color: var(--error-color, #db4437);
  padding-top: 6px; }
.hl-knöpfe { display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
  justify-content: flex-end; flex: 0 0 auto; margin-left: auto; }

/* -- Knöpfe: GitLaws vier Ecken, Orange fuer das Vorhaben */
.hl-knopf { background: var(--card-background-color, #fff);
  border: 1px solid rgba(127, 127, 127, .5); border-radius: 4px; padding: 6px 13px;
  font-size: 13.5px; font-weight: 500; cursor: pointer;
  color: var(--primary-text-color); font-family: inherit; line-height: 1.4; }
.hl-knopf:hover { background: rgba(127, 127, 127, .12); }
.hl-knopf[disabled] { opacity: .5; cursor: default; }
.hl-knopf.hl-primaer { background: var(--hl-orange); border-color: var(--hl-orange);
  color: #fff; }
.hl-knopf.hl-primaer:hover { background: var(--hl-rot); border-color: var(--hl-rot); }
.hl-knopf.hl-gefahr { background: none; border-color: rgba(214, 69, 65, .6);
  color: var(--error-color, #d64541); }
.hl-knopf.hl-gefahr:hover { background: rgba(214, 69, 65, .12); }
.hl-kategorie-wahl { display: flex; align-items: center; gap: 6px; font-size: 13px;
  color: var(--secondary-text-color); }
.hl-kategorie-wahl select { border: 1px solid rgba(127, 127, 127, .4);
  border-radius: 4px; background: var(--card-background-color, #fff);
  padding: 6px 8px; font: inherit; font-size: 13px;
  color: var(--primary-text-color); }
.hl-schon-da { font-size: 13px; color: var(--secondary-text-color); }

/* -- Das Detail: Karte, Datei-Rahmen fuer die Beschreibung, Releases */
.hl-detail .hl-beschreibung { font-size: 14px; }
.hl-verweise { display: flex; gap: 14px; padding: 10px 0 2px; flex-wrap: wrap; }
.hl-verweise a { color: var(--hl-lila); text-decoration: none; font-size: 14px;
  font-weight: 500; }
.hl-verweise a:hover { text-decoration: underline; }
.hl-datei { border: 1px solid rgba(127, 127, 127, .35); border-radius: 4px;
  margin: 16px 0; overflow: hidden; background: var(--card-background-color, #fff); }
.hl-datei-kopf { background: rgba(127, 127, 127, .12); padding: 10px 14px;
  font-size: 12.5px; font-weight: 600; color: var(--secondary-text-color);
  border-bottom: 1px solid rgba(127, 127, 127, .35);
  font-family: var(--code-font-family, monospace); }
.hl-readme { padding: 16px; font-size: 14px; line-height: 1.55; }
.hl-readme img { max-width: 100%; border-radius: 4px; }
.hl-readme pre { background: rgba(127, 127, 127, .12); padding: 12px;
  border-radius: 4px; overflow-x: auto; }
.hl-readme code { font-family: var(--code-font-family, monospace); font-size: 13px; }
.hl-readme blockquote { border-left: 3px solid var(--hl-lila); margin: 8px 0;
  padding: 4px 12px; opacity: .85; }
.hl-readme a { color: var(--hl-lila); }
.hl-releases .hl-release { background: var(--card-background-color, #fff);
  border: 1px solid rgba(127, 127, 127, .35); border-radius: 4px;
  padding: 12px 16px; margin-bottom: 8px; }
.hl-release-kopf { display: flex; align-items: baseline; gap: 10px; }
.hl-release-tag { font-weight: 600; font-size: 14.5px;
  background: rgba(107, 79, 187, .12); color: var(--hl-lila); border-radius: 4px;
  padding: 1px 8px; }
.hl-release-datum { margin-left: auto; font-size: 12px;
  color: var(--secondary-text-color); }
.hl-vorab { font-size: 11px; border: 1px solid rgba(127, 127, 127, .4);
  border-radius: 999px; padding: 1px 8px; color: var(--secondary-text-color); }
.hl-release-name { font-size: 13.5px; padding-top: 4px; }
.hl-release-notizen { font-size: 13px; padding-top: 6px; line-height: 1.45; }
.hl-readme h1, .hl-detail h2 { font-size: 18px; font-weight: 600; }
.hl-readme h2 { font-size: 16px; }
h2 { font-size: 16px; font-weight: 600; padding: 12px 0 8px; }
`;

/**
 * Derselbe Tanuki auch fuer die Seitenleiste: als einfarbige Silhouette
 * ueber die eigene Kollektion ``hacs-lab`` (denselben Dienst leistet
 * iconset.js auf JEDER Seite -- das hier ist der Rueckhalt, falls jene
 * Anmeldung nicht griff). Das Frontend fragt die Kollektionen ab, sobald
 * es ein Zeichen zeichnen soll; angemeldet darf das mehrfach sein.
 */
window.customIconsets = window.customIconsets || {};
window.customIconsets["hacs-lab"] = (name) =>
  name === "tanuki"
    ? { path: TANUKI_PFAD_KOERPER, viewBox: "0 0 50 48" }
    : null;

customElements.define("hacs-lab-panel", HacsLabPanel);
