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
 *   HACS-Laden: Aktualisierbar, Installiert, Neu, Downloadbar --
 *   jeder Kopf zaehlt seine Karten und laesst sich zuklappen.
 * * der Laden frischt sich selber auf: jedes Betreten laeuft
 *   ``hacs_lab/erneuern`` -- der frische M5-Lauf, nicht der Takt.
 *   Ruht die Bedienung (15 Sekunden), wird kein zweiter Lauf erzwungen.
 *
 * Flug 2084 macht den Laden voll -- die Wünsche des Imkers:
 *
 * * das Lager (``hacs_lab/lager.<host>`` im Speicher) hält die Liste
 *   und die Funde über Neustart und Wiederkehr hinweg: das Betreten
 *   malt SOFORT aus dem Speicher (``hacs_lab/eintraege``, kein
 *   Netzruf) und erneuert danach im Hintergrund -- der Laden geht
 *   nie wieder leer auf. Der Hintergrund-Takt des Lagers feuert
 *   ``hacs_lab_aktualisiert``; das Panel hört darauf und malt neu,
 *   während es offen bleibt.
 * * die Karten tragen die Zeichen ihrer Projekte (``avatar_url``);
 *   fehlt das Bild, bleibt ein Buchstabe -- nie ein kaputtes Bild.
 * * die Namen sind keine lila GitLab-Links mehr: Weiß im dunkeln,
 *   Schwarz im hellen -- die Farbe der Bedienung (``--primary-text-
 *   color``), damit der Laden in jede Tracht passt.
 * * der Abschnitt heisst jetzt Ehrlich: Installiert ist, was
 *   heruntergeladen und oben ist; Downloadbar ist, was beobachtet
 *   wird, aber noch nichts heruntergeladen hat.
 *
 * Flug 2085 macht den Laden unendlich -- die Wünsche des Imkers:
 *
 * * die Zeichen der Karten wie im Original-HACS: das Bild, wenn die
 *   Forge eins nennt, sonst ein Buchstabe in GitLabs Farben (dieselbe
 *   Pastell-Palette, derselbe Buchstabe immer dieselbe Farbe).
 * * die Instanzen stehen als Plättchen im Laden: jedes klickbar zu
 *   seinen Einstellungen (Abstand, Custom Repositories, Entfernen),
 *   und der gestrichelte «+»-Knopf daneben öffnet den Einrichtungs-
 *   dialog für die NÄCHSTE Instanz. Es gibt keine Obergrenze: jede
 *   Domain ist ein Eintrag, der Laden sammelt sie alle.
 * * der leere Laden (erste Einrichtung) schickt mit einem Knopf
 *   direkt in denselben Dialog -- kein Suchen in den Einstellungen.
 *
 * Flug 2088 stellt drei Schmieden in denselben Laden:
 *
 * * das Warten sieht aus wie Home Assistant: solange noch nichts
 *   da ist (erster Betritt, erste Detailfahrt), steht eine Karte
 *   mit dem Rundblitz des Hauses in seiner Farbe mittig im Raum --
 *   nicht GitLabs Leiste, sondern die Ladesprache der Umgebung.
 * * die Instanz-Plaettchen nennen ihren Anbieter (GitLab, Forgejo,
 *   Gitea) -- die Karte reist als "anbieter" mit der Liste; welche
 *   Schmiede einen Eintrag geformt hat, entscheidet der Server
 *   (core/schmiede.py), hier steht nur das Wort daneben.
 * * das Suffix-Fallback kennt gitea: foo/bar*gitea zaehlt zu seinen
 *   Buchstaben wie *lab und *forge.
 *
 * Flug 2091 macht die Suche EINMALIG -- der Wunsch des Imkers: eine
 * Suchoption oben in der Leiste, keine zweite unter den Kategorien.
 *
 * * das Suchfeld im Balken grenzt beim Tippen ein (wie gehabt) und
 *   fragt auf Enter ALLE eingerichteten Instanzen: ein Wort mit
 *   Schraegstrich ist ein Gruppen-Weg (frueher das Feld unter Neu),
 *   jedes andere ein Stichwort, das der Anbieter in Name und
 *   Beschreibung sucht. Die Funde landen im Abschnitt Neu.
 * * das Formular unter dem Abschnitt Neu ist damit weg -- die Suche
 *   hat nur noch EIN Zuhause, und die Lupe dreht sich, solange die
 *   Server antworten.
 *
 * Zwei Sprachen, im File selbst: Deutsch und Englisch, gewaehlt nach
 * der Sprache der Bedienung. Der Kennzeichnungs-Suffix (*lab, *forge,
 * *gitea)
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
      installiert: "Installiert",
      neu: "Neu",
      downloadbar: "Downloadbar",
    },
    abschnittstexte: {
      aktualisierbar: "Eine neuere Version ist erschienen",
      installiert: "Heruntergeladen und auf dem neuesten Stand",
      neu: "Was die Suche oben fand — noch nicht aufgenommen",
      downloadbar: "Beobachtet, aber noch nichts heruntergeladen",
    },
    abschnitte_leer: {
      aktualisierbar: "Nichts zu tun — alles auf dem neuesten Stand.",
      installiert: "Noch nichts heruntergeladen.",
      neu: "Noch keine Funde — oben suchen und Enter drücken.",
      downloadbar: "Nichts Beobachtetes ohne Download.",
    },
    stand: "Stand",
    suche_hinweis: "Eingrenzen beim Tippen — Enter fragt alle Instanzen",
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
    fuss_zeile: "Für die Freiheit gebaut — kein GitHub-Monopol-Scheiß.",
    lade_titel: "Wird geladen …",
    lade_text: "Der Bestand kommt aus dem Lager — einen Augenblick.",
    detail_lade_text: "Stammdaten, Beschreibung und Releases werden geholt.",
    instanzen_titel: "Instanzen",
    instanz_hinzufuegen: "Instanz hinzufügen",
    erste_instanz: "Erste Instanz einrichten",
    instanz_verwalten:
      "Instanz öffnen — Abstand, Custom Repositories, Entfernen",
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
      installiert: "Installed",
      neu: "New",
      downloadbar: "Downloadable",
    },
    abschnittstexte: {
      aktualisierbar: "A newer version has been released",
      installiert: "Downloaded and up to date",
      neu: "What the search above found — not added yet",
      downloadbar: "Watched, but nothing downloaded yet",
    },
    abschnitte_leer: {
      aktualisierbar: "Nothing to do — everything is up to date.",
      installiert: "Nothing downloaded yet.",
      neu: "No findings yet — search above and press Enter.",
      downloadbar: "Nothing watched without a download.",
    },
    stand: "as of",
    suche_hinweis: "Narrow while typing — Enter asks every instance",
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
    fuss_zeile:
      "Made for freedom — no GitHub monopoly, because one platform is a single point of failure.",
    lade_titel: "Loading …",
    lade_text: "The stock is on its way from the store cache — one moment.",
    detail_lade_text: "Fetching metadata, description, and releases.",
    instanzen_titel: "Instances",
    instanz_hinzufuegen: "Add instance",
    erste_instanz: "Set up the first instance",
    instanz_verwalten: "Open instance — interval, custom repositories, remove",
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

