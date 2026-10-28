"""Trantor Caption: Foundation One with a lowercase and a SemiBold.

Takes the upstream v0.4 TrueType font as the Regular, fills in the Basic Latin
symbols it lacks, replaces the placeholder lowercase (which duplicated the
capitals) with newly drawn glyphs, adds the accented letters and symbols
needed for UK English, and thickens the result to make the SemiBold.

The upstream licence reserves the name "FoundationOne", so this modified
version has to be published under a different family name.
"""
from common import ROOT, Builder

from .glyphs import ACCENTS, GLYPHS


class Caption(Builder):
    KEY = "caption"
    FAMILY = "Trantor Caption"
    CSS_FILE = "trantor-caption.css"
    UPSTREAM = ROOT / "families" / "caption" / "upstream" / "fonts" / "ttf" / "v0.4"
    COPYRIGHT = (
        "Copyright (c) 2021, Roger Sperberg (https://github.com/rsperberg/foundation-one), "
        "with Reserved Font Name FoundationOne. "
        "Lowercase, SemiBold and Latin-1 additions copyright (c) 2026, Codecup Ltd."
    )
    DESIGNER = "Roger Sperberg (capitals); lowercase, SemiBold and extensions added 2026"
    DESCRIPTION = "Based on Foundation One v0.4 by Roger Sperberg, with an added lowercase and SemiBold."

    # The upstream stem (I) is 116 units. SemiBold is about 26% heavier, the
    # same step as Trantor Hand's weights.
    WEIGHTS = [
        dict(style="Regular", weight=400, stroke=116, source="FoundationOne.ttf"),
        dict(style="SemiBold", weight=600, stroke=116, embolden=30, source="FoundationOne.ttf"),
    ]
    CAP = "flat"
    JOIN = "sharp"

    GLYPHS = GLYPHS
    ACCENTS = ACCENTS

    # Accented capitals reach about 1000 and descenders -230.
    TYPO_ASCENDER = 950
    TYPO_DESCENDER = -250

    def heights(self):
        return round(self.glyf["x"].yMax), round(self.glyf["H"].yMax)

    def capital_anchor(self, base, glyph):
        if base == "A":  # the apex is off-centre
            coords, _, _ = glyph.getCoordinates(self.glyf)
            return max(coords, key=lambda pt: pt[1])[0]
        return super().capital_anchor(base, glyph)
