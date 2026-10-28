"""Skeleton designs for the new glyphs.

All coordinates are stroke centre lines in font units (1000 UPM). The
upstream capitals sit on a centre-line baseline of 0 with a centre-line cap
height of about 718, so the round stroke ends overshoot both lines by half the
stroke width. The lowercase follows the same convention.

The lowercase is geometric to match the capitals: circular bowls, semicircular
arches and straight diagonals. `sb` is the (left, right) side bearing measured
from the ink, and `top` is the centre-line x used to place accents (it
defaults to the middle of the ink).
"""
from skeleton import Disc, Glyph, Stroke, arc, circle

X = 470  # x-height
ASC = 740  # ascender
DESC = -220  # descender
DOT = 660  # centre of the i and j dots
R = X / 2  # bowl radius

STEM = 60  # side bearing beside a vertical stem
ROUND = 40  # side bearing beside a bowl
DIAG = 15  # side bearing beside a diagonal


def bowl():
    return circle(R, R, R)


def arch(x, width, depth=0):
    """An n-arch from the stem at x, ending in a right-hand stem down to depth."""
    r = width / 2
    return Stroke(x, X - r).arc(x + r, X - r, r, 180, 0).line(x + width, depth)


GLYPHS = {
    "a": Glyph([bowl(), Stroke(X, X).line(X, 0)], (ROUND, STEM), top=R),
    "b": Glyph([Stroke(0, ASC).line(0, 0), bowl()], (STEM, ROUND), top=R),
    "c": Glyph([arc(R, R, R, 45, 315)], (ROUND, 25), top=R),
    "d": Glyph([bowl(), Stroke(X, ASC).line(X, 0)], (ROUND, STEM), top=R),
    "e": Glyph([Stroke(0, R).line(X, R).arc(R, R, R, 0, 320)], (ROUND, 30), top=R),
    "f": Glyph(
        [Stroke(0, 0).line(0, ASC - 130).arc(130, ASC - 130, 130, 180, 40),
         Stroke(-100, X).line(190, X)],
        (DIAG, 5), top=0),
    "g": Glyph(
        [bowl(), Stroke(X, X).line(X, -40).arc(X - 170, -40, 170, 0, -160)],
        (ROUND, STEM), top=R),
    "h": Glyph([Stroke(0, ASC).line(0, 0), arch(0, 380)], (STEM, STEM), top=190),
    "i": Glyph([Stroke(0, X).line(0, 0), Disc(0, DOT)], (STEM, STEM)),
    "j": Glyph(
        [Stroke(0, X).line(0, -80).arc(-130, -80, 130, 0, -160), Disc(0, DOT)],
        (-190, STEM), top=0),  # the hook tucks under the previous letter
    "k": Glyph(
        [Stroke(0, ASC).line(0, 0), Stroke(330, X).line(0, 170),
         Stroke(130, 288).line(350, 0)],
        (STEM, DIAG)),
    "l": Glyph([Stroke(0, ASC).line(0, 110).arc(110, 110, 110, 180, 270)], (STEM, 25), top=0),
    "m": Glyph(
        [Stroke(0, X).line(0, 0), arch(0, 300), arch(300, 300)], (STEM, STEM), top=300),
    "n": Glyph([Stroke(0, X).line(0, 0), arch(0, 380)], (STEM, STEM), top=190),
    "o": Glyph([bowl()], (ROUND, ROUND)),
    "p": Glyph([Stroke(0, X).line(0, DESC), bowl()], (STEM, ROUND), top=R),
    "q": Glyph([bowl(), Stroke(X, X).line(X, DESC)], (ROUND, STEM), top=R),
    "r": Glyph([Stroke(0, X).line(0, 0), arc(190, 280, 190, 180, 75)], (STEM, 10), top=120),
    "s": Glyph(
        [arc(165, 357, 125, 25, 270, ry=113).arc(165, 122, 140, 90, -155, ry=122)],
        (35, 35)),
    "t": Glyph(
        [Stroke(0, 650).line(0, 110).arc(110, 110, 110, 180, 270),
         Stroke(-100, X).line(190, X)],
        (DIAG, 20), top=0),
    "u": Glyph(
        [Stroke(0, X).line(0, 190).arc(190, 190, 190, 180, 360).line(380, X),
         Stroke(380, X).line(380, 0)],
        (STEM, STEM), top=190),
    "v": Glyph([Stroke(0, X).line(210, 0).line(420, X)], (DIAG, DIAG)),
    "w": Glyph(
        [Stroke(0, X).line(150, 0).line(300, X).line(450, 0).line(600, X)], (DIAG, DIAG)),
    "x": Glyph([Stroke(0, 0).line(400, X), Stroke(0, X).line(400, 0)], (20, 20)),
    "y": Glyph(
        [Stroke(0, X).line(210, 0), Stroke(420, X).line(112, DESC)], (DIAG, DIAG), top=210),
    "z": Glyph([Stroke(10, X).line(380, X).line(0, 0).line(390, 0)], (35, 35)),
    "dotlessi": Glyph([Stroke(0, X).line(0, 0)], (STEM, STEM), unicode=0x0131, top=0),

    # Stylistic set 1: the dotted o and crossed w of the title-sequence capitals.
    "o.ss01": Glyph([bowl(), Disc(R, R)], (ROUND, ROUND)),
    "w.ss01": Glyph(
        [Stroke(0, X).line(170, 0).line(340, X), Stroke(240, X).line(410, 0).line(580, X)],
        (DIAG, DIAG)),

    # Symbols for UK English.
    "sterling": Glyph(
        [arc(230, 560, 150, 20, 180).line(80, 0), Stroke(0, 0).line(420, 0),
         Stroke(-10, 330).line(260, 330)],
        (ROUND, ROUND), unicode=0x00A3),
    "Euro": Glyph(
        [arc(350, 359, 340, 45, 315), Stroke(-60, 280).line(330, 280),
         Stroke(-60, 440).line(330, 440)],
        (30, 60), unicode=0x20AC),
    "bullet": Glyph([Disc(0, 300, 110)], (ROUND, ROUND), unicode=0x2022),
    "degree": Glyph([circle(0, 620, 95)], (ROUND, ROUND), unicode=0x00B0),
}

# Accents are drawn centred on x=0 at their final height: ".lc" above the
# x-height and ".case" (flatter) above the capitals.
ACCENTS = {
    "grave.lc": [Stroke(45, 610).line(-45, 720)],
    "acute.lc": [Stroke(-45, 610).line(45, 720)],
    "circumflex.lc": [Stroke(-95, 610).line(0, 715).line(95, 610)],
    "dieresis.lc": [Disc(-95, 655), Disc(95, 655)],
    "tilde.lc": [Stroke(-110, 630).curve((-50, 740), (50, 580), (110, 690))],
    "grave.case": [Stroke(50, 860).line(-50, 940)],
    "acute.case": [Stroke(-50, 860).line(50, 940)],
    "circumflex.case": [Stroke(-100, 860).line(0, 935).line(100, 860)],
    "dieresis.case": [Disc(-100, 890), Disc(100, 890)],
    "tilde.case": [Stroke(-115, 870).curve((-55, 960), (55, 830), (115, 920))],
    "cedilla": [Stroke(0, -20).line(0, -80).arc(0, -135, 55, 90, -150)],
}
