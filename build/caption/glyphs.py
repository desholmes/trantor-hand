"""Skeleton designs for the new Trantor Caption glyphs.

All coordinates are stroke centre lines in font units (1000 UPM), drawn for
the Regular stroke of 116 units; SemiBold thickens the finished glyphs. The
upstream capitals have flat stroke ends sitting on the baseline (0) and the
cap height (768), so vertical strokes run between the ink lines and
horizontal strokes sit half a stroke inside them.

The lowercase borrows the capitals' construction: rounded-rectangle bowls,
square-shouldered arches, diagonals cut level at the baseline and x-height,
and a round dot standing in for the bar of f, as it does in F. An e with a
dot in place of its bar, like E, is in stylistic set 1; it is less legible
in running text.
"""
import math

import flat
from flat import accent_parts, beyond
from skeleton import Clipped, Disc, Glyph, Stroke, poly

HALF = 58  # half the Regular stroke
X = 520  # x-height (ink)
ASC = 768  # ascender (ink), level with the capitals
DESC = -230  # descender (ink)
XT, XB = X - HALF, HALF  # centre lines of strokes along the x-height and baseline
AT, DB = ASC - HALF, DESC + HALF  # ... along the ascender and descender
MID = (XT + XB) / 2
W = 360  # bowl width between stem centre lines
R = 140  # corner radius of bowls and arches
DOT = 70  # dot radius, as in the capitals
DOT_Y = 655  # centre of the i and j dots

STEM = 80  # side bearing beside a vertical stem
ROUND = 65  # side bearing beside a bowl
DIAG = 30  # side bearing beside a diagonal


def bowl(x0=0, x1=W):
    return poly([(x0, XB), (x1, XB), (x1, XT), (x0, XT)], R, closed=True)


def tip(x0, x1, top, bottom):
    return flat.tip(x0, x1, top, bottom, HALF)


def vee(x0, x1, top=X, bottom=0):
    return flat.vee(x0, x1, top, bottom, HALF)


