# Font Series

There are some other 2 other fonts we need to extend and fold into this repo. 

https://github.com/rsperberg/foundation-logo
https://github.com/rsperberg/foundation-one

Review them and advise on the approach to add them, including. Licence(s), overview about docs & sample pages for the series & usage guides. It's likely we'd use releases in Github as well, so consider when structuring this repo. It's ok if we need to rename this repo & the existing font (it hasn't been officially released yet).

## Plan

### What the upstream repos contain

|                      | Foundation Titles Hand (done: Trantor Hand) | Foundation Logo                                   | Foundation One                                      |
| -------------------- | ------------------------------------------- | ------------------------------------------------- | --------------------------------------------------- |
| Source of the design | Title sequence                              | Series logo (only F O U N D A T I exist on screen) | On-screen captions ("400 YEARS EARLIER", "SYNNAX") |
| Version / last commit | 0.85                                       | 0.3 (`703e55b`)                                   | 0.4 (`e21be3f`)                                     |
| Weights              | Regular, SemiBold                           | One (Medium, 500)                                 | One (Medium, 500)                                   |
| Coverage             | Basic Latin, 103 chars                      | Basic Latin + dashes/quotes, 103 chars            | 98 chars. **Missing** `$ % * ^ _ \` ~`, has `¤`     |
| Lowercase slots      | Copies of caps (we drew a real lowercase)   | Caps, except **e f k p s w x y z hold alternate capitals** | Copies of caps (z differs slightly)        |
| Kerning              | 1,823 pairs (`kern`)                        | 1,232 pairs (`kern`)                              | 1,915 pairs (`kern`)                                |
| OpenType features    | None                                        | None                                              | None                                                |
| Source format        | iFontMaker `.ifm2archive` + TTF             | Same                                              | Same                                                |
| GitHub releases      | None                                        | None                                              | None                                                |
| Licence              | OFL 1.1, RFN `FoundationTitlesHand`         | OFL 1.1, RFN `FoundationLogo`                     | OFL 1.1, RFN `FoundationOne`                        |

All three use the same structure: 1000 UPM, one TTF per weight, OFL 1.1, Roger Sperberg as copyright holder. Their TTFs load in the existing fontTools pipeline as Trantor Hand's do. Logo and One are monoline like Hand, but with flat stroke ends and sharp corners where Hand is rounded. Stems are about 120 units (Logo) and 116 (One), against Hand's 80 and 101. So new glyphs can be drawn with the skeleton approach in `build/skeleton.py`, once the stroker supports flat ends and sharp corners.

### Licences

- **Fonts: OFL 1.1, as now.** Each derived font must:
  - use a name that doesn't contain its Reserved Font Name. To be safe, avoid "Foundation" in every family name, since it is also the Apple TV+ title;
  - keep the upstream copyright line and add ours, as `OFL.txt` already does for Hand;
  - ship with the OFL text and keep the FONTLOG going.
- **Don't promote with the author's name.** OFL condition 4 bars using Roger Sperberg's name to promote the derivatives without permission. Credits in FONTLOG and on the About page are fine; "by Roger Sperberg" in marketing copy is not.
- **One root `OFL.txt` listing all three copyright/RFN lines.** The OFL allows several copyright lines, and GitHub still detects the licence as OFL-1.1. Each family folder and each release zip also gets its own `OFL.txt` with only that family's lines, so a single-font download carries the correct notice.
- **Build code: add an MIT `LICENSE-CODE`** for `build/`, the Makefile and the site. The OFL covers fonts, not tooling. *(Decision 4)*
- **No new Reserved Font Name for "Trantor".** Adding one would make forks harder for little benefit. *(Decision 4)*
- **Add a non-affiliation disclaimer** to the README, the site footer and FONTLOGs: the fonts are fan-made, based on lettering from the Apple TV+ series *Foundation*, and not affiliated with or endorsed by Apple, Skydance or the Asimov estate. Usage guides should say that typesetting the show's logo for commercial use can raise trademark issues, whatever the font licence says. This matters most for the Logo font.
- **Before release, run a quick trademark search** on the chosen family names.
- **Optional courtesy:** tell the upstream author about the derivatives (an issue on each repo, or an email to the address in the FONTLOGs).

### Naming

Keep **Trantor** as the series name, with a suffix for each font's role. Trantor Hand doesn't need renaming.

| Upstream               | New family                                  | Role                                     |
| ---------------------- | ------------------------------------------- | ---------------------------------------- |
| Foundation Titles Hand | **Trantor Hand** (unchanged)                | Titles and short text; has a lowercase   |
| Foundation Logo        | **Trantor Mark** (alt: Trantor Display)     | Wordmarks, a few large words             |
| Foundation One         | **Trantor Caption** (alt: Trantor Sign)     | All-caps labels, place and time stamps   |

