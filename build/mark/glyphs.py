"""Skeleton designs for the new Trantor Mark glyphs.

All coordinates are stroke centre lines in font units (1000 UPM), drawn for
the Regular stroke of 121 units; SemiBold thickens the finished glyphs. The
upstream capitals have flat stroke ends sitting on the baseline (0) and the
cap height (800), so vertical strokes run between the ink lines and
horizontal strokes sit half a stroke inside them.

The lowercase is geometric like the capitals: circular bowls, semicircular
arches, c and e built like C and E (a half circle with straight tails, the
e with E's dot in place of a bar), and diagonals cut level at the baseline
and x-height. The upstream letters carry wide tracking in their right side
bearings, and the lowercase does the same.
"""
import flat
from flat import beyond
from skeleton import Clipped, Disc, Glyph, Stroke, arc, circle, poly

HALF = 60  # half the Regular stroke
X = 540  # x-height (ink)
ASC = 800  # ascender (ink), level with the capitals
DESC = -240  # descender (ink)
XT, XB = X - HALF, HALF  # centre lines of strokes along the x-height and baseline
R = (XT - XB) / 2  # bowl radius
CY = X / 2  # bowl centre
DOT = 62  # dot radius, as in the capitals
DOT_Y = 680  # centre of the i and j dots

TRACK = 290  # tracking added to every right side bearing, as upstream
STEM = 55  # side bearing beside a vertical stem
ROUND = 45  # side bearing beside a bowl
DIAG = 20  # side bearing beside a diagonal


def sb(left, right):
    return (left, right + TRACK)


def tip(x0, x1, top, bottom):
    return flat.tip(x0, x1, top, bottom, HALF)


def vee(x0, x1, top=X, bottom=0):
    return flat.vee(x0, x1, top, bottom, HALF)


def bowl(x=0):
    return circle(x + R, CY, R)


def arch(x, width, depth=0):
    """An n-arch from the stem at x, ending in a right-hand stem down to depth."""
    r = width / 2
    return Stroke(x, XT - r).arc(x + r, XT - r, r, 180, 0).line(x + width, depth)


def open_bowl(tail=90):
    """C and E's shape: a half circle with straight tails to the right."""
    return Stroke(R + tail, XT).line(R, XT).arc(R, CY, R, 90, 270).line(R + tail, XB)