/** Void-Tags: stehen allein, ohne Schliesser. */
const VOID_TAGS = new Set([
  "br", "hr", "img", "input", "meta", "link", "col", "area", "base",
  "embed", "source", "track", "wbr",
]);

/** Gaenzlich verbotene Tags: Skripte, Rahmen, Formen -- weg, samt Inhalt. */
const HTML_VERBOTEN = new Set([
  "script", "style", "iframe", "object", "embed", "form", "input",
  "button", "select", "textarea", "template", "noscript", "svg", "math",
  "frame", "frameset", "applet", "video", "audio", "canvas",
]);

/** Erlaubte Tags im README -- der Rest verliert seine Huelle, der Inhalt bleibt. */
const HTML_ERLAUBT = new Set([
  "table", "thead", "tbody", "tfoot", "tr", "td", "th", "caption",
  "colgroup", "col", "div", "span", "p", "br", "hr",
  "h1", "h2", "h3", "h4", "h5", "h6",
  "ul", "ol", "li", "dl", "dt", "dd", "blockquote", "center",
  "details", "summary", "figure", "figcaption",
  "b", "i", "u", "s", "strong", "em", "small", "sub", "sup",
  "code", "pre", "kbd", "samp", "var", "mark", "del", "ins", "abbr",
  "cite", "a", "img",
]);

/** Attribute je Tag -- nur diese reisen mit, Adressen nur http(s). */
const ATTR_PRO_TAG = {
  a: ["href", "title"],
  img: ["src", "alt", "title", "width", "height"],
  td: ["colspan", "rowspan", "align", "width"],
  th: ["colspan", "rowspan", "align", "width"],
  table: ["align", "border", "width", "summary"],
  details: ["open"],
  abbr: ["title"],
};

function html_attribute(node) {
  const tag = node.tagName.toLowerCase();
  const erlaubt = ATTR_PRO_TAG[tag];
  let raus = "";
  if (erlaubt) {
    for (const name of erlaubt) {
      const wert = node.getAttribute(name);
      if (wert === null || wert === undefined || wert === "") {
        continue;
      }
      if ((name === "href" || name === "src") && !adresse_ok(String(wert))) {
        continue;
      }
      raus += ` ${name}="${fliehe(String(wert))}"`;
    }
  }
  if (tag === "a" && adresse_ok(node.getAttribute("href") || "")) {
    raus += ' target="_blank" rel="noopener noreferrer"';
  }
  return raus;
}

function html_sauber(node) {
  if (node.nodeType === 3) {
    return inline_markdown(fliehe(node.nodeValue || ""));
  }
  if (node.nodeType !== 1) {
    return "";
  }
  const tag = node.tagName.toLowerCase();
  if (HTML_VERBOTEN.has(tag)) {
    return "";
  }
  // Ein Bild ohne taugliche Adresse ist keine Zierde, nur Muell --
  // es faellt ganz weg (javascript: und Verwandte erreichen so nie
  // den Laden).
  if (tag === "img" && !adresse_ok(node.getAttribute("src") || "")) {
    return "";
  }
  const kinder = [...node.childNodes].map(html_sauber).join("");
  if (!HTML_ERLAUBT.has(tag)) {
    return kinder;
  }
  if (VOID_TAGS.has(tag)) {
    return `<${tag}${html_attribute(node)}>`;
  }
  return `<${tag}${html_attribute(node)}>${kinder}</${tag}>`;
}

/**
 * Ein HTML-Block aus dem README, gesaeubert (Flug 2096, Wunde 1).
 *
 * Die Tabellen und der Schmuck vieler HACS-READMEs kommen als HTML --
 * bislang standen sie als Roh-Text im Laden. Der Sauberer nimmt den
 * Block auseinander (DOMParser) und setzt ihn aus der Whitelist
 * wieder zusammen: Skripte und Rahmen fallen ganz weg, unbekannte
 * Huellen verlieren nur ihre Schale, Adressen duerfen http(s) sein,
 * und Inline-Markdown laeuft ueber die Textknoten wie ueberall.
 */
function html_block(zeilen) {
  try {
    const doc = new DOMParser().parseFromString(zeilen.join("\n"), "text/html");
    return [...doc.body.childNodes].map(html_sauber).join("");
  } catch (fehler) {
    return zeilen.map(fliehe).join("\n");
  }
}

/**
 * Der Kleinstrenderer: Ueberschriften, Listen, Zitate, Code-Bloecke,
 * Trennlinien, Absaetze plus Inline-Markdown. HTML-Bloecke (Tabellen
 * und Schmuck vieler HACS-READMEs) gehen seit Flug 2096 durch den
 * Sauberer -- Whitelist, keine Skripte, nur http(s)-Adressen --;
 * alles andere kommt geflohen rein, wie immer.
 */
