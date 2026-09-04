/**
 * HACS*lab Panel -- Stufe M7: Bedienung wie im Laden, nur eben mit *lab.
 *
 * Bewusst ohne Bausatz: eine Datei, vanilles JavaScript als ES-Modul,
 * geladen ueber ``/hacs_lab/panel.js``. Das Frontend von Home
 * Assistant findet hier das Element ``hacs-lab-panel`` und setzt ihm
 * ``hass`` und ``panel``. Alles weitere laufen die WebSocket-Befehle
 * aus ``websocket_api.py`` und die ganz normalen Dienste (install
 * auf den update-Entities aus Stufe M5).
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
    tabs: { installiert: "Installiert", verfuegbar: "Verfügbar" },
    suche: "Suchen (Name, Beschreibung)…",
    sortierung: "Sortierung",
    sort: { name: "Name", sterne: "Sterne", datum: "Datum" },
    aktualisieren: "Liste aktualisieren",
    scan: "Suchen",
    quelle: "Quelle",
    gruppe: "Gruppe (leer = ganze Instanz)",
    untergruppen: "mit Untergruppen",
    entwicklung: "auch hacs-development",
    hinzufuegen: "Hinzufügen",
    entfernen: "Entfernen",
    installieren: "Installieren",
    update_install: "Aktualisieren",
    details: "Details",
    zurueck: "Zurück",
    leer: "Noch nichts hier — füge ein Repository hinzu oder starte die Entdeckung.",
    keine_funde: "Keine Treffer.",
    instanzen_leer: "Keine Instanz eingerichtet — zuerst eine Instanz anlegen.",
    installiert_label: "installiert",
    neueste_label: "neueste",
    vorab: "Vorabversion",
    readme_fehlt: "Dieses Projekt hat keine lesbare Beschreibung.",
    releases: "Releases",
    keine_releases: "Keine Releases — Tags zählen als Fallback.",
    repository: "Repository",
    tickets: "Tickets",
    releases_link: "Releases",
    sterne_ein: "Stern",
    sterne_viele: "Sterne",
    kategorie: "Kategorie",
    entfernt_hinweis: "Nur die Beobachtung — Dateien bleiben liegen (Stufe M4).",
    entfernen_frage: (name) =>
      `${name} entfernen? Installierte Dateien bleiben liegen.`,
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
  },
  en: {
    titel: "HACS*lab",
    tabs: { installiert: "Installed", verfuegbar: "Available" },
    suche: "Search (name, description)…",
    sortierung: "Sort by",
    sort: { name: "Name", sterne: "Stars", datum: "Date" },
    aktualisieren: "Refresh list",
    scan: "Scan",
    quelle: "Source",
    gruppe: "Group (empty = whole instance)",
    untergruppen: "include subgroups",
    entwicklung: "include hacs-development",
    hinzufuegen: "Add",
    entfernen: "Remove",
    installieren: "Install",
    update_install: "Update",
    details: "Details",
    zurueck: "Back",
    leer: "Nothing here yet — add a repository or run discovery.",
    keine_funde: "No results.",
    instanzen_leer: "No instance configured — set one up first.",
    installiert_label: "installed",
    neueste_label: "latest",
    vorab: "pre-release",
    readme_fehlt: "This project has no readable description.",
    releases: "Releases",
    keine_releases: "No releases — tags count as fallback.",
    repository: "Repository",
    tickets: "Tickets",
    releases_link: "Releases",
    sterne_ein: "star",
    sterne_viele: "stars",
    kategorie: "Category",
    entfernt_hinweis: "Only the watch — files stay in place (M4).",
    entfernen_frage: (name) => `Remove ${name}? Installed files stay in place.`,
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

/** Kategorienamen -- der Server schickt sie mit, dies ist nur der Rückfall. */
const KATEGORIEN = [
  "integration",
  "plugin",
  "theme",
  "template",
  "appdaemon",
  "python_script",
];