Rename the repo **`trantor-hand` → `trantor-type`** (alt: `trantor-fonts`). GitHub redirects git and web URLs after a rename. It does **not** redirect GitHub Pages, so `desholmes.github.io/trantor-hand` will 404. That is acceptable because nothing has been released, but the link added in `167d161` and the About page must be updated in the same change.

### Extending Logo and One

The show never uses lowercase in either design, so both lowercases are our own invention. Each will be monoline with flat ends and will take on its font's quirks: Caption's decorative dots, Mark's broken strokes and stemless forms. *(Decisions 2 and 5)*

Applies to both:
- **Lowercase a–z:** drawn as centre-line skeletons and stroked at both weights, as for Hand. Review rendered specimens of the first pass before tuning kerning.
- **Weights:** the upstream outlines become Regular (400), unchanged. SemiBold (600) capitals, figures and punctuation come from offsetting the upstream outlines evenly on both sides with skia-pathops, to stems about 25% heavier (~150 units), the same step as Hand. The lowercase is stroked at the matching width.
- Same additions as Hand: the UK English accented letters (as composites, upper and lower), `ı`, `£ € … • °` and a no-break space.
- Convert the upstream `kern` table to GPOS and add pairs for the new glyphs, as `build/kerning.py` already does.
- New name table, version, vertical metrics, OS/2 data and pinned timestamps, using the code Hand already has.
- Same outputs as Hand: TTF, WOFF2, WOFF and a CSS file.

**Trantor Mark:**
- Move the alternate capitals from the lowercase slots (e f k p s w x y z) into named glyphs under `ss01`, with `salt` as well so design apps' alternates pickers find them.
- Investigate an `ss02` for the second, thinner logo (undotted O, different A F N), using the reference images upstream. Optional; can follow later.

**Trantor Caption:**
- Draw the missing `$ % * ^ _ \` ~` to match its dotted figures, so it covers Basic Latin in full.
- Keep `¤`.

### Repo structure

```
trantor-type/
├── README.md              series overview, families, quick start, links
├── OFL.txt                all three copyright/RFN lines
├── LICENSE-CODE           MIT, build tooling and site
├── CONTRIBUTING.md        building, dependencies (moved out of README)
├── Makefile               make fonts | make fonts FAMILY=mark | make specimen | make release
├── pyproject.toml, uv.lock
├── build/
│   ├── common.py          names, metrics, OS/2, GPOS from kern, composites, webfonts, CSS
│   ├── build.py           entry point; builds one or all families
│   ├── hand/              glyphs.py, kerning.py, skeleton.py, family.py
│   ├── mark/              family.py (alternates → ss01/salt, additions)
│   └── caption/           family.py, glyphs.py (missing symbols)
├── families/
│   ├── hand/              FONTLOG.txt, OFL.txt, upstream/ (the current upstream/, plus UPSTREAM.md with repo + commit)
│   ├── mark/              FONTLOG.txt, OFL.txt, upstream/
│   └── caption/           FONTLOG.txt, OFL.txt, upstream/
├── fonts/                 built output, committed (Pages serves it)
│   ├── trantor.css        @font-face for every family
│   ├── hand/              ttf/, webfonts/, trantor-hand.css
│   ├── mark/
│   └── caption/
├── index.html             series landing page (GitHub Pages root)
├── hand/  mark/  caption/ one page per family: about, specimen, usage
├── assets/site.css        shared site styles
└── .github/workflows/     check.yml, release.yml
```

Notes on the structure:
- **Keep committing built fonts.** Pages serves from the repo, and builds are already byte-identical (`RELEASE_EPOCH`), so CI can rebuild and fail if the committed files are stale.
- **Refactor `build/build.py` before adding the new fonts.** Its `Builder` class becomes the shared base in `common.py`, and each family supplies its specifics. Make sure Hand's output is byte-identical before and after the refactor (only the paths change); this proves the refactor.
- **Record upstream provenance.** Vendor each upstream (TTF, `.ifm2archive` sources, OFL, FONTLOG, README) under `families/<name>/upstream/` with the commit SHA it came from. Leave out the sample and reference JPGs; we'll link to them instead.

### Docs and sample pages

GitHub Pages, static HTML, using the fonts themselves:

- **`/` (series landing):** what the series is, then a card for each family. Each card shows a live sample set in that font, the family's role, its weights and character set, and buttons for specimen and latest download. Below the cards: the disclaimer, credits and licence summary.
- **`/<family>/` (one page per family):**
  - **About:** origin in the show, the upstream font and version, what we changed.
  - **Specimen:** editable type tester (size, weight, case, ss01 toggle), size waterfall, full character grid, alternates shown side by side, kerning samples.
  - **Usage.**
  - **Download:** links to the latest release assets.
- **Usage guide (on each family page, with a summary in the README):**
  - Web: self-host and include `fonts/trantor.css` or the family's own CSS. Pin to a release with jsDelivr (`cdn.jsdelivr.net/gh/desholmes/trantor-type@v1.000/fonts/...`). Use `font-display: swap`, preload the WOFF2, apply ss01 with `font-feature-settings`.
  - Desktop: install the TTFs on macOS and Windows; find alternates in Figma, Adobe and Pages.
  - Which font to use when: Hand for titles and short running text, Mark for wordmarks of a few words, Caption for labels with tracking. Include suggested `letter-spacing` and pairings.
  - Mark and Caption's lowercase is our addition. For the on-screen look, set them in caps with `text-transform: uppercase`.
  - Licence in plain English, plus the trademark note.
- **README** becomes a series overview with a quick start. The build and dependency material moves to CONTRIBUTING.md.

### Releases

- **Version the series as a whole.** All families share one version, and the tag equals the font version string: tag `v1.000` ↔ name-table `Version 1.000`. Per-family tags (`hand-v1.000`) break GitHub's "Latest release" and complicate CI, so I'd only use them if the families need to ship independently. *(Decision 3)*
- **Release assets:**
  - `TrantorType-v1.000.zip`: every family, `OFL.txt`, FONTLOGs and a README.
  - One zip per family, e.g. `TrantorHand-v1.000.zip`: `ttf/`, `webfonts/` with CSS, that family's `OFL.txt` and `FONTLOG.txt`, and a short README.
  - `SHA256SUMS`.
- **`make release`** builds the zips locally into `dist/`, which is git-ignored.
- **`release.yml`** runs on a `v*` tag push:
  1. `make sync`, `make fonts`, `make audit`;
  2. check that the rebuilt fonts match the committed ones;
  3. `make release`;
  4. create the GitHub release with the assets and the changelog section from the FONTLOGs.

  Pin actions to commit SHAs, matching the repo's supply-chain approach.
- **`check.yml`** runs on PRs: build, verify the committed fonts are current, and run the audit. Optionally add fontbakery's OpenType profile as a dev dependency, under the same pinning rules.
- **Changelog:** keep it in each family's FONTLOG, which the OFL needs anyway. Generate the release notes from it.

### Order of work

1. Confirm the decisions below.
2. Restructure: rename the repo, move Hand into `families/hand` and `fonts/hand`, refactor the build into `common.py`, check Hand's output is byte-identical, split README into README and CONTRIBUTING, update the Pages links.
3. Extend the stroker to support flat ends and sharp corners, and add outline offsetting for the SemiBold.
4. Add Trantor Caption first, as it is the more complete upstream: SemiBold, missing symbols, lowercase (review specimens), accents, kerning.
5. Add Trantor Mark: alternates to ss01/salt, SemiBold, lowercase (review specimens), accents, kerning. The `ss02` thin logo variant can follow later.
6. Update licence files: root OFL with all copyright lines, per-family OFL, LICENSE-CODE, disclaimers.
7. Site: shared CSS, landing page, three family pages with specimen and usage.
8. CI: `check.yml`, then `release.yml` and `make release`.
9. Tag `v1.000`, check the release assets and Pages, then optionally tell the upstream author.

### Decisions needed

1. **Names.** Series "Trantor", repo `trantor-type`, families Trantor Hand / Mark / Caption?
   1. Answer: Proposed names accepted
2. **Lowercase.** Unicase for Mark and Caption (proposed), or draw real lowercases as for Hand? Drawing them is a much bigger job and goes beyond anything in the show.
   1. Answer: Draw real lowercase for new fonts
   2. Follow-up: carry over each font's quirks (Caption's dots, Mark's broken strokes); review specimens before kerning
3. **Versioning.** One series-wide version and tag (proposed), or independent per-family releases?
   1. One series-wide version
4. **Licensing extras.** MIT for build code, and no new "Trantor" Reserved Font Name?
   1. Answer: Proposed accepted
5. **Weights.** Logo and One have one weight each. Ship them as a single "Regular" (proposed), or add a SemiBold to match Hand?
   1. Answer: Add semibold for the new fonts
   2. Follow-up: upstream outlines are Regular (400); SemiBold (600) is offset ~25% heavier, as for Hand