function markdown(text) {
  if (!text) return "";
  const rohzeilen = String(text).split(/\r?\n/);

  // Vorab-Zerlegung (Flug 2096): Codezaeune schuetzen ihren Inhalt
  // vor der HTML-Erkennung -- ein ```-Beispiel mit <table> darin bleibt
  // Code. Ein HTML-Block beginnt mit einem oeffnenden Tag und endet mit
  // dessen Schliesser; Void-Tags stehen allein. Zwischen den Zeilen
  // eines Blocks darf alles stehen (auch Leerzeilen und Fliesstext),
  // denn Textknoten kriegen ohnehin Inline-Markdown.
  const teile = []; // { art: "md", zeile } | { art: "fertig", html }
  let code = null;
  let html = null; // { zeilen: [...], tag: "table" }
  for (const roh of rohzeilen) {
    if (code !== null) {
      if (/^\s*```/.test(roh)) {
        teile.push({
          art: "fertig",
          html: `<pre><code>${fliehe(code.join("\n"))}</code></pre>`,
        });
        code = null;
      } else {
        code.push(roh);
      }
      continue;
    }
    if (/^\s*```/.test(roh)) {
      code = [];
      continue;
    }
    if (html !== null) {
      html.zeilen.push(roh);
      if (new RegExp(`</${html.tag}\\s*>`, "i").test(roh)) {
        teile.push({ art: "fertig", html: html_block(html.zeilen) });
        html = null;
      }
      continue;
    }
    const eroeffner = roh.match(/^\s*<([a-zA-Z][a-zA-Z0-9-]*)\b/);
    if (eroeffner) {
      const tag = eroeffner[1].toLowerCase();
      if (VOID_TAGS.has(tag)) {
        teile.push({ art: "fertig", html: html_block([roh]) });
        continue;
      }
      html = { zeilen: [roh], tag };
      continue;
    }
    teile.push({ art: "md", zeile: fliehe(roh) });
  }
  if (code !== null) {
    teile.push({
      art: "fertig",
      html: `<pre><code>${fliehe(code.join("\n"))}</code></pre>`,
    });
  }
  if (html !== null) {
    teile.push({ art: "fertig", html: html_block(html.zeilen) });
  }

  const stueck = [];
  let absatz = [];
  let modus = null; // null | "ul" | "ol" | "blockquote"

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

  for (const teil of teile) {
    if (teil.art === "fertig") {
      absatz_schliessen();
      liste_schliessen();
      stueck.push(teil.html);
      continue;
    }
    const zeile = teil.zeile;
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

/** Uhrkurzform (Stand des Lagers), falls ISO -- sonst unverandert. */
function uhr_kurz(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/** Der juengste Lager-Stand ueber alle Instanzen (leer, wenn keiner). */
function neuester_stand(karte) {
  let juengste = "";
  for (const wert of Object.values(karte || {})) {
    if (String(wert) > juengste) {
      juengste = String(wert);
    }
  }
  return juengste;
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

/** Die Marken der drei Schmieden -- Eigennamen, nicht übersetzbar. */
const ANBIETER_NAMEN = {
  gitlab: "GitLab",
  forgejo: "Forgejo",
  gitea: "Gitea",
};

/** Der Rundblitz -- die Warteskulptur des Hauses (Flug 2088).
 *
 * Derselbe Bogen, den ha-spinner zeichnet: ein Kreis, dem ein Stück
 * fehlt, das sich dreht. Bewusst als eigenes SVG statt als ha-spinner:
 * das Element gehört dem Haus und darf fehlen -- die eigene Zeichnung
 * steht immer, und ihre Farben sind die der Tracht (var). */
function dreher_svg(groesse_klasse) {
  return (
    `<svg class="${groesse_klasse}" viewBox="0 0 24 24" aria-hidden="true" ` +
    `focusable="false"><circle cx="12" cy="12" r="9.5" fill="none" ` +
    `stroke="currentColor" stroke-width="2.6" stroke-linecap="round" ` +
    `stroke-dasharray="43 14"/></svg>`
  );
}

/** Die Abschnitte des Ladens, in dieser Reihenfolge. */
const ABSCHNITTE = ["aktualisierbar", "installiert", "neu", "downloadbar"];

/** Das Ereignis, das der Server feuert, sobald ein Lager frisch liegt. */
const EREIGNIS_AKTUALISIERT = "hacs_lab_aktualisiert";

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

/** Das Markenbild (Flug 2097): original.png, 96x96 als Daten-URI.
 *
 * Der Imker hat gesprochen -- EIN Bild ueberall: das Panel traegt es
 * in der Leiste und auf der Ladeseite, dieselbe Quelle liefert auch
 * den Avatar und spaeter die exe-Form. Eingebettet als Daten-URI,
 * damit das Panel ohne zweite Datei und ohne Netzruft auskommt;
 * die Fuesse des Markensymbols (Fusszeile, Brotkrumen-Pfeil) bleiben
 * fuer den Fuchs von GitLab reserviert.
 */
const LOGO_DATAURI = "data:image/png;base64,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";

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

/** Der Server -- zwei Schichten mit Licht, fuer die Instanz-Plaettchen. */
const SERVER_SVG =
  '<svg class="hl-server" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<rect x="1.5" y="1.8" width="13" height="4.6" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.4"/>' +
  '<circle cx="4.1" cy="4.1" r="0.95" fill="currentColor"/>' +
  '<rect x="1.5" y="9.6" width="13" height="4.6" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.4"/>' +
  '<circle cx="4.1" cy="11.9" r="0.95" fill="currentColor"/></svg>';

/** Warndreieck fuer die Instanz-Meldung. */
const WARN_SVG =
  '<svg class="hl-warn" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
  '<path d="M8 2 15 14H1Z" fill="none" stroke="currentColor" stroke-width="1.5" ' +
  'stroke-linejoin="round"/><path d="M8 6.5v3.2" stroke="currentColor" ' +
  'stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="12" r="0.9" ' +
  'fill="currentColor"/></svg>';

/** Wie lange ein frischer Lauf ruht, bevor der Betritt ihn erneut erzwinge. */
const BETRETEN_RUHE_MS = 15000;

/**
 * GitLabs Pastell-Palette fuer Buchstaben-Zeichen (Flug 2085): fehlt
 * das Bild eines Projekts, bekommt sein Buchstabe eine dieser Farben
 * -- dieselbe Farbe fuer denselben Namen, wie GitLab es mit seinen
 * Initialen-Avataren haelt. Der Buchstabe bleibt dunkel (#333238,
 * GitLabs Leisten-Farbe): lesbar auf Pastell, bei Tag und bei Nacht.
 */
const ZEICHEN_FARBEN = [
  "#FFD599",
  "#D6EFFF",
  "#FCD5CE",
  "#D3FDD8",
  "#E4DFFF",
  "#FFE1BE",
  "#C4D7F6",
  "#FDE8F6",
  "#D9F2E6",
  "#F3E5C3",
];
const ZEICHEN_SCHRIFT = "#333238";

/** Dasselbe Wort -- dieselbe Farbe. Stabil, unauffaellig, ohne Speicher. */
function zeichen_farbe(name) {
  let saat = 0;
  for (const zeichen of String(name)) {
    saat = (saat * 31 + (zeichen.codePointAt(0) || 0)) % 9973;
  }
  return ZEICHEN_FARBEN[saat % ZEICHEN_FARBEN.length];
}

/** Die Klasse des Panels. */
class HacsLabPanel extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._suche = "";
    this._sort = "name";
    this._eintraege = [];
    this._instanzen = [];
    this._anbieter = {}; // host -> Schmiede-Name (GitLab/Forgejo/Gitea)
    this._funde_pro_host = {}; // host -> Funde (Lager oder eigene Suche)
    this._aktualisiert_am = {}; // host -> Zeitstempel des Lagers
    this._kategorien = KATEGORIEN;
    this._funde_von = ""; // Gruppen-Wort, das die Funde zuletzt erzeugte (Flug 2091)
    this._sucht = false; // laeuft gerade die Kopfsuche gegen die Instanzen?
    this._such_fehler = {}; // host -> Grund (nur von der Kopfsuche)
    this._detail = null; // { host, pfad, daten }
    this._fehler = "";
    this._instanz_fehler = {}; // host -> Grund (aus dem frischen Lauf)
    this._beschaeftigt = false;
    this._laedt = true; // die erste Fahrt: noch nichts gesehen (Flug 2088)
    this._erneuert_am = 0;
    this._abmeldung = null; // Ereignis-Abo kuenndigen
    this._offen = {
      aktualisierbar: true,
      installiert: true,
      neu: true,
      downloadbar: false,
    };
  }

  set hass(hass) {
    const erste = this._hass === null;
    this._hass = hass;
    if (erste) {
      this._abonnieren();
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

  disconnectedCallback() {
    // Das Ereignis-Abo gehoert zum Element: verlaesst der Laden die
    // Buehne, wird es gekuendigt -- niemand hoert auf leere Kartons.
    if (this._abmeldung) {
      try {
        this._abmeldung();
      } catch (fehler) {
        /* schon gekuendigt */
      }
      this._abmeldung = null;
    }
  }

  get _t() {
    return TEXTE[sprache(this._hass)];
  }

  /** Der Betritt: erst aus dem Lager malen, dann im Hintergrund erneuern. */
  _betrete() {
    if (!this._hass) {
      return;
    }
    this._lade().finally(() => {
      if (
        this._erneuert_am &&
        Date.now() - this._erneuert_am < BETRETEN_RUHE_MS
      ) {
        return;
      }
      this._erneuern();
    });
  }

  /** Auf das Ereignis des Lagers hoeren -- der Hintergrund malt mit. */
  _abonnieren() {
    const verbindung = this._hass && this._hass.connection;
    if (!verbindung || typeof verbindung.subscribeEvents !== "function") {
      return; // Rueckhalt: ohne Abonnement bleibt der Frischhol-Knopf
    }
    verbindung
      .subscribeEvents((ereignis) => {
        if (!ereignis || !ereignis.host || this._beschaeftigt || this._detail) {
          return;
        }
        this._lade();
      }, EREIGNIS_AKTUALISIERT)
      .then((abmelden) => {
        this._abmeldung = abmelden;
      })
      .catch(() => {
        /* das Abonnement darf scheitern, der Laden bleibt bedienbar */
      });
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

  /** Der frische Lauf: jeder Aktualisierer wird herumgedreht, dann das Lager. */
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
      this._uebernehme(antwort);
      this._instanz_fehler = antwort.gescheitert || {};
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    this._erneuert_am = Date.now();
    this._laedt = false;
    this._beschaeftigt = false;
    this._zeichne();
  }

  /**
   * Ziel im Home-Assistant-Frontend ansteuern (Flug 2085).
   *
   * Der Weg ist derselbe, dessen sich HACS fuer seine Knöpfe bedient:
   * Adresse in die Geschichte legen und das Router-Ereignis feuern --
   * das Frontend haelt die Leiste, das Panel wird abgebaut. Gelingt
   * das Ereignis nicht (kaum denkbar), faellt die Zeile auf die gute
   * alte Ganze-Seite-Weiterleitung zurueck.
   */
  _gehe(ziel) {
    try {
      window.history.pushState(null, "", ziel);
      window.dispatchEvent(new Event("location-changed"));
    } catch (fehler) {
      window.location.assign(ziel);
    }
  }

  /** Die Liste laden -- der schnelle Griff aus dem Lager (kein Netzruf). */
  async _lade() {
    if (!this._hass) return;
    this._beschaeftigt = true;
    this._zeichne();
    try {
      const antwort = await this._hass.callWS({
        type: "hacs_lab/eintraege",
      });
      this._uebernehme(antwort);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = this._fehlertext(fehler);
    }
    // Die erste Fahrt ist vorbei: ob mit Bestand oder mit Fehler --
    // ab hier ist die Ladeseite nicht mehr die ehrliche Antwort.
    this._laedt = false;
    this._beschaeftigt = false;
    this._zeichne();
  }

  /** Eine Lager-Antwort in den Zustand des Panels uebernehmen. */
  _uebernehme(antwort) {
    this._eintraege = antwort.eintraege || [];
    this._instanzen = antwort.instanzen || [];
    this._anbieter = antwort.anbieter || {};
    this._kategorien = antwort.kategorien || KATEGORIEN;
    this._funde_pro_host = {};
    for (const fund of antwort.funde || []) {
      const host = fund.host || "";
      (this._funde_pro_host[host] = this._funde_pro_host[host] || []).push(fund);
    }
    this._aktualisiert_am = antwort.aktualisiert_am || {};
    // Der frische Lauf ist die neuere Wahrheit: die Funde stammen jetzt
    // wieder vom Takt des Hauses, nicht mehr von der letzten Kopfsuche.
    this._funde_von = "";
    this._such_fehler = {};
  }

  /**
   * Die Kopfsuche fragt die Instanzen (Flug 2091: die EINE Suche).
   *
   * Tippen grenzt ein -- Enter fragt alle eingerichteten Server direkt.
   * Ein Wort mit Schraegstrich ist ein Gruppen-Weg (wie frueher das
   * Feld unter Neu), alles andere ein Stichwort, das der Anbieter in
   * Name und Beschreibung sucht. Leer gefragt: der ganze Bestand,
   * genau wie der Takt ihn faende. Die Funde landen im Abschnitt Neu
   * und bleiben bis zum naechsten Lauf des Lagers stehen; gescheiterte
   * Server melden sich im Banner und verlieren ihre letzten Funde
   * nicht.
   */
  async _suche_server() {
    if (this._sucht || !this._hass || !this._instanzen.length) {
      return;
    }
    this._sucht = true;
    this._zeichne();
    const nadel = this._suche.trim();
    const funde_neu = {};
    const fehler = {};
    for (const host of this._instanzen) {
      const frage = { type: "hacs_lab/entdecken", host: host };
      if (nadel.includes("/")) {
        frage.gruppe = nadel;
      } else if (nadel) {
        frage.stichwort = nadel;
      }
      try {
        const antwort = await this._hass.callWS(frage);
        funde_neu[host] = antwort.funde || [];
      } catch (grund) {
        fehler[host] = this._fehlertext(grund);
        funde_neu[host] = this._funde_pro_host[host] || [];
      }
    }
    this._funde_pro_host = funde_neu;
    this._funde_von = nadel.includes("/") ? nadel : "";
    this._such_fehler = fehler;
    this._sucht = false;
    this._zeichne();
    // Die Frage ist fertig -- der Fokus gehoert zurueck ins Feld, der
    // Cursor an sein Ende (dieselbe Kunst wie beim Tippen).
    const frisch = this.querySelector('input[data-rolle="suche"]');
    if (frisch) {
      frisch.focus();
      frisch.setSelectionRange(frisch.value.length, frisch.value.length);
    }
  }

  /** Detailansicht holen: Stammdaten, README, Releases. */
  async _hole_detail(host, pfad) {
    // Erst das Geruest: der Name steht in den Brotkrumen, waehrend die
    // Ladeseite (Flug 2088) den Rest heranholt.
    this._detail = { host: host, pfad: pfad, daten: null };
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
      // Zurueck in den Laden mit der Meldung -- eine steckengebliebene
      // Ladeseite waere die unehrlichere Antwort.
      this._detail = null;
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
      const liste = this._funde_pro_host[host] || [];
      if (liste.length) {
        this._funde_pro_host[host] = liste.map((f) =>
          f.full_name === pfad ? { ...f, vorhanden: true } : f
        );
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
    this._beschaeftigt = false;
    this._erneuert_am = 0; // der Betritt-Ruhe zwingt hier nichts
    await this._erneuern();
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
   * aktualisierbar (installiert, aber neueste weicht ab), installiert
   * (heruntergeladen und oben), downloadbar (beobachtet, nichts
   * heruntergeladen), neu (Funde der Suche, noch nicht aufgenommen).
   */
  _gruppen() {
    const aktualisierbar = [];
    const installiert = [];
    const downloadbar = [];
    for (const e of this._eintraege) {
      if (!this._passt(e)) {
        continue;
      }
      const update_da = e.neueste && e.installiert !== e.neueste;
      if (e.installiert && update_da) {
        aktualisierbar.push(e);
      } else if (e.installiert) {
        installiert.push(e);
      } else {
        downloadbar.push(e);
      }
    }
    // Die Funde der Kopfsuche sind die ANTWORT auf das Gruppen-Wort --
    // wenn die Nadel genau dieses Wort ist, zeigt der Abschnitt Neu
    // alles, was die Server sagten (die Namen muessen das Wort ja nicht
    // tragen). Jede andere Nadel greift wie ueberall: Name, Pfad, Text.
    const nadel = this._suche.trim().toLowerCase();
    const gruppen_wort = this._funde_von.trim().toLowerCase();
    // Flug 2096, Wunde 2 aus dem 3-System-Test: ein Gesicht, ein Platz.
    // Ein Fund, der schon Eintrag ist, bleibt NUR beim Eintrag --
    // entweder Neu ODER Downloadbar ODER Installiert/Aktualisierbar,
    // nie doppelt und nie dreifach. Der Server schickt in jedem Fund
    // ein vorhanden-Faehnchen, und der eigene Abgleich greift, falls
    // das Faehnchen fehlt.
    const bereits = new Set(
      this._eintraege.map(
        (e) => (e.host || "") + "|" + (e.pfad || e.full_name || "")
      )
    );
    const neu = [];
    for (const host of Object.keys(this._funde_pro_host)) {
      for (const fund of this._funde_pro_host[host]) {
        if (fund && fund.vorhanden) {
          continue;
        }
        const name = fund.full_name || fund.pfad || "";
        if (bereits.has((fund.host || host) + "|" + name)) {
          continue;
        }
        if (nadel && nadel !== gruppen_wort && !this._passt(fund)) {
          continue;
        }
        neu.push(fund);
      }
    }
    return {
      aktualisierbar: this._sortiere(aktualisierbar),
      installiert: this._sortiere(installiert),
      neu: this._sortiere(neu),
      downloadbar: this._sortiere(downloadbar),
    };
  }

  _zeichne() {
    this._gerendert = true;
    const inhalt = this._detail
      ? this._detail.daten
        ? this._html_detail()
        : this._html_ladeseite(this._t.detail_lade_text)
      : this._laedt && !this._instanzen.length && !this._eintraege.length
        ? this._html_ladeseite(this._t.lade_text)
        : this._html_laden();
    this.innerHTML = `
      <style>${STIL}</style>
      <div class="hl-panel">
        ${this._html_balken()}
        <div class="hl-inhalt">
          ${this._fehler ? `<div class="hl-fehler">${fliehe(this._fehler)}</div>` : ""}
          ${inhalt}
        </div>
        ${this._html_fusszeile()}
      </div>`;
    this._binden();
  }

  /** Die Ladeseite (Flug 2088) -- die Warteskulptur des Hauses.
   *
   * Der Rundblitz dreht sich in der Farbe der Tracht
   * (``--primary-color``), die Karte traegt die Ecken und den Grund
   * des Hauses (``--ha-card-*``). Solange noch kein Bestand da ist,
   * ist DAS die ehrliche Flaeche -- keine leeren Abschnitte, kein
   * Zappeln, sondern die Sprache, die Home Assistant auch spricht,
   * wenn es selber laedt.
   */
  _html_ladeseite(text) {
    const t = this._t;
    return `
      <div class="hl-ladeseite">
        <div class="hl-ladekarte" role="status" aria-live="polite">
          <img class="hl-lade-logo" src="${LOGO_DATAURI}" alt="${fliehe(t.titel)}">
          ${dreher_svg("hl-dreher")}
          <div class="hl-lade-titel">${fliehe(t.lade_titel)}</div>
          <div class="hl-lade-text">${fliehe(text || t.lade_text)}</div>
        </div>
      </div>`;
  }

  /** Der Balken oben -- GitLabs Leiste: Marke, Suche, Werkzeuge. */
  _html_balken() {
    const t = this._t;
    const updates = this._gruppen().aktualisierbar.length;
    const marke = `
      <div class="hl-marke">
        <img class="hl-logo" src="${LOGO_DATAURI}" alt="${fliehe(t.titel)}">
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
        <div class="hl-suchfeld ${this._sucht ? "sucht" : ""}">
          ${LUPE_SVG}
          <input class="hl-suche" type="search" placeholder="${fliehe(t.suche)}"
                 value="${fliehe(this._suche)}" data-rolle="suche"
                 title="${fliehe(t.suche_hinweis)}"
                 enterkeyhint="search"
                 aria-label="${fliehe(t.suche)}"
                 ${this._sucht ? 'aria-busy="true"' : ""}>
        </div>
        <div class="hl-werkzeuge">
          <button class="hl-ikonknopf" data-aktion="aktualisieren" title="${fliehe(t.aktualisieren)}"
                  aria-label="${fliehe(t.aktualisieren)}" ${this._beschaeftigt ? "disabled" : ""}>${KREIS_SVG}</button>
          <button class="hl-ikonknopf" data-aktion="neu" title="${fliehe(t.neu_knopf)}"
                  aria-label="${fliehe(t.neu_knopf)}">${PLUS_SVG}</button>
        </div>
      </div>`;
  }

  /** Die Fusszeile (Flug 2092): der Gruss vom unteren Rand.
   *
   * Wer ganz runterscrollt, bekommt den Grund des Hauses in einer
   * Zeile: der Fuchs und das Geluebde -- fuer die Freiheit gebaut,
   * gegen das Monopol. Der Fuchs tanzt ein kleines Stueck, wenn man
   * ihn streichelt (hover) -- sonst steht er still und wartet.
   */
  _html_fusszeile() {
    const t = this._t;
    return `
      <footer class="hl-fuss" role="contentinfo">
        ${tanuki_svg("hl-fuss-tanuki")}
        <span class="hl-fuss-wort">${fliehe(t.fuss_zeile)}</span>
      </footer>`;
  }

  /** Der Laden: Werkzeugleiste, Instanz-Plaettchen, Meldung, Abschnitte. */
  _html_laden() {
    const t = this._t;
    if (!this._instanzen.length) {
      return `
        <div class="hl-hinweis">
          <div>${fliehe(t.instanzen_leer)}</div>
          <button class="hl-knopf hl-primaer hl-hinweis-knopf" data-aktion="instanz_hinzu">
            ${fliehe(t.erste_instanz)}
          </button>
        </div>`;
    }
    const gruppen = this._gruppen();
    const gesamt =
      gruppen.aktualisierbar.length +
      gruppen.installiert.length +
      gruppen.downloadbar.length;
    const stand = uhr_kurz(neuester_stand(this._aktualisiert_am));
    const stand_zeile = stand
      ? ` · ${fliehe(t.stand)} ${fliehe(stand)}`
      : "";
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
        <span class="hl-zaehler-zeile">${fliehe(t.anzahl(gesamt))}${stand_zeile}${this._sucht ? ` · ${fliehe(t.scan_laeuft)}` : this._beschaeftigt ? ` · ${fliehe(t.frisch_laeuft)}` : ""}</span>
      </div>
      <div class="hl-instanzzeile">
        <span class="hl-instanzwort">${fliehe(t.instanzen_titel)}</span>
        ${this._instanzen
          .map(
            (h) =>
              `<button class="hl-instanz" data-aktion="instanz" title="${fliehe(t.instanz_verwalten)}">${SERVER_SVG}<span>${fliehe(h)}</span>${this._html_anbieter(h)}</button>`
          )
          .join("")}
        <button class="hl-instanz hl-instanz-neu" data-aktion="instanz_hinzu" title="${fliehe(t.instanz_hinzufuegen)}">${PLUS_SVG}<span>${fliehe(t.instanz_hinzufuegen)}</span></button>
      </div>`;
    const meldungen = {
      ...this._instanz_fehler,
      ...this._such_fehler,
    };
    const meldung = Object.keys(meldungen).length
      ? `<div class="hl-banner">${WARN_SVG}<span>${fliehe(
          Object.entries(meldungen)
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
        ${offen ? `<div class="hl-abschnitt-koerper">${karten}${leer}</div>` : ""}
      </section>`;
  }

  /** Das Zeichen einer Karte: Bild, oder farbiger Buchstabe (GitLab). */
  _avatar_html(zeile) {
    const name = String(zeile.name || zeile.full_name || "?").trim();
    const bloss = name.replace(/[*](lab|forge|gitea)$/i, "");
    const buchstabe = fliehe(
      (bloss.charAt(0) || "?").toUpperCase()
    );
    const farbe = zeichen_farbe(bloss || name);
    const adresse = String(zeile.avatar_url || "");
    if (adresse && adresse_ok(adresse)) {
      return (
        `<img class="hl-avatar" src="${fliehe(adresse)}" alt="" loading="lazy"` +
        ` data-buchstabe="${buchstabe}" data-farbe="${farbe}">`
      );
    }
    return (
      `<span class="hl-avatar hl-avatar-buchstabe" style="background:${farbe};` +
      `color:${ZEICHEN_SCHRIFT}" aria-hidden="true">${buchstabe}</span>`
    );
  }

  /** Das Wort der Schmiede auf einem Plaettchen (Flug 2088).
   *
   * Die Karte "anbieter" reist mit der Liste; fehlt sie (alter
   * Server, spaeterer Blick), bleibt das Plaettchen, wie es war --
   * kein Wort ist besser als ein geratenes.
   */
  _html_anbieter(host) {
    const name = ANBIETER_NAMEN[this._anbieter[host]];
    return name ? `<span class="hl-anbieter">${fliehe(name)}</span>` : "";
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
        ${this._avatar_html(e)}
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
    const host = f.host || "";
    return `
      <div class="hl-karte ${f.vorhanden ? "schon-da" : ""}">
        ${this._avatar_html(f)}
        <div class="hl-karte-haupt">
          <div class="hl-karte-kopf" data-aktion="details" data-host="${fliehe(host)}" data-pfad="${fliehe(f.full_name)}" title="${fliehe(t.details)}">
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
                   <button class="hl-knopf hl-primaer" data-aktion="hinzufuegen" data-host="${fliehe(host)}" data-pfad="${fliehe(f.full_name)}" ${this._beschaeftigt ? "disabled" : ""}>${fliehe(t.hinzufuegen)}</button>`
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
          ${this._avatar_html({ name: info.name || info.full_name, avatar_url: info.avatar_url })}
          <div class="hl-karte-haupt">
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

    // Ein Zeichen, das nicht kommen will, wird zum Buchstaben -- nie
    // zum kaputten Bild (Flug 2084). Der Fallback sitzt als Zuhoerer,
    // nicht als Inline-Attribut: CSP laesst Inline-Handler kalt. Seit
    // Flug 2085 traegt er dieselbe Farbe wie von Anfang an.
    for (const bild of $$(".hl-avatar[data-buchstabe]")) {
      bild.addEventListener("error", () => {
        const ersatz = document.createElement("span");
        ersatz.className = "hl-avatar hl-avatar-buchstabe";
        ersatz.setAttribute("aria-hidden", "true");
        ersatz.style.background = bild.dataset.farbe || "";
        ersatz.style.color = ZEICHEN_SCHRIFT;
        ersatz.textContent = bild.dataset.buchstabe || "?";
        bild.replaceWith(ersatz);
      });
    }

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
        } else if (aktion === "instanz") {
          // Plättchen: zu den Einstellungen der Integration -- dort stehen
          // Abstand, Custom Repositories und Entfernen je Instanz.
          this._gehe("/config/integrations/integration/hacs_lab");
        } else if (aktion === "instanz_hinzu") {
          // Die nächste Domain: der Einrichtungsdialog, Domain vorbelegt.
          this._gehe("/config/integrations/dashboard/add?domain=hacs_lab");
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
      // Enter fragt die Instanzen: die EINE Suche des Ladens (Flug
      // 2091) -- das Formular unter den Kategorien ist damit erspart.
      suche.addEventListener("keydown", (ereignis) => {
        if (ereignis.key === "Enter") {
          ereignis.preventDefault();
          this._suche_server();
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
/* Das Markenbild (Flug 2097): original.png in der Leiste -- Eckigkeit
   wie GitLabs eigene Kachel, Hoehe wie einst der Fuchs. */
.hl-logo { height: 28px; width: auto; flex: 0 0 auto; border-radius: 6px;
  display: block; }
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
.hl-inhalt { max-width: 1000px; margin: 0 auto; padding: 12px 16px 8px; }

/* -- Die Fusszeile (Flug 2092): Fuchs und Geluebde am unteren Rand */
.hl-fuss { max-width: 1000px; margin: 0 auto; padding: 20px 16px 32px;
  display: flex; align-items: center; justify-content: center; gap: 9px;
  color: var(--secondary-text-color); font-size: 12.5px;
  border-top: 1px solid rgba(127, 127, 127, .25); }
.hl-fuss-tanuki { height: 18px; width: auto; flex: 0 0 auto;
  transition: transform .25s ease; }
.hl-fuss:hover { color: var(--primary-text-color); }
.hl-fuss:hover .hl-fuss-tanuki { animation: hl-fuchs-tanz .6s ease; }
@keyframes hl-fuchs-tanz { 25% { transform: rotate(-9deg); }
  60% { transform: rotate(7deg); } 100% { transform: rotate(0); } }
.hl-fehler { background: var(--error-color, #db4437); color: #fff;
  border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 14px; }
.hl-banner { display: flex; gap: 10px; align-items: flex-start;
  background: rgba(252, 163, 38, .14); border: 1px solid rgba(252, 163, 38, .55);
  border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 13.5px;
  color: var(--primary-text-color); }
.hl-warn { width: 15px; height: 15px; color: var(--hl-gold);
  flex: 0 0 auto; margin-top: 1px; }
.hl-hinweis { opacity: .7; padding: 24px 0; text-align: center; font-size: 14px; }
.hl-hinweis-knopf { margin-top: 14px; }

/* -- Die Instanz-Plaettchen (Flug 2085): endlos viele Server */
.hl-instanzzeile { display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 0 0 12px; }
.hl-instanzwort { font-size: 12.5px; color: var(--secondary-text-color);
  flex: 0 0 auto; }
.hl-instanz { display: inline-flex; align-items: center; gap: 7px;
  border: 1px solid rgba(127, 127, 127, .4); border-radius: 999px;
  background: var(--card-background-color, #fff); color: var(--primary-text-color);
  padding: 4px 12px 4px 9px; font: inherit; font-size: 12.5px; cursor: pointer;
  max-width: 100%; }
.hl-instanz span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hl-instanz svg { width: 13px; height: 13px; flex: 0 0 auto;
  color: var(--secondary-text-color); }
.hl-instanz:hover { border-color: var(--hl-orange); }
.hl-instanz:hover svg { color: var(--hl-orange); }
.hl-instanz-neu { border-style: dashed; }
.hl-instanz-neu svg { width: 12px; height: 12px; }

/* -- Das Wort der Schmiede auf dem Plaettchen (Flug 2088) */
.hl-anbieter { font-size: 10.5px; font-weight: 600; line-height: 1.7;
  color: var(--secondary-text-color); border: 1px solid rgba(127, 127, 127, .35);
  border-radius: 999px; padding: 0 7px; flex: 0 0 auto; }

/* -- Die Ladeseite (Flug 2088): Home Assistants eigene Wartesprache.
   Der Rundblitz dreht in der Farbe der Tracht, die Karte traegt Ecken
   und Grund des Hauses -- dieselben Variablen, die ha-card nutzt. */
.hl-ladeseite { display: flex; justify-content: center; padding: 56px 0; }
.hl-ladekarte { display: flex; flex-direction: column; align-items: center;
  gap: 10px; min-width: 260px; max-width: 380px; padding: 30px 44px;
  background: var(--card-background-color, #fff);
  border: 1px solid var(--ha-card-border-color, rgba(127, 127, 127, .35));
  border-radius: var(--ha-card-border-radius, 12px);
  box-shadow: var(--ha-card-box-shadow, none); }
/* Das Markenbild auf der Ladeseite: das Gesicht des Hauses, solange
   der Rundblitz noch dreht (Flug 2097). */
.hl-lade-logo { height: 56px; width: auto; border-radius: 10px; }
.hl-dreher { width: 36px; height: 36px; color: var(--primary-color, #03a9f4);
  animation: hl-drehen .9s linear infinite; }
.hl-lade-titel { font-size: 15px; font-weight: 600;
  color: var(--primary-text-color); }
.hl-lade-text { font-size: 13px; color: var(--secondary-text-color);
  text-align: center; line-height: 1.45; }
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

/* -- Die Kopfsuche (Flug 2091): waehrend sie laeuft, dreht sich die
   Lupe -- dieselbe Sprache wie der Rundblitz der Ladeseite. */
.hl-suchfeld.sucht .hl-lupe { animation: hl-drehen .9s linear infinite;
  color: var(--hl-orange); }

/* -- Karten: GitLaws Zeilen -- kompakt, Rand statt Schatten */
.hl-karte { display: flex; gap: 12px; background: var(--card-background-color, #fff);
  border: 1px solid rgba(127, 127, 127, .35); border-radius: 4px;
  padding: 12px 14px; margin-bottom: 8px; flex-wrap: wrap; align-items: flex-start; }
.hl-karte:hover { border-color: rgba(127, 127, 127, .6); }
.hl-karte.schon-da { opacity: .55; }

/* -- Das Zeichen der Karte (Flug 2084): Bild oder Buchstabe.
   Flug 2085: ohne Bild traegt der Buchstabe GitLabs Pastell -- die
   Farbe kommt von der Karte (inline), die Klasse bleibt das Layout. */
.hl-avatar { width: 38px; height: 38px; border-radius: 6px; flex: 0 0 auto;
  object-fit: cover; background: var(--card-background-color, #fff); }
.hl-avatar-buchstabe { display: inline-flex; align-items: center; justify-content: center;
  background: rgba(127, 127, 127, .18); color: var(--primary-text-color);
  font-weight: 600; font-size: 16px; user-select: none; }

.hl-karte-haupt { flex: 1 1 340px; min-width: 0; }
.hl-karte-kopf { display: flex; align-items: baseline; gap: 10px; cursor: pointer; }
.hl-name { font-size: 15px; font-weight: 600; color: var(--primary-text-color);
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
.hl-verweise a { color: var(--primary-text-color); text-decoration: underline;
  font-size: 14px; font-weight: 500; }
.hl-verweise a:hover { text-decoration: none; }
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
.hl-readme a { color: var(--primary-text-color); text-decoration: underline; }
/* Flug 2096: die HTML-Tabellen der HACS-READMEs -- dezent im Haus-Stil */
.hl-readme table { border-collapse: collapse; margin: 10px 0; max-width: 100%;
  display: block; overflow-x: auto; }
.hl-readme td, .hl-readme th { border: 1px solid var(--divider-color, rgba(127, 127, 127, .25));
  padding: 6px 10px; vertical-align: top; }
.hl-readme ul, .hl-readme ol { padding-left: 22px; margin: 6px 0; }
.hl-readme p { margin: 6px 0; }
.hl-releases .hl-release { background: var(--card-background-color, #fff);
  border: 1px solid rgba(127, 127, 127, .35); border-radius: 4px;
  padding: 12px 16px; margin-bottom: 8px; }
.hl-release-kopf { display: flex; align-items: baseline; gap: 10px; }
.hl-release-tag { font-weight: 600; font-size: 14.5px;
  background: rgba(127, 127, 127, .15); color: var(--primary-text-color);
  border-radius: 4px; padding: 1px 8px; }
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
