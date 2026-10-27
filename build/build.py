#!/usr/bin/env python3
"""Build Trantor Hand from the Foundation Titles Hand capitals.

Takes the upstream v0.85 TrueType fonts, replaces the placeholder lowercase
(which duplicated the capitals) with newly drawn glyphs, adds the accented
letters and symbols needed for UK English, rebuilds kerning and metadata, and
writes TTF, WOFF2 and WOFF files plus a CSS @font-face stylesheet.

The upstream licence reserves the name "FoundationTitlesHand", so this
modified version has to be published under a different family name.
"""
import os
import unicodedata
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from glyphs import ACCENTS, ACCENT_UNICODE_NAMES, COMPOSITES, GLYPHS
from kerning import lowercase_pairs
from skeleton import outline

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "upstream" / "fonts" / "ttf" / "latest"
TTF_DIR = ROOT / "fonts" / "ttf"
WEB_DIR = ROOT / "fonts" / "webfonts"

FAMILY = "Trantor Hand"
PS_FAMILY = FAMILY.replace(" ", "")
CSS_FILE = "trantor-hand.css"
VERSION = "1.000"
# Font timestamps are pinned to the release date so rebuilds are byte-identical.
# Update alongside VERSION; SOURCE_DATE_EPOCH in the environment overrides it.
RELEASE_EPOCH = "1793059200"  # 2026-10-27T00:00:00Z
COPYRIGHT = (
    "Copyright (c) 2021, Roger Sperberg (https://github.com/rsperberg/foundation-titles-hand), "
    "with Reserved Font Name FoundationTitlesHand. "
    "Lowercase and Latin-1 additions copyright (c) 2026, Codecup Ltd."
)
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"

# Stroke widths measured from the upstream capitals (stem of I).
WEIGHTS = [
    dict(style="Regular", weight=400, stroke=80, source="FoundationTitlesHand-v0.85.ttf"),
    dict(style="SemiBold", weight=600, stroke=101, source="FoundationTitlesHand-SemiBold-v0.85.ttf"),
]

# Vertical metrics: ascender/descender for line spacing (close to upstream's
# 1097-unit line), and the clipping box is taken from the actual glyphs.
TYPO_ASCENDER = 840
TYPO_DESCENDER = -260


