# Trantor Hand

**Trantor Hand** is Foundation Titles Hand v0.85 (Regular and SemiBold) with:

1. a new lowercase a–z, drawn in the same monoline, round-ended style as the capitals and stroked at the same weight (80 units Regular, 101 SemiBold);
1. accented letters for UK English loanwords (café, naïve, rôle, façade, señor, Zoë…): à á â ä ç è é ê ë ì í î ï ñ ò ó ô ö ù ú û ü, their capitals, and ı;
1. £, €, …, •, ° and a no-break space;
1. rebuilt kerning: the original capital pairs plus lowercase pairs (Ta, Yo, We, r., y, …);
1. an optional stylistic set (`ss01`) with the dotted o and crossed w of the title-sequence capitals.

The upstream licence reserves the name "FoundationTitlesHand", so the modified font has to use a different name. To rename it, change `FAMILY` and `CSS_FILE` in [build/build.py](build/build.py) and rebuild.

## Using the webfont

Copy [fonts/webfonts/](fonts/webfonts/) into the web application and include the stylesheet:

```html
<link rel="stylesheet" href="/fonts/trantor-hand.css" />
```

```css
body {
  font-family: "Trantor Hand", sans-serif;
} /* weight 400 */
strong,
h1,
h2 {
  font-weight: 600;
} /* SemiBold */
.titles {
  font-feature-settings: "ss01";
} /* dotted o, crossed w */
```

WOFF2 (with a WOFF fallback) is used by all current browsers. Desktop TTFs are in [fonts/ttf/](fonts/ttf/).

Open the specimen with `make specimen` and go to <http://localhost:8000/specimen/>. Opening it directly from disk won't work because browsers block fonts loaded over `file://`.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) manages Python and the dependencies: `brew install uv`.
- [Socket Firewall](https://socket.dev/) (`sfw`) vets packages as they are downloaded. It is needed only to add, lock or upgrade dependencies, not to build: `npm install -g sfw`.
- [Trivy](https://trivy.dev/) scans the locked dependencies for known vulnerabilities: `brew install trivy`.

## Building

```sh
make fonts
```

This installs the locked dependencies with uv and runs [build/build.py](build/build.py), which:

1. loads the upstream TTFs from [upstream/fonts/ttf/latest/](upstream/fonts/ttf/latest/);
2. replaces the placeholder lowercase (upstream duplicated the capitals) with glyphs drawn as centre-line skeletons in [build/glyphs.py](build/glyphs.py) and expanded to outlines with round caps and joins ([build/skeleton.py](build/skeleton.py));
3. adds the accented composites and symbols;
4. rebuilds kerning ([build/kerning.py](build/kerning.py)), names, vertical metrics and OS/2 data;
5. writes `fonts/ttf/*.ttf`, `fonts/webfonts/*.woff2`, `*.woff` and `trantor-hand.css`.

To change a letter, edit its skeleton in `build/glyphs.py` and rebuild. Both weights update together.

## Dependencies

Dependencies are declared in [pyproject.toml](pyproject.toml) and locked with hashes in [uv.lock](uv.lock). Measures against supply chain attacks:

- **Exact pins.** Every direct dependency is pinned to one version (`==`).
- **Minimum release age.** Versions published in the last 3 days are ignored (`exclude-newer`), so a compromised release has time to be found and pulled before it can be locked.
- **Socket Firewall.** Every command that resolves dependencies runs through `sfw`, which blocks known-malicious packages.
- **Wheels only.** `no-build` stops uv from building source distributions, so no third-party build code runs.
- **Locked installs.** `uv sync --locked` installs exactly what is in `uv.lock` and fails if the lockfile is out of date.

| Command                        | What it does                                            |
| ------------------------------ | ------------------------------------------------------- |
| `make sync`                    | Install from `uv.lock`                                  |
| `make add PKG=name==1.2.3`     | Add a dependency (exact version required)               |
| `make add-dev PKG=name==1.2.3` | Add a development dependency                            |
| `make lock`                    | Re-resolve `uv.lock` after editing `pyproject.toml`     |
| `make upgrade PKG=name`        | Upgrade one locked package, e.g. to fix a vulnerability |
| `make audit`                   | Fail on HIGH-severity known vulnerabilities (Trivy)     |

## Source and licence

[upstream/](upstream/) is a copy of [rsperberg/foundation-titles-hand](https://github.com/rsperberg/foundation-titles-hand) at commit `1c7b784` (22 Nov 2021), trimmed to what the build and licence need: the v0.85 TTFs, the original iFontMaker sources and the licence and font-log files. The sample images, the title-sequence reference frames and the older font versions were removed; the images in `upstream/README.md` now link to the original repo.

The fonts are licensed under the SIL Open Font License 1.1 (see [OFL.txt](OFL.txt)). The licence text has to be distributed with the fonts, and the fonts may not be sold on their own. Change history is in [FONTLOG.txt](FONTLOG.txt).