/** Die Klasse des Panels. */
class HacsLabPanel extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._tab = "installiert";
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
    this._beschaeftigt = false;
  }

  set hass(hass) {
    const erste = this._hass === null;
    this._hass = hass;
    if (erste) {
      this._lade();
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
    }
  }

  get _t() {
    return TEXTE[sprache(this._hass)];
  }

  /** Fehler-Objekt (WebSocket oder Dienst) in Klartext. */
  _fehlertext(fehler) {
    const code = fehler && fehler.code;
    const t = this._t;
    if (code && t.fehler[code] !== undefined) {
      return t.fehler[code];
    }
    if (fehler && fehler.message && !code) {
      return t.fehler.sonst + " (" + fehler.message + ")";
    }
    if (typeof fehler === "string" && fehler) {
      return t.fehler.sonst + " (" + fehler + ")";
    }
    return t.fehler.sonst;
  }

  /** Liste laden (installierte Eintraege + Instanzen). */
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

  /** Sichtbare Zeilen nach Suche und Sortierung. */
  _sichtbar() {
    const nadel = this._suche.trim().toLowerCase();
    const quelle =
      this._tab === "installiert"
        ? this._eintraege.map((e) => ({
            ...e,
            _datum: e.veroeffentlicht_am || e.hinzugefuegt_am || "",
          }))
        : (this._funde || []).map((f) => ({ ...f, _datum: "" }));
    const gefiltert = quelle.filter((z) => {
      if (!nadel) return true;
      const heuhaufen = (
        (z.name || "") +
        " " +
        (z.beschreibung || "") +
        " " +
        (z.full_name || z.pfad || "")
      ).toLowerCase();
      return heuhaufen.includes(nadel);
    });
    const richtung = this._tab === "installiert" ? 1 : 1;
    gefiltert.sort((a, b) => {
      if (this._sort === "sterne") {
        return (b.sterne || 0) - (a.sterne || 0) || String(a.name).localeCompare(String(b.name));
      }
      if (this._sort === "datum" && this._tab === "installiert") {
        return String(b._datum).localeCompare(String(a._datum)) || String(a.name).localeCompare(String(b.name));
      }
      return richtung * String(a.name).localeCompare(String(b.name));
    });
    return gefiltert;
  }

  _zeichne() {
    this._gerendert = true;
    const t = this._t;
    const inhalt = this._detail ? this._html_detail() : this._html_liste();
    this.innerHTML = `
      <style>${STIL}</style>
      <div class="hl-panel">
        <div class="hl-kopf">
          <ha-icon icon="mdi:hexagon-multiple"></ha-icon>
          <h1>${fliehe(t.titel)}</h1>
          ${
            this._detail
              ? `<button class="hl-knopf" data-aktion="zurueck">← ${fliehe(t.zurueck)}</button>`
              : `<span class="hl-abstand"></span>
                 <button class="hl-knopf" data-aktion="aktualisieren" ${this._beschaeftigt ? "disabled" : ""}>${fliehe(t.aktualisieren)}</button>`
          }
        </div>
        ${this._fehler ? `<div class="hl-fehler">${fliehe(this._fehler)}</div>` : ""}
        ${inhalt}
      </div>`;
    this._binden();
  }

  _html_liste() {
    const t = this._t;
    const zeilen = this._sichtbar();
    const ist_da = this._tab === "installiert";
    const suchfeld = `
      <div class="hl-werkzeug">
        <input class="hl-suche" type="search" placeholder="${fliehe(t.suche)}"
               value="${fliehe(this._suche)}" data-rolle="suche">
        <select class="hl-sort" data-rolle="sort">
          <option value="name" ${this._sort === "name" ? "selected" : ""}>${fliehe(t.sort.name)}</option>
          <option value="sterne" ${this._sort === "sterne" ? "selected" : ""}>${fliehe(t.sort.sterne)}</option>
          ${ist_da ? `<option value="datum" ${this._sort === "datum" ? "selected" : ""}>${fliehe(t.sort.datum)}</option>` : ""}
        </select>
      </div>`;
    const tabs = `
      <div class="hl-tabs" role="tablist">
        <button class="hl-tab ${ist_da ? "aktiv" : ""}" data-aktion="tab" data-tab="installiert">${fliehe(t.tabs.installiert)}</button>
        <button class="hl-tab ${!ist_da ? "aktiv" : ""}" data-aktion="tab" data-tab="verfuegbar">${fliehe(t.tabs.verfuegbar)}</button>
      </div>`;
    if (!this._instanzen.length) {
      return `${tabs}<div class="hl-hinweis">${fliehe(t.instanzen_leer)}</div>`;
    }
    const scan_form = !ist_da
      ? `
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
        <button class="hl-knopf" data-aktion="scan" ${this._beschaeftigt ? "disabled" : ""}>${fliehe(this._beschaeftigt ? t.scan_laeuft : t.scan)}</button>
      </div>`
      : "";
    const leere_meldung = ist_da ? t.leer : t.keine_funde;
    const koerper = zeilen.length
      ? zeilen.map((z) => (ist_da ? this._html_zeile_eintrag(z) : this._html_zeile_fund(z))).join("")
      : `<div class="hl-hinweis">${fliehe(leere_meldung)}</div>`;
    return `${suchfeld}${tabs}${scan_form}<div class="hl-liste">${koerper}</div>`;
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
        <div class="hl-karte-kopf" data-aktion="details" data-host="${fliehe(e.host)}" data-pfad="${fliehe(e.pfad)}">
          <div class="hl-titelzeile">
            <span class="hl-name">${fliehe(e.name)}</span>
            <span class="hl-kategorie">${fliehe(e.kategorie)}</span>
          </div>
          <div class="hl-unterzeile">
            ${versionszeile}
            <span class="hl-zahlen">
              ${e.sterne !== undefined ? `<span title="Sterne"><ha-icon icon="mdi:star"></ha-icon> ${fliehe(String(e.sterne))}</span>` : ""}
              ${e.offene_tickets !== undefined ? `<span title="Tickets"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(e.offene_tickets))}</span>` : ""}
            </span>
          </div>
          ${e.beschreibung ? `<div class="hl-beschreibung">${fliehe(e.beschreibung)}</div>` : ""}
          ${e.fehler ? `<div class="hl-klein-fehler">${fliehe(e.fehler)}</div>` : ""}
        </div>
        <div class="hl-knöpfe">
          ${
            update_da && e.entity_id
              ? `<button class="hl-knopf hl-primaer" data-aktion="install" data-key="${fliehe(e.storage_key)}">${fliehe(t.update_install)}</button>`
              : ""
          }
          ${
            !e.installiert && e.neueste && e.entity_id
              ? `<button class="hl-knopf hl-primaer" data-aktion="install" data-key="${fliehe(e.storage_key)}">${fliehe(t.installieren)}</button>`
              : ""
          }
          <button class="hl-knopf" data-aktion="entfernen" title="${fliehe(t.entfernt_hinweis)}" data-key="${fliehe(e.storage_key)}">${fliehe(t.entfernen)}</button>
        </div>
      </div>`;
  }

  _html_zeile_fund(f) {
    const t = this._t;
    const sternwort = f.sterne === 1 ? t.sterne_ein : t.sterne_viele;
    return `
      <div class="hl-karte ${f.vorhanden ? "schon-da" : ""}">
        <div class="hl-karte-kopf" data-aktion="details" data-host="${fliehe(this._scan_host)}" data-pfad="${fliehe(f.full_name)}">
          <div class="hl-titelzeile">
            <span class="hl-name">${fliehe(f.name)}</span>
            <span class="hl-kategorie">${fliehe(f.kategorie)}</span>
          </div>
          <div class="hl-unterzeile">
            <span class="hl-version">${fliehe(f.letzte_version || "—")}</span>
            <span class="hl-zahlen">
              <span title="${fliehe(String(f.sterne))} ${fliehe(sternwort)}"><ha-icon icon="mdi:star"></ha-icon> ${fliehe(String(f.sterne))}</span>
              <span title="Tickets"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(f.offene_tickets))}</span>
            </span>
          </div>
          ${f.beschreibung ? `<div class="hl-beschreibung">${fliehe(f.beschreibung)}</div>` : ""}
          ${!f.gueltig && f.fehler ? `<div class="hl-klein-fehler">${fliehe(f.fehler)}</div>` : ""}
        </div>
        <div class="hl-knöpfe">
          ${
            f.vorhanden
              ? `<span class="hl-schon-da">${fliehe(this._t.tabs.installiert)} ✓</span>`
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
      ? `<div class="hl-readme">${markdown(d.readme)}</div>`
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
          <div class="hl-titelzeile">
            <span class="hl-name">${fliehe(info.name || info.full_name)}</span>
          </div>
          ${info.beschreibung ? `<div class="hl-beschreibung">${fliehe(info.beschreibung)}</div>` : ""}
          <div class="hl-unterzeile">
            <span class="hl-zahlen">
              <span title="${fliehe(String(info.sterne))} ${fliehe(sterne_wort)}"><ha-icon icon="mdi:star"></ha-icon> ${fliehe(String(info.sterne))}</span>
              <span title="Tickets"><ha-icon icon="mdi:alert-circle-outline"></ha-icon> ${fliehe(String(info.offene_tickets))}</span>
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
        if (aktion === "tab") {
          this._tab = knopf.dataset.tab;
          this._zeichne();
        } else if (aktion === "aktualisieren") {
          this._lade();
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
        } else if (aktion === "hinzufuegen") {
          const wahl = wurzel.querySelector(
            `select[data-rolle="kategorie"][data-pfad="${CSS.escape(knopf.dataset.pfad)}"]`
          );
          const kategorie = wahl ? wahl.value : "integration";
          this._hinzufuegen(knopf.dataset.host, knopf.dataset.pfad, kategorie);
        }
      });
    }

    const suche = $('input[data-rolle="suche"]');
    if (suche) {
      suche.addEventListener("input", () => {
        this._suche = suche.value;
        const liste = $(".hl-liste");
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
.hl-panel { max-width: 720px; margin: 0 auto; padding: 8px 16px 48px;
  color: var(--primary-text-color); }
.hl-kopf { display: flex; align-items: center; gap: 12px; padding: 8px 0 16px; }
.hl-kopf h1 { font-size: 24px; font-weight: 400; margin: 0; flex: 0 0 auto; }
.hl-kopf ha-icon { color: var(--primary-color, #f6c546); }
.hl-abstand { flex: 1; }
.hl-knöpfe { display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
  justify-content: flex-end; padding: 0 16px 12px; }
.hl-knopf { background: none; border: none; border-radius: 999px;
  padding: 8px 16px; font-size: 14px; font-weight: 500; cursor: pointer;
  color: var(--primary-color, #f6c546);
  font-family: inherit; }
.hl-knopf:hover { background: rgba(0, 0, 0, 0.06); }
.hl-knopf[disabled] { opacity: 0.5; cursor: default; }
.hl-knopf.hl-primaer { background: var(--primary-color, #f6c546);
  color: var(--text-primary-color, #fff); }
.hl-knopf.hl-primaer:hover { filter: brightness(1.05); background: var(--primary-color, #f6c546); }
.hl-fehler { background: var(--error-color, #db4437); color: #fff;
  border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;
  font-size: 14px; }
.hl-hinweis { opacity: 0.7; padding: 24px 0; text-align: center; font-size: 14px; }
.hl-werkzeug { display: flex; gap: 8px; padding-bottom: 12px; }
.hl-suche { flex: 1; border: none; border-radius: 8px;
  background: rgba(0, 0, 0, 0.08); padding: 10px 14px; font-size: 14px;
  color: var(--primary-text-color); font-family: inherit; }
.hl-sort { border: none; border-radius: 8px; background: rgba(0, 0, 0, 0.08);
  padding: 10px; font-size: 14px; color: var(--primary-text-color);
  font-family: inherit; }
.hl-tabs { display: flex; gap: 24px; border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  margin-bottom: 12px; }
.hl-tab { background: none; border: none; padding: 10px 2px; font-size: 14px;
  font-weight: 500; cursor: pointer; color: var(--secondary-text-color);
  border-bottom: 2px solid transparent; font-family: inherit; }
.hl-tab.aktiv { color: var(--primary-color, #f6c546);
  border-bottom-color: var(--primary-color, #f6c546); }
.hl-scan { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center;
  padding: 8px 0 16px; font-size: 13px; }
.hl-scan label { display: flex; align-items: center; gap: 6px;
  color: var(--secondary-text-color); }
.hl-scan input[type="text"], .hl-scan select { border: none;
  border-radius: 6px; background: rgba(0, 0, 0, 0.08); padding: 6px 8px;
  font-size: 13px; color: var(--primary-text-color); font-family: inherit; }
.hl-häkchen { cursor: pointer; }
.hl-karte { background: var(--card-background-color, #fff);
  border-radius: var(--ha-card-border-radius, 12px);
  box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
  margin-bottom: 8px; overflow: hidden; }
.hl-karte.schon-da { opacity: 0.55; }
.hl-karte-kopf { padding: 14px 16px 6px; cursor: pointer; }
.hl-titelzeile { display: flex; align-items: baseline; gap: 10px; }
.hl-name { font-size: 16px; font-weight: 500; word-break: break-all; }
.hl-kategorie { font-size: 12px; color: var(--secondary-text-color);
  border: 1px solid rgba(0,0,0,0.15); border-radius: 999px; padding: 2px 10px; }
.hl-unterzeile { display: flex; align-items: center; gap: 12px;
  padding-top: 6px; font-size: 13px; color: var(--secondary-text-color);
  flex-wrap: wrap; }
.hl-version.frisch { color: var(--primary-color, #f6c546); font-weight: 500; }
.hl-zahlen { display: flex; gap: 10px; margin-left: auto; }
.hl-beschreibung { font-size: 13px; color: var(--secondary-text-color);
  padding-top: 6px; }
.hl-klein-fehler { font-size: 12px; color: var(--error-color, #db4437);
  padding-top: 6px; }
.hl-kategorie-wahl { display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--secondary-text-color); }
.hl-kategorie-wahl select { border: none; border-radius: 6px;
  background: rgba(0, 0, 0, 0.08); padding: 6px 8px; font-size: 13px;
  color: var(--primary-text-color); font-family: inherit; }
.hl-schon-da { font-size: 13px; color: var(--secondary-text-color);
  padding: 8px 0; }
.hl-detail .hl-beschreibung { font-size: 14px; }
.hl-verweise { display: flex; gap: 16px; padding: 10px 0 2px; flex-wrap: wrap; }
.hl-verweise a { color: var(--primary-color, #f6c546);
  text-decoration: none; font-size: 14px; font-weight: 500; }
.hl-readme { padding: 16px 0; font-size: 14px; line-height: 1.5; }
.hl-readme img { max-width: 100%; border-radius: 8px; }
.hl-readme pre { background: rgba(0, 0, 0, 0.08); padding: 12px;
  border-radius: 8px; overflow-x: auto; }
.hl-readme code { font-family: var(--code-font-family, monospace);
  font-size: 13px; }
.hl-readme blockquote { border-left: 3px solid var(--primary-color, #f6c546);
  margin: 8px 0; padding: 4px 12px; opacity: 0.85; }
.hl-releases .hl-release { background: var(--card-background-color, #fff);
  border-radius: var(--ha-card-border-radius, 12px);
  box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
  padding: 12px 16px; margin-bottom: 8px; }
.hl-release-kopf { display: flex; align-items: baseline; gap: 10px; }
.hl-release-tag { font-weight: 500; font-size: 15px; }
.hl-release-datum { margin-left: auto; font-size: 12px;
  color: var(--secondary-text-color); }
.hl-vorab { font-size: 11px; border: 1px solid rgba(0,0,0,0.15);
  border-radius: 999px; padding: 1px 8px;
  color: var(--secondary-text-color); }
.hl-release-name { font-size: 13px; padding-top: 4px; }
.hl-release-notizen { font-size: 13px; padding-top: 6px; line-height: 1.45; }
.hl-readme h1, .hl-detail h2 { font-size: 18px; font-weight: 500; }
.hl-readme h2 { font-size: 16px; }
h2 { font-size: 16px; font-weight: 500; padding: 12px 0 8px; }
`;

customElements.define("hacs-lab-panel", HacsLabPanel);
