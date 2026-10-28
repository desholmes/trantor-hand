"""Trantor Hand: Foundation Titles Hand with a new lowercase.

Takes the upstream v0.85 TrueType fonts, replaces the placeholder lowercase
(which duplicated the capitals) with newly drawn glyphs and adds the accented
letters and symbols needed for UK English.

The upstream licence reserves the name "FoundationTitlesHand", so this
modified version has to be published under a different family name.
"""
from common import ROOT, Builder

from .glyphs import ACCENTS, GLYPHS
from .kerning import lowercase_pairs


class Hand(Builder):
    KEY = "hand"
    FAMILY = "Trantor Hand"
    CSS_FILE = "trantor-hand.css"
    UPSTREAM = ROOT / "families" / "hand" / "upstream" / "fonts" / "ttf" / "latest"
    COPYRIGHT = (
        "Copyright (c) 2021, Roger Sperberg (https://github.com/rsperberg/foundation-titles-hand), "
        "with Reserved Font Name FoundationTitlesHand. "
        "Lowercase and Latin-1 additions copyright (c) 2026, Codecup Ltd."
    )
    DESIGNER = "Roger Sperberg (capitals); lowercase and extensions added 2026"
    DESCRIPTION = "Based on Foundation Titles Hand v0.85 by Roger Sperberg, with an added lowercase."

    # Stroke widths measured from the upstream capitals (stem of I).
    WEIGHTS = [
        dict(style="Regular", weight=400, stroke=80, source="FoundationTitlesHand-v0.85.ttf"),
        dict(style="SemiBold", weight=600, stroke=101, source="FoundationTitlesHand-SemiBold-v0.85.ttf"),
    ]

    GLYPHS = GLYPHS
    ACCENTS = ACCENTS
    STYLISTIC_SETS = [("ss01", "Title-sequence o and w", [("o", "o.ss01"), ("w", "w.ss01")])]

    # Vertical metrics: ascender/descender for line spacing (close to upstream's
    # 1097-unit line), and the clipping box is taken from the actual glyphs.
    TYPO_ASCENDER = 840
    TYPO_DESCENDER = -260

    def capital_anchor(self, base, glyph):
        if base == "C":  # centre of the open bowl, not of the bounding box
            return glyph.xMin + (glyph.yMax - glyph.yMin) / 2
        if base == "A":  # the apex is off-centre
            coords, _, _ = glyph.getCoordinates(self.glyf)
            return max(coords, key=lambda pt: pt[1])[0]
        return super().capital_anchor(base, glyph)

    def new_pairs(self, groups):
        return lowercase_pairs(groups)
