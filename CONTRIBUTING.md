# Contributing

## Prerequisites

- [uv](https://docs.astral.sh/uv/) manages Python and the dependencies: `brew install uv`.
- [Socket Firewall](https://socket.dev/) (`sfw`) vets packages as they are downloaded. It is needed only to add, lock or upgrade dependencies, not to build: `npm install -g sfw`.
- [Trivy](https://trivy.dev/) scans the locked dependencies for known vulnerabilities: `brew install trivy`.

## Layout

| Path                         | What it holds                                                                            |
| ---------------------------- | ---------------------------------------------------------------------------------------- |
| `families/<family>/upstream/` | The original font, trimmed copy; `UPSTREAM.md` records the repo and commit it came from |
| `families/<family>/`          | The family's `OFL.txt` and `FONTLOG.txt`, shipped with its fonts                         |
| `build/common.py`             | Shared build steps: names, metrics, composites, kerning, features, webfonts, CSS        |
| `build/<family>/`             | Each family's glyph designs (`glyphs.py`), kerning (`kerning.py`) and settings (`family.py`) |
| `build/skeleton.py`, `flat.py` | Drawing glyphs as centre lines and stroking them                                        |
| `fonts/`                      | Built fonts, committed so the site can serve them; `trantor.css` covers every family    |
| `index.html`, `<family>/`, `assets/` | The GitHub Pages site                                                          |

## Building

```sh
make fonts                  # every family
make fonts FAMILY=caption   # one family: hand, caption or mark
```

This installs the locked dependencies with uv and runs [build/build.py](build/build.py). For each weight of each family, it:

1. loads the upstream TTF from `families/<family>/upstream/`;
2. replaces the placeholder lowercase (upstream duplicated the capitals) with glyphs drawn as centre-line skeletons in `build/<family>/glyphs.py`, stroked to the weight's width: round ends for Hand, flat ends for Caption and Mark;
3. adds the accented composites and symbols;
4. for Caption and Mark SemiBold, thickens every outline of the finished Regular;
5. rebuilds kerning (`build/<family>/kerning.py`), names, vertical metrics and OS/2 data;
6. writes `fonts/<family>/ttf/*.ttf`, `fonts/<family>/webfonts/*.woff2`, `*.woff` and the family's CSS, then `fonts/trantor.css`.

To change a letter, edit its skeleton in `build/<family>/glyphs.py` and rebuild. Both weights update together. Commit the rebuilt `fonts/` with the change.

Open the site with `make specimen` and go to <http://localhost:8000/>. Each family's page has a type tester and its full character set. Opening the pages straight from disk won't work, because browsers block fonts loaded over `file://`.

### Reproducible builds

Rebuilding on the same platform gives byte-identical fonts: timestamps are pinned to `RELEASE_EPOCH` in [build/common.py](build/common.py). Across platforms, skia-pathops' floating point can move a point by one unit or reorder contours. `make check-fonts`, which CI runs, rebuilds and compares the result with `fonts/` ([build/check.py](build/check.py)):

- it accepts identical files, or outlines within an average of one unit;
- names, cmap, advance widths and OpenType features must match exactly.

The committed fonts are what the site serves and what releases package.

## Releasing

All families share one version, `RELEASE` in [build/common.py](build/common.py), and a release is tagged `v` plus that version (`v1.0.0`). Inside the fonts it is written as a three-place decimal, as OpenType expects: 1.0.0 becomes `Version 1.000`, and 1.2.3 becomes `Version 1.203`. So the minor version must stay under 10 and the patch under 100.

1. Set `RELEASE` and `RELEASE_EPOCH` (the release date, midnight UTC), and add a ChangeLog entry to the top of each family's `FONTLOG.txt` with the same date.
2. Run `make fonts` and commit, including `fonts/`.
3. Check the packages locally with `make release TAG=v1.0.0`. This writes `dist/`, which git ignores.
4. Push a tag: `git tag v1.0.0 && git push origin v1.0.0`.

The [release workflow](.github/workflows/release.yml) then:

- runs the dependency audit and `make release`;
- publishes a GitHub release with `TrantorType.zip` (every family), one zip per family and `SHA256SUMS`;
- uses each family's newest FONTLOG entry as the release notes.

The zip names carry no version, so `releases/latest/download/TrantorHand.zip` always points at the newest release.

## Dependencies

Dependencies are declared in [pyproject.toml](pyproject.toml) and locked with hashes in [uv.lock](uv.lock). Measures against supply chain attacks:

- **Exact pins.** Every direct dependency is pinned to one version (`==`).
- **Minimum release age.** Versions published in the last 3 days are ignored (`exclude-newer`), so a compromised release has time to be found and pulled before it can be locked.
- **Socket Firewall.** Every command that resolves dependencies runs through `sfw`, which blocks known-malicious packages.
- **Wheels only.** `no-build` stops uv from building source distributions, so no third-party build code runs.
- **Locked installs.** `uv sync --locked` installs exactly what is in `uv.lock` and fails if the lockfile is out of date.
- **Pinned actions.** GitHub Actions are pinned to commit SHAs of releases at least two weeks old, with the tool versions (uv, Trivy) pinned too. Workflows get read-only tokens, except the release job, which can write releases.

| Command                        | What it does                                            |
| ------------------------------ | ------------------------------------------------------- |
| `make sync`                    | Install from `uv.lock`                                  |
| `make add PKG=name==1.2.3`     | Add a dependency (exact version required)               |
| `make add-dev PKG=name==1.2.3` | Add a development dependency                            |
| `make lock`                    | Re-resolve `uv.lock` after editing `pyproject.toml`     |
| `make upgrade PKG=name`        | Upgrade one locked package, e.g. to fix a vulnerability |
| `make audit`                   | Fail on HIGH-severity known vulnerabilities (Trivy)     |
| `make check-fonts`             | Rebuild and compare with the committed fonts            |
| `make release TAG=v1.0.0`      | Package `dist/` for a release                           |
