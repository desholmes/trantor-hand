"""Shared build steps for the Trantor fonts.

Each family subclasses Builder and sets its names, upstream sources, glyph
designs and metrics as class attributes. Builder takes the upstream TrueType
font for one weight, adds the new glyphs and composites, rebuilds kerning and
metadata, and writes TTF, WOFF2 and WOFF files plus a CSS @font-face
stylesheet.
"""
import unicodedata
from pathlib import Path

import pathops
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from skeleton import outline

ROOT = Path(__file__).resolve().parent.parent

# One version for the whole series.
VERSION = "1.000"
# Font timestamps are pinned to the release date so rebuilds are byte-identical.
# Update alongside VERSION; SOURCE_DATE_EPOCH in the environment overrides it.
RELEASE_EPOCH = "1793059200"  # 2026-10-27T00:00:00Z

LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"

LOWERCASE = set("abcdefghijklmnopqrstuvwxyz")

# Accented letters used in UK English loanwords (café, naïve, façade, rôle,
# señor, Zoë, crème brûlée...).
MARKS = {"grave": "GRAVE", "acute": "ACUTE", "circumflex": "CIRCUMFLEX", "dieresis": "DIAERESIS"}
COMPOSITES = [(v + m, v, m) for v in "aeiouAEIOU" for m in MARKS]
COMPOSITES += [("ccedilla", "c", "cedilla"), ("Ccedilla", "C", "cedilla"),
               ("ntilde", "n", "tilde"), ("Ntilde", "N", "tilde")]
ACCENT_UNICODE_NAMES = dict(MARKS, cedilla="CEDILLA", tilde="TILDE")