GLYPHS = {
    "a": Glyph(
        [poly([(40, XT), (W, XT), (W, 0)], R),
         poly([(W, 300), (0, 300), (0, XB), (W, XB)], 110)],
        (ROUND, STEM), top=W / 2),
    "b": Glyph([Stroke(0, ASC).line(0, 0), bowl()], (STEM, ROUND), top=W / 2),
    "c": Glyph([poly([(W, XT), (0, XT), (0, XB), (W, XB)], R)], (ROUND, 30), top=W / 2),
    "d": Glyph([bowl(), Stroke(W, ASC).line(W, 0)], (ROUND, STEM), top=W / 2),
    "e": Glyph(
        [poly([(0, MID), (W, MID), (W, XT), (0, XT), (0, XB), (W, XB)], R)],
        (ROUND, 30), top=W / 2),
    "f": Glyph(
        [poly([(0, 0), (0, AT), (210, AT)], R), Disc(HALF + 45 + DOT, XT, DOT)],
        (STEM, 10), top=HALF),
    "g": Glyph(
        [bowl(), poly([(W, X), (W, DB), (40, DB)], R)],
        (ROUND, STEM), top=W / 2),
    "h": Glyph(
        [Stroke(0, ASC).line(0, 0), poly([(0, XT), (W, XT), (W, 0)], R)],
        (STEM, STEM), top=W / 2),
    "i": Glyph([Stroke(0, X).line(0, 0), Disc(0, DOT_Y, DOT)], (STEM, STEM)),
    "j": Glyph(
        [poly([(0, X), (0, DB), (-150, DB)], R), Disc(0, DOT_Y, DOT)],
        (-90, STEM), top=0),  # the hook tucks under the previous letter
    "k": Glyph(
        [Stroke(0, ASC).line(0, 0),
         Clipped([Stroke(*beyond((W, X), (0, 170))).line(0, 170),
                  Stroke(150, 280).line(*beyond((W + 20, 0), (150, 280)))], 0, X)],
        (STEM, DIAG)),
    "l": Glyph([poly([(0, ASC), (0, XB), (130, XB)], R)], (STEM, 20), top=0),
    "m": Glyph(
        [poly([(0, 0), (0, XT), (580, XT), (580, 0)], R), Stroke(290, XT).line(290, 0)],
        (STEM, STEM), top=290),
    "n": Glyph([poly([(0, 0), (0, XT), (W, XT), (W, 0)], R)], (STEM, STEM), top=W / 2),
    "o": Glyph([bowl()], (ROUND, ROUND)),
    "p": Glyph([Stroke(0, X).line(0, DESC), bowl()], (STEM, ROUND), top=W / 2),
    "q": Glyph([bowl(), Stroke(W, X).line(W, DESC)], (ROUND, STEM), top=W / 2),
    "r": Glyph([poly([(0, 0), (0, XT), (250, XT)], R)], (STEM, 15), top=120),
    "s": Glyph(
        [poly([(W, XT), (0, XT), (0, MID), (W, MID), (W, XB), (0, XB)], 100)],
        (45, 45)),
    "t": Glyph(
        [poly([(0, 660), (0, XB), (150, XB)], R), Stroke(-110, XT).line(210, XT)],
        (DIAG, 20), top=0),
    "u": Glyph(
        [poly([(0, X), (0, XB), (W, XB)], R), Stroke(W, X).line(W, 0)],
        (STEM, STEM), top=W / 2),
    "v": Glyph([vee(0, 440)], (DIAG, DIAG)),
    "w": Glyph([vee(0, 380), vee(380, 760)], (DIAG, DIAG)),
    "x": Glyph(
        [Clipped([Stroke(*beyond((0, 0), (420, X))).line(*beyond((420, X), (0, 0))),
                  Stroke(*beyond((0, X), (420, 0))).line(*beyond((420, 0), (0, X)))], 0, X)],
        (DIAG, DIAG)),
    "y": Glyph(
        [Clipped([poly([beyond((0, X), tip(0, 440, X, 0)), tip(0, 440, X, 0)]),
                  Stroke(*beyond((440, X), tip(0, 440, X, 0))).line(
                      *beyond(tip(0, 440, X, 0), (440, X), 330))], DESC, X)],
        (DIAG, DIAG), top=220),
    "z": Glyph([poly([(0, XT), (W, XT), (0, XB), (W + 20, XB)])], (45, 45)),
    "dotlessi": Glyph([Stroke(0, X).line(0, 0)], (STEM, STEM), unicode=0x0131, top=0),

    # Stylistic set 1: an e with a dot in place of its bar, like E.
    "e.ss01": Glyph(
        [poly([(W, XT), (0, XT), (0, XB), (W, XB)], R), Disc(W + HALF - DOT, MID, DOT)],
        (ROUND, 30), top=W / 2),

    # Basic Latin symbols missing upstream.
    "dollar": Glyph(
        [poly([(420, 640), (0, 640), (0, 384), (420, 384), (420, 128), (0, 128)], 120),
         Stroke(210, 640).line(210, 800), Stroke(210, 128).line(210, -32)],
        (55, 55), unicode=0x0024),
    "percent": Glyph(
        [Disc(0, 620, DOT), Disc(460, 150, DOT),
         Clipped([Stroke(*beyond((40, 0), (420, 768))).line(*beyond((420, 768), (40, 0)))], 0, 768)],
        (55, 55), unicode=0x0025),
    "asterisk": Glyph(
        [Stroke(200 + 200 * math.cos(math.radians(a)), 540 + 200 * math.sin(math.radians(a)))
         .line(200 - 200 * math.cos(math.radians(a)), 540 - 200 * math.sin(math.radians(a)))
         for a in (90, 30, -30)],
        (40, 40), unicode=0x002A),
    "asciicircum": Glyph(
        [Clipped([poly([(0, 420), tip(0, 360, 420, 768), (360, 420)])], 450, 768)],
        (40, 40), unicode=0x005E),
    "underscore": Glyph([Stroke(0, -120).line(520, -120)], (20, 20), unicode=0x005F),
    "grave": Glyph(accent_parts("grave", 620), (60, 60), unicode=0x0060),
    "asciitilde": Glyph(
        [Stroke(0, 330).curve((110, 470), (290, 250), (400, 400))], (50, 50), unicode=0x007E),

    # Symbols for UK English.
    "sterling": Glyph(
        [poly([(420, AT), (120, AT), (120, XB)], R), Stroke(0, XB).line(470, XB),
         Stroke(0, 384).line(280, 384)],
        (50, 40), unicode=0x00A3),
    "Euro": Glyph(
        [poly([(560, AT), (0, AT), (0, XB), (560, XB)], 220),
         Stroke(-110, 300).line(340, 300), Stroke(-110, 468).line(340, 468)],
        (40, 30), unicode=0x20AC),
    "bullet": Glyph([Disc(0, 384, 95)], (ROUND, ROUND), unicode=0x2022),
    "degree": Glyph(
        [poly([(0, 470), (240, 470), (240, AT), (0, AT)], 90, closed=True)],
        (ROUND, ROUND), unicode=0x00B0),
}

# Accents are drawn centred on x=0 at their final height.
ACCENTS = flat.accents(X, ASC)
