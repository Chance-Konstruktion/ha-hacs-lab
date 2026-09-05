# HACS*lab

HACS behaviour for self-hosted Git forges: add, discover, and update Home
Assistant custom components that live on **GitLab**, **Gitea**, or **Forgejo**
([Codeberg](https://codeberg.org)) — the way HACS does it for GitHub.

**Not a fork.** HACS*lab is its own Home Assistant integration that runs
*alongside* HACS. We change no HACS code and copy none. There is a reason:
a fork would have to chase every HACS release, and nobody but us would ever
use it.

## The problem

HACS knows exactly one source: GitHub. A custom repository with a GitLab
address is rejected; there is no switch for it. If your integrations live on
your own — or any other — GitLab, Gitea, or Forgejo instance, you install
by hand and never learn that a new version exists.

HACS*lab closes that gap. It speaks to all three families directly: it finds
repositories tagged for discovery, reads their metadata, compares versions,
downloads the version archive, and installs it safely.

## Installation

HACS cannot deliver HACS*lab — it only knows GitHub — so the honest way is
by hand. It takes about two minutes.

**Requirements**

- Home Assistant 2025.2 or newer (the test lane runs against 2026.2)
- A GitLab, Gitea, or Forgejo (Codeberg) instance you can reach from your
  Home Assistant host
- Optional: a read token — for private repositories or to be gentler on
  rate limits (GitLab `read_api` scope; a Gitea/Forgejo token with read
  access)

**Steps**

1. Download the release archive `hacs-lab-vX.Y.Z.zip` from the
   [releases page](https://gitlab.schanz.ipv64.net/chance-konstruktion/hacs-lab/-/releases).
   The SHA-256 of the archive is part of every release description — verify
   it if you like. The archive link points into this GitLab's package
   registry; the project is internal, so downloading needs an account on the
   instance.
2. Extract the archive **into your Home Assistant configuration directory**
   (the one that contains `configuration.yaml`). The archive contains a
   single folder, `custom_components/hacs_lab/` — core library included.
   One folder to copy, nothing else to set up; the integration finds its
   core through relative imports, so it never touches your Python path.
3. Restart Home Assistant.
4. Add the integration: *Settings → Devices & Services → Add Integration*,
   search for **HACS*lab**. Enter the host of your instance (a pasted
   project link is shortened to its host) and, optionally, your read token.
   The provider stays on **auto** for most cases — HACS*lab asks the
   instance itself which API it speaks (works for gitlab.com, codeberg.org,
   gitea.com, and self-hosted servers alike); pick GitLab, Forgejo, or Gitea
   by hand only if auto-detection cannot decide. The dialog checks the
   connection and tells you plainly when it fails.
   Several instances sit side by side — one per host, each with its own
   provider, token, and entries.
5. After setup you get a sidebar panel — no YAML anywhere. The sidebar
   entry wears the GitLab tanuki, served by the integration itself
   (`frontend/iconset.js`, registered on every frontend page).

> The setup dialog and the panel speak German and English — Home
> Assistant picks the language, the integration ships both
> (`translations/de.json`, `translations/en.json`).

> **Upgrading from v0.1.0?** That archive shipped an import layout that
> breaks the setup dialog with `No module named 'hacs_lab'` — the config
> flow reached for a top-level package that Home Assistant never
> provides. Remove **both** leftovers from your configuration directory
> first: `custom_components/hacs_lab/` **and** the stray top-level
> `hacs_lab/` folder the old archive dropped next to it. Then extract a
> current archive (one folder, core included) and restart. Since v0.1.1
> the integration also carries an icon in the settings page
> (`mdi:gitlab`); `logo.png` and `original.png` in this repository are
> the brand artwork — the demonic GitLab fox taking over the Home
> Assistant house: HA blue, a white home, and a tanuki in ember colors
> with burning GitLab seams whose claws dig into the facade.

> **Upgrading from v0.1.1?** Extract the v0.2.0 archive over the old
> folder and restart — same layout, nothing to clean up. What's new:
> a repository in the plain HACS layout (`custom_components/<domain>/`
> nested anywhere in its tag source archive) now installs **without a
> prebuilt attachment** — HACS*lab finds the storage form itself
> (issue #15) — and HACS*lab now accepts its own delivery form, so it
> can keep itself up to date: add this repository to its own watch
> list and the next release offers itself as an update.

## Using HACS*lab

> **Handbuch / Manual:** the [project wiki](https://gitlab.schanz.ipv64.net/chance-konstruktion/
> hacs-lab/-/wikis/Home) explains everything in depth, **in German and in
> English** — installation, adding providers (as many servers as you like,
> GitLab/Gitea/Forgejo in any mix), settings, the store, repository-owner
> instructions, and a troubleshooting page.

- **The panel:** one page, collapsible sections like the HACS store —
  *Updatable*, *Installed*, *New* (scan findings), *Downloadable* —
  each header counting its cards. The top bar follows your GitLab:
  tanuki mark, a "Search or go to …" field, refresh and add tools,
  breadcrumbs in the detail view. Cards carry their project's avatar
  (or a letter in GitLab's pastel colours when a project has none).
  Names follow your theme's text colour — white in dark mode, black in
  light mode. While the first stock is still on its way, the panel shows
  a Home Assistant-style loading card (spinner in your theme's primary
  colour) instead of an empty store.
- **Unlimited servers, any mix:** every instance is one config entry —
  set up as many as you like, each with its own provider (GitLab,
  Forgejo, Gitea), token, and interval. The store shows them all as
  clickable instance chips — each labelled with its provider — with a
  dashed "+ Add instance" button that opens the setup dialog for the
  next domain. The empty store's first-run hint carries the same button.
- **Never an empty store:** the list lives in the *Lager*, a per-instance
  cache in Home Assistant's storage (`hacs_lab.lager.<host>`). Opening
  the panel paints from that cache instantly (no network round-trip),
  then runs the fresh check in the background and re-renders when it
  lands. After a restart the cache is read while Home Assistant is
  still booting; the first background run follows shortly, and the
  same interval you set for the heartbeat keeps the cache fresh —
  `hacs_lab_aktualisiert` events repaint the panel while it stays
  open. The refresh button still forces a run at any time.
- **Add a custom repository:** open the panel, choose *Add*, paste the
  project URL, pick a category. HACS*lab reads the metadata, the version,
  and offers the install.
- **Discover:** repositories whose owner set the topic `hacs` on their
  GitLab, Gitea, or Forgejo project show up in the panel's *New* section
  — with description, stars, and the latest version. A second topic
  (`hacs-plugin`, `hacs-theme`, …) fixes the category without asking.
- **Updates:** every entry gets an update entity and a heartbeat whose
  interval you can tune per entry. A new release or tag raises the update,
  the install service swaps the files safely — staged in a temporary
  directory first, then an atomic switch, rolled back on failure.
- **Preferred source:** if a release carries exactly one ZIP attachment,
  that built artifact is installed instead of the auto-generated tag
  archive; anything ambiguous falls back to the archive. That fallback
  understands the repository layout: it finds `custom_components/<domain>/`
  at any depth and installs only that subtree — so the standard HACS
  structure installs as-is, without a built attachment (issue #15).
- **Uninstall & restart:** every entry with a recorded install also
  uninstalls — the recorded target path is checked against the known
  category roots, then removed in one move. Installing or uninstalling
  an **integration** raises a repair-center hint to restart Home
  Assistant (integrations only load at startup); the hint clears
  itself once the restart happened.
- **Robust stock:** a renamed project is recognised by its ID and the name
  follows silently; a reachable-but-changed repository is reported, never
  guessed; diagnostics never print your token in the clear.

## For repository owners

To make a project findable and installable by HACS*lab (works the same on
GitLab, Gitea, and Forgejo/Codeberg):

1. Set the topic `hacs` under *Settings → General → Topics*.
2. Put a valid `hacs.json` on the default branch. Minimal shape:

   ```json
   {
     "name": "My integration",
     "render_readme": true,
     "homeassistant": "2025.2.0"
   }
   ```

   Repositories with a different layout set `content_in_root`,
   `zip_release`, or `filename` — the same conventions HACS established.
3. Publish versions as releases, or at least as tags. Releases win; tags
   are the fallback. No built artifact required: the auto-generated tag
   archive is enough — HACS*lab recognises the `custom_components/<domain>/`
   folder inside it and installs exactly that subtree, leaving repository
   root files (README, CI config) out of the target. A release with a
   built ZIP attachment (the domain folder as its root) stays the most
   precise delivery and still wins when present.

`hacs-development` as a second topic marks a repository as a development
state — it is only found when explicitly searched for.

## Safety

Installing code from a forge is a trust decision, not a technical one.
HACS*lab takes the technical part seriously: version archives are unpacked
with path-escape, size, count, and symlink guards — four malicious test
archives (path traversal, giant file, symlink attack, zip bomb) are part of
the test suite and must be rejected *before* anything is written. The
integrity of an interrupted install never lies: staged first, switched
atomically, rolled back on failure.

## Repository layout

```
logo.png, original.png        brand artwork — the GitLab fox in the HA house
hacs.json                     repository conventions for HACS*lab itself
custom_components/hacs_lab/   the integration — thin Home Assistant layer
  manifest.json               domain, version, config flow, icon
  config_flow.py              setup dialog with connection check
  lager.py                    the store cache: persisted list + scan,
                              background interval, `hacs_lab_aktualisiert`
  frontend/panel.js           the sidebar panel (no YAML) — GitLab-style
  frontend/iconset.js         the tanuki as sidebar icon (own icon
                              collection `hacs-lab`, on every page)
  translations/               dialog texts
  core/                       the core — pure Python, no Home Assistant,
                              no network in tests; lives here since the
                              delivery-form decision (issue #11)
    forge.py                  the provider interface (GitLab, Forgejo, Gitea, …)
    gitlab_forge.py           GitLab REST v4
    forgejo_forge.py          Forgejo (Codeberg recordings)
    gitea_forge.py            Gitea — the Forgejo sister (topic search)
    schmiede.py               the forge factory + provider auto-detection
    http_aiohttp.py           aiohttp-backed HttpClient (session passed in)
    validierung.py            hacs.json, manifest.json
    versionen.py              version compare and update decision
    entdeckung.py             topic → candidate → validation
    entpacken.py              guarded unpacking, atomic install
auslieferung/release_bauen.py deterministic release archive builder
tests/                        core suite — pytest, no network
tests_ha/                     Home Assistant lane — offline, on a test double
```

## Development

Two lanes, one verdict: the core runs lean, the framework layer needs
Home Assistant (Python 3.13, `requirements-ha.txt`).

```bash
python -m pytest -q                       # core: no HA, no network
python -m pytest tests_ha -q -p pytest_homeassistant_custom_component
```

On Windows set `PYTHONUTF8=1` first — otherwise healthy tests report
failures that are not there.

Releases are built deterministically by
`auslieferung/release_bauen.py`: fixed timestamps, sorted entries,
reproducible bytes. A tag pipeline builds the archive and attaches it to a
GitLab release; the build refuses when the tag and `manifest.json`
disagree on the version.

The engineering documentation is German — that is where the reasoning
lives: [ARCHITEKTUR.md](ARCHITEKTUR.md) (the four structural decisions),
[ROADMAP.md](ROADMAP.md) (milestones M0–M10 and their acceptance tests),
[MITARBEIT.md](MITARBEIT.md) (how to contribute). The interface for a
second forge provider — and what HACS itself would have to adopt for one —
is written up in [PROPOSAL.md](PROPOSAL.md).

## License

[MIT](LICENSE) — Copyright (c) 2026 chance-konstruktion and the HACS*lab
contributors.