GLYPHS = {
    "a": Glyph([bowl(), Stroke(2 * R, X).line(2 * R, 0)], sb(ROUND, STEM), top=R),
    "b": Glyph([Stroke(0, ASC).line(0, 0), bowl()], sb(STEM, ROUND), top=R),
    "c": Glyph([open_bowl()], sb(ROUND, 20), top=R),
    "d": Glyph([bowl(), Stroke(2 * R, ASC).line(2 * R, 0)], sb(ROUND, STEM), top=R),
    "e": Glyph([open_bowl(), Disc(R + 90 - DOT, CY, DOT)], sb(ROUND, 20), top=R),
    "f": Glyph(
        [Stroke(0, 0).line(0, ASC - HALF - 140).arc(140, ASC - HALF - 140, 140, 180, 90).line(220, ASC - HALF),
         Stroke(-110, XT).line(210, XT)],
        sb(DIAG, 0), top=50),
    "g": Glyph(
        [bowl(), Stroke(2 * R, X).line(2 * R, -30).arc(2 * R - 150, -30, 150, 0, -160)],
        sb(ROUND, STEM), top=R),
    "h": Glyph([Stroke(0, ASC).line(0, 0), arch(0, 400)], sb(STEM, STEM), top=200),
    "i": Glyph([Stroke(0, X).line(0, 0), Disc(0, DOT_Y, DOT)], sb(STEM, STEM)),
    "j": Glyph(
        [Stroke(0, X).line(0, -50).arc(-130, -50, 130, 0, -160), Disc(0, DOT_Y, DOT)],
        sb(-180, STEM), top=0),  # the hook tucks under the previous letter
    "k": Glyph(
        [Stroke(0, ASC).line(0, 0),
         Clipped([Stroke(*beyond((360, X), (0, 180))).line(0, 180),
                  Stroke(140, 300).line(*beyond((380, 0), (140, 300)))], 0, X)],
        sb(STEM, DIAG)),
    "l": Glyph([Stroke(0, ASC).line(0, 180).arc(120, 180, 120, 180, 270)], sb(STEM, 25), top=0),
    "m": Glyph(
        [Stroke(0, X).line(0, 0), arch(0, 320), arch(320, 320)], sb(STEM, STEM), top=320),
    "n": Glyph([Stroke(0, X).line(0, 0), arch(0, 400)], sb(STEM, STEM), top=200),
    "o": Glyph([bowl()], sb(ROUND, ROUND)),
    "p": Glyph([Stroke(0, X).line(0, DESC), bowl()], sb(STEM, ROUND), top=R),
    "q": Glyph([bowl(), Stroke(2 * R, X).line(2 * R, DESC)], sb(ROUND, STEM), top=R),
    "r": Glyph(
        [Stroke(0, X).line(0, 0), arc(200, XT - 200, 200, 180, 90).line(260, XT)],
        sb(STEM, 10), top=130),
    "s": Glyph(
        [Stroke(300, XT).line(170, XT).arc(170, 375, 130, 90, 270, ry=105)
         .arc(170, 165, 130, 90, -90, ry=105).line(30, XB)],
        sb(35, 35)),
    "t": Glyph(
        [Stroke(0, 680).line(0, 180).arc(120, 180, 120, 180, 270),
         Stroke(-110, XT).line(210, XT)],
        sb(DIAG, 20), top=0),
    "u": Glyph(
        [Stroke(0, X).line(0, XB + 200).arc(200, XB + 200, 200, 180, 360).line(400, X),
         Stroke(400, X).line(400, 0)],
        sb(STEM, STEM), top=200),
    "v": Glyph([vee(0, 460)], sb(DIAG, DIAG)),
    "w": Glyph([vee(0, 380), vee(380, 760)], sb(DIAG, DIAG)),
    "x": Glyph(
        [Clipped([Stroke(*beyond((0, 0), (440, X))).line(*beyond((440, X), (0, 0))),
                  Stroke(*beyond((0, X), (440, 0))).line(*beyond((440, 0), (0, X)))], 0, X)],
        sb(DIAG, DIAG)),
    "y": Glyph(
        [Clipped([poly([beyond((0, X), tip(0, 460, X, 0)), tip(0, 460, X, 0)]),
                  Stroke(*beyond((460, X), tip(0, 460, X, 0))).line(
                      *beyond(tip(0, 460, X, 0), (460, X), 340))], DESC, X)],
        sb(DIAG, DIAG), top=230),
    "z": Glyph([poly([(0, XT), (380, XT), (0, XB), (400, XB)])], sb(35, 35)),
    "dotlessi": Glyph([Stroke(0, X).line(0, 0)], sb(STEM, STEM), unicode=0x0131, top=0),

    # Symbols for UK English.
    "sterling": Glyph(
        [arc(260, 590, 150, 0, 180).line(110, XB), Stroke(0, XB).line(470, XB),
         Stroke(0, 380).line(300, 380)],
        sb(40, 40), unicode=0x00A3),
    "Euro": Glyph(
        [Stroke(560, 800 - HALF).line(400, 800 - HALF).arc(400, 400, 340, 90, 270).line(560, XB),
         Stroke(-60, 320).line(380, 320), Stroke(-60, 480).line(380, 480)],
        sb(40, 20), unicode=0x20AC),
    "bullet": Glyph([Disc(0, 400, 95)], sb(ROUND, ROUND), unicode=0x2022),
    "degree": Glyph([circle(0, 680, 100)], sb(ROUND, ROUND), unicode=0x00B0),
}

# Accents are drawn centred on x=0 at their final height.
ACCENTS = flat.accents(X, ASC)
