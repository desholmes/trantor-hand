"""Trantor Mark: Foundation Logo with a lowercase and a SemiBold.

Takes the upstream v0.3 TrueType font as the Regular, moves the alternate
capitals that upstream kept in the lowercase slots (the thinner logo's E F K
P S W X Y Z) to stylistic set 1, draws a lowercase in their place, adds the
accented letters and symbols needed for UK English, and thickens the result
to make the SemiBold.

The upstream licence reserves the name "FoundationLogo", so this modified
version has to be published under a different family name.
"""
import copy

from common import ROOT, Builder

from .glyphs import ACCENTS, GLYPHS

ALTERNATES = "efkpswxyz"


class Mark(Builder):
    KEY = "mark"
    FAMILY = "Trantor Mark"
    CSS_FILE = "trantor-mark.css"
    UPSTREAM = ROOT / "families" / "mark" / "upstream" / "fonts" / "ttf" / "latest"
    COPYRIGHT = (
        "Copyright (c) 2021, Roger Sperberg (https://github.com/rsperberg/foundation-logo), "
        "with Reserved Font Name FoundationLogo. "
        "Lowercase, SemiBold and Latin-1 additions copyright (c) 2026, Codecup Ltd."
    )
    DESIGNER = "Roger Sperberg (capitals); lowercase, SemiBold and extensions added 2026"
    DESCRIPTION = "Based on Foundation Logo v0.3 by Roger Sperberg, with an added lowercase and SemiBold."

    # The upstream stem (I) is 121 units. SemiBold is about 26% heavier, the
    # same step as Trantor Hand's weights.
    WEIGHTS = [
        dict(style="Regular", weight=400, stroke=121, source="FoundationLogo.ttf"),
        dict(style="SemiBold", weight=600, stroke=121, embolden=32, source="FoundationLogo.ttf"),
    ]
    CAP = "flat"
    JOIN = "sharp"

    GLYPHS = GLYPHS
    ACCENTS = ACCENTS
    _subs = [(ch.upper(), ch.upper() + ".ss01") for ch in ALTERNATES]
    STYLISTIC_SETS = [("ss01", "Alternate logo capitals", _subs), ("salt", None, _subs)]

    # Accented capitals reach about 1040 and descenders -240.
    TYPO_ASCENDER = 980
    TYPO_DESCENDER = -260

    def prepare(self):
        # Keep the alternate capitals, and their kerning, under new names
        # before the lowercase is drawn over them.
        for ch in ALTERNATES:
            name = ch.upper() + ".ss01"
            self.glyf.glyphs[name] = copy.deepcopy(self.glyf[ch])
            self.hmtx[name] = self.hmtx[ch]
            self.order.append(name)
        renamed = {ch: ch.upper() + ".ss01" for ch in ALTERNATES}
        kern = self.font["kern"].kernTables[0]
        kern.kernTable = {(renamed.get(l, l), renamed.get(r, r)): v for (l, r), v in kern.kernTable.items()}

    def heights(self):
        return round(self.glyf["x"].yMax), round(self.glyf["H"].yMax)

    def capital_anchor(self, base, glyph):
        # Centre accents on the main shape, not on the detached dots of A, E and O.
        coords, ends, _ = glyph.getCoordinates(self.glyf)
        start, best = 0, None
        for end in ends:
            xs = [x for x, _ in coords[start:end + 1]]
            ys = [y for _, y in coords[start:end + 1]]
            size = (max(xs) - min(xs)) * (max(ys) - min(ys))
            if best is None or size > best[0]:
                best = (size, (min(xs) + max(xs)) / 2)
            start = end + 1
        if base == "A":  # the apex is off-centre
            return max(coords, key=lambda pt: pt[1])[0]
        return best[1]
