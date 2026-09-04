# HACS*lab

HACS behaviour for GitLab repositories: add, discover, and update Home
Assistant custom components that live on a GitLab instance — the way HACS
does it for GitHub.

**Not a fork.** HACS*lab is its own Home Assistant integration that runs
*alongside* HACS. We change no HACS code and copy none. There is a reason:
a fork would have to chase every HACS release, and nobody but us would ever
use it.

## The problem

HACS knows exactly one source: GitHub. A custom repository with a GitLab
address is rejected; there is no switch for it. If your integrations live on
your own — or any other — GitLab instance, you install by hand and never
learn that a new version exists.

HACS*lab closes that gap. It speaks to GitLab (and Forgejo — see
[Codeberg](https://codeberg.org)) directly: it finds repositories tagged for
discovery, reads their metadata, compares versions, downloads the version
archive, and installs it safely.

## Installation

HACS cannot deliver HACS*lab — it only knows GitHub — so the honest way is
by hand. It takes about two minutes.

**Requirements**

- Home Assistant 2024.6 or newer (the test lane runs against 2025.2)
- A GitLab instance you can reach from your Home Assistant host
- Optional: a personal access token with `read_api` scope — for private
  repositories or to be gentler on rate limits

**Steps**

1. Download the release archive `hacs-lab-vX.Y.Z.zip` from the
   [releases page](https://gitlab.schanz.ipv64.net/chance-konstruktion/hacs-lab/-/releases).
   The SHA-256 of the archive is part of every release description — verify
   it if you like.
2. Extract the archive **into your Home Assistant configuration directory**
   (the one that contains `configuration.yaml`). The archive mirrors the
   repository layout, so every folder lands where it belongs: the
   integration under `custom_components/hacs_lab/`, and — depending on the
   release — the core library next to it.
3. Restart Home Assistant.
4. Add the integration: *Settings → Devices & Services → Add Integration*,
   search for **HACS*lab**. Enter the host of your GitLab instance (a pasted
   project link is shortened to its host), optionally your read token. The
   dialog checks the connection and tells you plainly when it fails.
   Several instances sit side by side — one per GitLab host, each with its
   own entries.
5. After setup you get a sidebar panel — no YAML anywhere.

> The setup dialog currently speaks German; English UI strings are on the
> roadmap. The panel itself already carries both languages.

## Using HACS*lab

- **Add a custom repository:** open the panel, choose *Add*, paste the
  project URL, pick a category. HACS*lab reads the metadata, the version,
  and offers the install.
- **Discover:** repositories whose owner set the topic `hacs` on the GitLab
  side show up under *Discovery* — with description, stars, and the latest
  version. A second topic (`hacs-plugin`, `hacs-theme`, …) fixes the
  category without asking.
- **Updates:** every entry gets an update entity and a heartbeat whose
  interval you can tune per entry. A new release or tag raises the update,
  the install service swaps the files safely — staged in a temporary
  directory first, then an atomic switch, rolled back on failure.
- **Robust stock:** a renamed project is recognised by its ID and the name
  follows silently; a reachable-but-changed repository is reported, never
  guessed; diagnostics never print your token in the clear.

## For repository owners

To make a GitLab project findable and installable by HACS*lab:

1. Set the topic `hacs` under *Settings → General → Topics*.
2. Put a valid `hacs.json` on the default branch. Minimal shape:

   ```json
   {
     "name": "My integration",
     "render_readme": true,
     "homeassistant": "2024.6.0"
   }
   ```

   Repositories with a different layout set `content_in_root`,
   `zip_release`, or `filename` — the same conventions HACS established.
3. Publish versions as releases, or at least as tags. Releases win; tags
   are the fallback.

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
hacs_lab/                     the core — pure Python, no Home Assistant,
                              no network in tests
  core/forge.py               the provider interface (GitLab, Forgejo, …)
  core/gitlab_forge.py        GitLab REST v4
  core/forgejo_forge.py       Forgejo (Codeberg recordings)
  core/validierung.py         hacs.json, manifest.json
  core/versionen.py           version compare and update decision
  core/entdeckung.py          topic → candidate → validation
  core/entpacken.py           guarded unpacking, atomic install
custom_components/hacs_lab/   the thin Home Assistant layer
  manifest.json               domain, version, config flow
  config_flow.py              setup dialog with connection check
  frontend/panel.js           the sidebar panel (no YAML)
  translations/               dialog texts
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
