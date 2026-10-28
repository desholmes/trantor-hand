"""Kerning for the Trantor Caption lowercase and new glyphs.

Each side of a pair is a string of characters; a letter also stands for its
accented and stylistic-set forms. The upstream capital-to-capital kerning is
kept as it is (see common.py). Values are larger than Trantor Hand's, as the
upstream capital kerning is.
"""
from common import Builder

PUNCTUATION = {
    ".": "period", ",": "comma", "'": "quotesingle", '"': "quotedbl",
    "’": "quoteright", "”": "quotedblright", ")": "parenright",
    "]": "bracketright", "}": "braceright", "?": "question", "!": "exclam",
}

ROUNDS = "acegoqs"

PAIRS = [
    ("T", ROUNDS, -130), ("T", "mnpruvwxyz", -100),
    ("V", ROUNDS, -90), ("V", "mnpruy", -50),
    ("W", ROUNDS, -70), ("W", "mnpruy", -40),
    ("Y", ROUNDS, -120), ("Y", "mnpruvwxyz", -80),
    ("F", "aceoqs", -80), ("P", "aceoqs", -70),
    ("K", "aceoq", -40), ("X", "aceoq", -30),
    ("A", "vwy", -50), ("L", "vwy", -60), ("A", "t", -25),
    ("r", "acdegoq", -25), ("r", ".,", -100),
    ("vy", ".,", -80), ("w", ".,", -60), ("f", ".,", -40),
    ("fvy", "aceoq", -20), ("w", "aceoq", -15),
    ("ceo", "vwxy", -20), ("kx", "aceoq", -20),
    ("f", "'\"’”)]}?!", 40),
]


def lowercase_pairs(groups):
    """Return {(left, right): value} for PAIRS, expanding letters to their groups."""
    return Builder.expand_pairs(PAIRS, groups, PUNCTUATION)