class Builder:
    # Set by each family.
    KEY = None  # folder name under families/ and fonts/
    FAMILY = None
    CSS_FILE = None
    UPSTREAM = None  # folder holding the upstream TTFs
    COPYRIGHT = None
    DESIGNER = None
    DESCRIPTION = None
    # dicts: style, weight, stroke, source and, for a weight made by
    # thickening the upstream outlines, embolden (the extra stroke width).
    WEIGHTS = []
    CAP = "round"  # stroke ends: round or flat
    JOIN = "round"  # stroke corners: round or sharp
    GLYPHS = {}
    ACCENTS = {}
    COMPOSITES = COMPOSITES  # (name, base, mark)
    ACCENT_UNICODE_NAMES = ACCENT_UNICODE_NAMES
    # (tag, name, [(glyph, alternate), ...]); the name is shown for ssNN tags.
    STYLISTIC_SETS = []
    TYPO_ASCENDER = 840
    TYPO_DESCENDER = -260
    X_HEIGHT = 470  # centre-line heights; the stroke adds half its width
    CAP_HEIGHT = 718

    def __init__(self, spec):
        self.spec = spec
        self.font = TTFont(self.UPSTREAM / spec["source"])
        self.glyf = self.font["glyf"]
        self.hmtx = self.font["hmtx"]
        self.order = list(self.font.getGlyphOrder())
        self.tops = {}

    @property
    def ps_family(self):
        return self.FAMILY.replace(" ", "")

    @classmethod
    def ttf_dir(cls):
        return ROOT / "fonts" / cls.KEY / "ttf"

    @classmethod
    def web_dir(cls):
        return ROOT / "fonts" / cls.KEY / "webfonts"

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

    def outline(self, parts):
        return outline(parts, self.spec["stroke"], self.CAP, self.JOIN)

    def draw(self, parts, dx=0):
        path = self.outline(parts)
        pen = TTGlyphPen(None)
        path.draw(Cu2QuPen(TransformPen(pen, (1, 0, 0, 1, dx, 0)), max_err=0.5))
        return pen.glyph()

    def drawn_glyphs(self):
        for name, g in self.GLYPHS.items():
            x_min, _, x_max, _ = self.outline(g.parts).bounds
            dx = round(g.sb[0] - x_min)
            advance = round(x_max - x_min + g.sb[0] + g.sb[1])
            self.set_glyph(name, self.draw(g.parts, dx), advance, g.unicode or (ord(name) if len(name) == 1 else None))
            top = g.top if g.top is not None else (x_min + x_max) / 2
            self.tops[name] = top + dx
        for name, parts in self.ACCENTS.items():
            self.set_glyph(name, self.draw(parts), 0)

    def embolden(self, extra):
        """Thicken every outline by `extra` (half on each side), keeping the side
        bearings, then rescale vertically so the baseline and cap height stay
        where they were. This makes the vertical strokes `extra` heavier and
        the horizontals slightly less, as in most bold designs."""
        glyph_set = self.font.getGlyphSet()
        height = self.glyf["H"].yMax
        half = extra / 2
        scale = height / (height + extra)
        for name in self.order:
            glyph = self.glyf[name]
            if glyph.isComposite() or glyph.numberOfContours == 0:
                continue
            path = pathops.Path()
            glyph_set[name].draw(path.getPen())
            path.simplify(clockwise=True)
            ring = pathops.Path(path)
            ring.stroke(extra, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
            path = pathops.op(path, ring, pathops.PathOp.UNION, clockwise=True)
            path.convertConicsToQuads()
            pen = TTGlyphPen(None)
            path.draw(Cu2QuPen(TransformPen(pen, (1, 0, 0, scale, half, half * scale)), max_err=0.5))
            self.glyf.glyphs[name] = pen.glyph()
        for name in self.order:
            advance, _ = self.hmtx[name]
            glyph = self.glyf[name]
            glyph.recalcBounds(self.glyf)
            self.hmtx[name] = (advance + extra if advance else 0, getattr(glyph, "xMin", 0))

    def capital_anchor(self, base, glyph):
        """The x to centre an accent on, for an upstream glyph."""
        return (glyph.xMin + glyph.xMax) / 2

    def anchor(self, base):
        if base in self.tops:
            return self.tops[base]
        return self.capital_anchor(base, self.glyf[base])

    def component_base(self, base):
        """The glyph an accented letter is built on."""
        return "dotlessi" if base == "i" else base

    def composites(self):
        for name, base, mark in self.COMPOSITES:
            accent = mark if mark == "cedilla" else mark + (".case" if base.isupper() else ".lc")
            pen = TTGlyphPen(self.glyf.glyphs)
            pen.addComponent(self.component_base(base), (1, 0, 0, 1, 0, 0))
            pen.addComponent(accent, (1, 0, 0, 1, round(self.anchor(base)), 0))
            case = "CAPITAL" if base.isupper() else "SMALL"
            cp = ord(unicodedata.lookup(f"LATIN {case} LETTER {base.upper()} WITH {self.ACCENT_UNICODE_NAMES[mark]}"))
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
        for name, base, _ in self.COMPOSITES:
            groups.setdefault(base, [base]).append(name)
        for name in self.GLYPHS:
            if "." in name:
                base = name.split(".")[0]
                groups.setdefault(base, [base]).append(name)
        groups["i"] = ["i", "dotlessi"] + groups.get("i", [])[1:]
        return groups

    @staticmethod
    def expand_pairs(pairs, groups, punctuation, scale=1):
        """Kerning from (left, right, value) rules. Each side is a string of
        characters; a letter also stands for its accented and stylistic-set
        forms. Values are multiplied by scale and rounded to 5 units."""
        def names(side):
            out = []
            for ch in side:
                name = punctuation.get(ch, ch)
                out += groups.get(name, [name])
            return out

        kerning = {}
        for left, right, value in pairs:
            for l in names(left):
                for r in names(right):
                    kerning[l, r] = value if scale == 1 else round(value * scale / 5) * 5
        return kerning

    def new_pairs(self, groups):
        """Kerning for the new glyphs: {(left, right): value}."""
        return {}

    def features(self):
        groups = self.groups()
        upstream = self.font["kern"].kernTables[0].kernTable
        kerning = {}
        for (left, right), value in upstream.items():
            if left in LOWERCASE or right in LOWERCASE:
                continue  # these referred to the old copies of the capitals
            for l in groups.get(left, [left]):
                for r in groups.get(right, [right]):
                    kerning[l, r] = value
        kerning.update(self.new_pairs(groups))

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
"""
        for tag, label, subs in self.STYLISTIC_SETS:
            body = "\n".join(f"  sub {g} by {alt};" for g, alt in subs)
            if tag.startswith("ss"):
                body = f'  featureNames {{ name "{label}"; }};\n' + body
            fea += f"""
feature {tag} {{
{body}
}} {tag};
"""
        addOpenTypeFeaturesFromString(self.font, fea)
        return len(kerning)

    def metadata(self):
        style, weight = self.spec["style"], self.spec["weight"]
        regular = style == "Regular"
        ps_name = f"{self.ps_family}-{style}"

        name = self.font["name"]
        name.names = []
        records = {
            0: self.COPYRIGHT,
            1: self.FAMILY if regular else f"{self.FAMILY} {style}",
            2: "Regular",
            3: f"{VERSION};{ps_name}",
            4: f"{self.FAMILY} {style}",
            5: f"Version {VERSION}",
            6: ps_name,
            9: self.DESIGNER,
            10: self.DESCRIPTION,
            13: LICENSE,
            14: LICENSE_URL,
        }
        if not regular:
            records.update({16: self.FAMILY, 17: style})
        for name_id, text in records.items():
            name.setName(text, name_id, 3, 1, 0x409)
            name.setName(text, name_id, 1, 0, 0)

        y_min = min(getattr(self.glyf[g], "yMin", 0) for g in self.order)
        y_max = max(getattr(self.glyf[g], "yMax", 0) for g in self.order)

        os2 = self.font["OS/2"]
        os2.version = 4
        os2.usWeightClass = weight
        os2.fsSelection = (1 << 6 if regular else 0) | (1 << 7)  # REGULAR, USE_TYPO_METRICS
        os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = self.TYPO_ASCENDER, self.TYPO_DESCENDER, 0
        os2.usWinAscent = max(self.TYPO_ASCENDER, y_max)
        os2.usWinDescent = max(-self.TYPO_DESCENDER, -y_min)
        os2.sxHeight, os2.sCapHeight = self.heights()
        os2.usDefaultChar, os2.usBreakChar, os2.usMaxContext = 0, 32, 2
        os2.ulCodePageRange1, os2.ulCodePageRange2 = 1, 0  # Latin 1
        os2.recalcUnicodeRanges(self.font)

        hhea = self.font["hhea"]
        hhea.ascent, hhea.descent, hhea.lineGap = self.TYPO_ASCENDER, self.TYPO_DESCENDER, 0

        head = self.font["head"]
        head.fontRevision = float(VERSION)
        head.macStyle = 0
        self.font["gasp"].gaspRange = {0xFFFF: 0x000F}  # unhinted: smooth at all sizes
        self.font["post"].underlinePosition = -150
        return ps_name

    def heights(self):
        """x-height and cap height of the ink, for OS/2."""
        stroke = self.spec["stroke"]
        return round(self.X_HEIGHT + stroke / 2), round(self.CAP_HEIGHT + stroke / 2)

    def prepare(self):
        """Adjust the upstream glyphs before anything is added."""

    def build(self):
        self.prepare()
        self.drawn_glyphs()
        self.composites()
        if self.spec.get("embolden"):
            self.embolden(self.spec["embolden"])
        self.font.setGlyphOrder(self.order)
        self.glyf.setGlyphOrder(self.order)
        ps_name = self.metadata()
        pairs = self.features()
        self.font["OS/2"].recalcAvgCharWidth(self.font)

        ttf_dir, web_dir = self.ttf_dir(), self.web_dir()
        ttf_dir.mkdir(parents=True, exist_ok=True)
        web_dir.mkdir(parents=True, exist_ok=True)
        ttf = ttf_dir / f"{ps_name}.ttf"
        self.font.save(ttf)
        for flavor in ("woff2", "woff"):
            web = TTFont(ttf)
            web.flavor = flavor
            web.save(web_dir / f"{ps_name}.{flavor}")
        print(f"{ps_name}: {len(self.order)} glyphs, {pairs} kerning pairs")
        return ps_name

    @classmethod
    def build_family(cls):
        for spec in cls.WEIGHTS:
            cls(spec).build()
        (cls.web_dir() / cls.CSS_FILE).write_text(cls.css())

    @classmethod
    def css(cls, prefix=""):
        """@font-face rules for every weight; prefix is the path from the
        stylesheet to the webfonts folder."""
        rules = []
        for spec in cls.WEIGHTS:
            ps_name = f"{cls.FAMILY.replace(' ', '')}-{spec['style']}"
            rules.append(f"""@font-face {{
  font-family: "{cls.FAMILY}";
  src: url("{prefix}{ps_name}.woff2") format("woff2"),
       url("{prefix}{ps_name}.woff") format("woff");
  font-weight: {spec["weight"]};
  font-style: normal;
  font-display: swap;
}}
""")
        return "\n".join(rules)
