"""Kerning for the lowercase and new glyphs.

Each side of a pair is a string of characters; a letter also stands for its
accented and stylistic-set forms. The upstream capital-to-capital kerning is
kept as it is (see build.py).
"""
PUNCTUATION = {
    ".": "period", ",": "comma", "'": "quotesingle", '"': "quotedbl",
    "’": "quoteright", "”": "quotedblright", ")": "parenright",
    "]": "bracketright", "}": "braceright", "?": "question", "!": "exclam",
}

ROUNDS = "acegoqs"

PAIRS = [
    ("T", ROUNDS, -100), ("T", "mnpruvwxyz", -80),
    ("V", ROUNDS, -70), ("V", "mnpruy", -40),
    ("W", ROUNDS, -60), ("W", "mnpruy", -35),
    ("Y", ROUNDS, -90), ("Y", "mnpruvwxyz", -60),
    ("F", "aceoqs", -60), ("P", "aceoqs", -50),
    ("K", "aceoq", -30), ("X", "aceoq", -25),
    ("AL", "vwy", -40), ("A", "t", -20),
    ("r", "acdegoq", -15), ("r", ".,", -70),
    ("vy", ".,", -60), ("w", ".,", -50), ("f", ".,", -50),
    ("fvy", "aceoq", -15), ("w", "aceoq", -10),
    ("ceo", "vwxy", -15), ("kx", "aceoq", -15),
    ("f", "'\"’”)]}?!", 30),
]


def expand(side, groups):
    names = []
    for ch in side:
        name = PUNCTUATION.get(ch, ch)
        names += groups.get(name, [name])
    return names


def lowercase_pairs(groups):
    """Return {(left, right): value} for PAIRS, expanding letters to their groups."""
    kerning = {}
    for left, right, value in PAIRS:
        for l in expand(left, groups):
            for r in expand(right, groups):
                kerning[l, r] = value
    return kerning
