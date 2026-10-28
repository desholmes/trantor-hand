"""Kerning for the Trantor Mark lowercase and new glyphs.

Each side of a pair is a string of characters; a letter also stands for its
accented and stylistic-set forms. The upstream capital-to-capital kerning is
kept as it is (see common.py). Capitals also stand for their ss01
alternates. Values are larger than Trantor Hand's, as the upstream capital
kerning is.
"""
from common import Builder

PUNCTUATION = {
    ".": "period", ",": "comma", "'": "quotesingle", '"': "quotedbl",
    "’": "quoteright", "”": "quotedblright", ")": "parenright",
    "]": "bracketright", "}": "braceright", "?": "question", "!": "exclam",
}

ROUNDS = "acegoqs"

PAIRS = [
    ("T", ROUNDS, -120), ("T", "mnpruvwxyz", -90),
    ("V", ROUNDS, -85), ("V", "mnpruy", -45),
    ("W", ROUNDS, -70), ("W", "mnpruy", -40),
    ("Y", ROUNDS, -110), ("Y", "mnpruvwxyz", -70),
    ("F", "aceoqs", -70), ("P", "aceoqs", -60),
    ("K", "aceoq", -35), ("X", "aceoq", -30),
    ("A", "vwy", -45), ("L", "vwy", -60), ("A", "t", -20),
    ("r", "acdegoq", -20), ("r", ".,", -90),
    ("vy", ".,", -70), ("w", ".,", -60), ("f", ".,", -60),
    ("fvy", "aceoq", -20), ("w", "aceoq", -15),
    ("ceo", "vwxy", -20), ("kx", "aceoq", -20),
    ("f", "'\"’”)]}?!", 40),
]


def lowercase_pairs(groups, alternates):
    """Return {(left, right): value} for PAIRS, expanding letters to their
    groups and capitals to their ss01 alternates."""
    groups = dict(groups)
    for ch in alternates:
        cap = ch.upper()
        groups[cap] = groups.get(cap, [cap]) + [cap + ".ss01"]
    return Builder.expand_pairs(PAIRS, groups, PUNCTUATION)