class Builder:
    def __init__(self, spec):
        self.spec = spec
        self.font = TTFont(UPSTREAM / spec["source"])
        self.glyf = self.font["glyf"]
        self.hmtx = self.font["hmtx"]
        self.order = list(self.font.getGlyphOrder())
        self.tops = {}

    def set_glyph(self, name, glyph, advance, unicode=None):
        if name not in self.order:
            self.order.append(name)
        self.glyf.glyphs[name] = glyph
        glyph.recalcBounds(self.glyf)
        self.hmtx[name] = (advance, getattr(glyph, "xMin", 0))
        if unicode is not None:
            for table in self.font["cmap"].tables:
                if table.isUnicode():
                    table.cmap[unicode] = name

    def draw(self, parts, dx=0):
        path = outline(parts, self.spec["stroke"])
        pen = TTGlyphPen(None)
        path.draw(Cu2QuPen(TransformPen(pen, (1, 0, 0, 1, dx, 0)), max_err=0.5))
        return pen.glyph()

    def drawn_glyphs(self):
        for name, g in GLYPHS.items():
            x_min, _, x_max, _ = outline(g.parts, self.spec["stroke"]).bounds
            dx = round(g.sb[0] - x_min)
            advance = round(x_max - x_min + g.sb[0] + g.sb[1])
            self.set_glyph(name, self.draw(g.parts, dx), advance, g.unicode or (ord(name) if len(name) == 1 else None))
            top = g.top if g.top is not None else (x_min + x_max) / 2
            self.tops[name] = top + dx
        for name, parts in ACCENTS.items():
            self.set_glyph(name, self.draw(parts), 0)

    def anchor(self, base):
        if base in self.tops:
            return self.tops[base]
        g = self.glyf[base]
        if base == "C":  # centre of the open bowl, not of the bounding box
            return g.xMin + (g.yMax - g.yMin) / 2
        if base == "A":  # the apex is off-centre
            coords, _, _ = g.getCoordinates(self.glyf)
            return max(coords, key=lambda pt: pt[1])[0]
        return (g.xMin + g.xMax) / 2

    def composites(self):
        for name, base, mark in COMPOSITES:
            accent = mark if mark == "cedilla" else mark + (".case" if base.isupper() else ".lc")
            pen = TTGlyphPen(self.glyf.glyphs)
            pen.addComponent("dotlessi" if base == "i" else base, (1, 0, 0, 1, 0, 0))
            pen.addComponent(accent, (1, 0, 0, 1, round(self.anchor(base)), 0))
            case = "CAPITAL" if base.isupper() else "SMALL"
            cp = ord(unicodedata.lookup(f"LATIN {case} LETTER {base.upper()} WITH {ACCENT_UNICODE_NAMES[mark]}"))
            self.set_glyph(name, pen.glyph(), self.hmtx[base][0], cp)

        # Ellipsis from three full stops, spaced a little tighter than "...".
        period = self.glyf["period"]
        step = period.xMax - period.xMin + 70
        pen = TTGlyphPen(self.glyf.glyphs)
        for i in range(3):
            pen.addComponent("period", (1, 0, 0, 1, i * step, 0))
        self.set_glyph("ellipsis", pen.glyph(), 2 * step + self.hmtx["period"][0], 0x2026)

        for table in self.font["cmap"].tables:
            if table.isUnicode():
                table.cmap[0x00A0] = "space"  # no-break space

    def groups(self):
        groups = {}
        for name, base, _ in COMPOSITES:
            groups.setdefault(base, [base]).append(name)
        for name in GLYPHS:
            if "." in name:
                base = name.split(".")[0]
                groups.setdefault(base, [base]).append(name)
        groups["i"] = ["i", "dotlessi"] + groups.get("i", [])[1:]
        return groups

    def features(self):
        groups = self.groups()
        upstream = self.font["kern"].kernTables[0].kernTable
        new_lowercase = set("abcdefghijklmnopqrstuvwxyz")
        kerning = {}
        for (left, right), value in upstream.items():
            if left in new_lowercase or right in new_lowercase:
                continue  # these referred to the old copies of the capitals
            for l in groups.get(left, [left]):
                for r in groups.get(right, [right]):
                    kerning[l, r] = value
        kerning.update(lowercase_pairs(groups))

        for tag in ("kern", "GPOS", "GSUB", "GDEF", "FFTM"):
            if tag in self.font:
                del self.font[tag]
        rules = "\n".join(f"  pos {l} {r} {v};" for (l, r), v in sorted(kerning.items()) if v)
        fea = f"""
languagesystem DFLT dflt;
languagesystem latn dflt;

feature kern {{
{rules}
}} kern;

feature ss01 {{
  featureNames {{ name "Title-sequence o and w"; }};
  sub o by o.ss01;
  sub w by w.ss01;
}} ss01;
"""
        addOpenTypeFeaturesFromString(self.font, fea)
        return len(kerning)

    def metadata(self):
        style, weight = self.spec["style"], self.spec["weight"]
        regular = style == "Regular"
        ps_name = f"{PS_FAMILY}-{style}"

        name = self.font["name"]
        name.names = []
        records = {
            0: COPYRIGHT,
            1: FAMILY if regular else f"{FAMILY} {style}",
            2: "Regular",
            3: f"{VERSION};{ps_name}",
            4: f"{FAMILY} {style}",
            5: f"Version {VERSION}",
            6: ps_name,
            9: "Roger Sperberg (capitals); lowercase and extensions added 2026",
            10: "Based on Foundation Titles Hand v0.85 by Roger Sperberg, with an added lowercase.",
            13: LICENSE,
            14: LICENSE_URL,
        }
        if not regular:
            records.update({16: FAMILY, 17: style})
        for name_id, text in records.items():
            name.setName(text, name_id, 3, 1, 0x409)
            name.setName(text, name_id, 1, 0, 0)

        y_min = min(getattr(self.glyf[g], "yMin", 0) for g in self.order)
        y_max = max(getattr(self.glyf[g], "yMax", 0) for g in self.order)

        os2 = self.font["OS/2"]
        os2.version = 4
        os2.usWeightClass = weight
        os2.fsSelection = (1 << 6 if regular else 0) | (1 << 7)  # REGULAR, USE_TYPO_METRICS
        os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = TYPO_ASCENDER, TYPO_DESCENDER, 0
        os2.usWinAscent = max(TYPO_ASCENDER, y_max)
        os2.usWinDescent = max(-TYPO_DESCENDER, -y_min)
        stroke = self.spec["stroke"]
        os2.sxHeight = round(470 + stroke / 2)
        os2.sCapHeight = round(718 + stroke / 2)
        os2.usDefaultChar, os2.usBreakChar, os2.usMaxContext = 0, 32, 2
        os2.ulCodePageRange1, os2.ulCodePageRange2 = 1, 0  # Latin 1
        os2.recalcUnicodeRanges(self.font)

        hhea = self.font["hhea"]
        hhea.ascent, hhea.descent, hhea.lineGap = TYPO_ASCENDER, TYPO_DESCENDER, 0

        head = self.font["head"]
        head.fontRevision = float(VERSION)
        head.macStyle = 0
        self.font["gasp"].gaspRange = {0xFFFF: 0x000F}  # unhinted: smooth at all sizes
        self.font["post"].underlinePosition = -150
        return ps_name

    def build(self):
        self.drawn_glyphs()
        self.composites()
        self.font.setGlyphOrder(self.order)
        self.glyf.setGlyphOrder(self.order)
        ps_name = self.metadata()
        pairs = self.features()
        self.font["OS/2"].recalcAvgCharWidth(self.font)

        TTF_DIR.mkdir(parents=True, exist_ok=True)
        WEB_DIR.mkdir(parents=True, exist_ok=True)
        ttf = TTF_DIR / f"{ps_name}.ttf"
        self.font.save(ttf)
        for flavor in ("woff2", "woff"):
            web = TTFont(ttf)
            web.flavor = flavor
            web.save(WEB_DIR / f"{ps_name}.{flavor}")
        print(f"{ps_name}: {len(self.order)} glyphs, {pairs} kerning pairs")
        return ps_name


def write_css(fonts):
    rules = []
    for spec, ps_name in fonts:
        rules.append(f"""@font-face {{
  font-family: "{FAMILY}";
  src: url("{ps_name}.woff2") format("woff2"),
       url("{ps_name}.woff") format("woff");
  font-weight: {spec["weight"]};
  font-style: normal;
  font-display: swap;
}}
""")
    (WEB_DIR / CSS_FILE).write_text("\n".join(rules))


def main():
    os.environ.setdefault("SOURCE_DATE_EPOCH", RELEASE_EPOCH)
    fonts = [(spec, Builder(spec).build()) for spec in WEIGHTS]
    write_css(fonts)


if __name__ == "__main__":
    main()
