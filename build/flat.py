"""Drawing helpers shared by the flat-ended designs (Caption and Mark).

Foundation One and Foundation Logo cut their stroke ends flat, and the ends
of diagonals level with the baseline and x-height, so their V shapes come to
a sharp point that just touches the line.
"""
import math

from skeleton import Clipped, Disc, Stroke, poly


def beyond(p, q, d=150):
    """The point d past p on the line from q through p."""
    length = math.dist(p, q)
    return (p[0] + (p[0] - q[0]) * d / length, p[1] + (p[1] - q[1]) * d / length)


def tip(x0, x1, top, bottom, half):
    """The centre-line vertex of a V from x0 to x1, drawn with a stroke of
    2 * half, whose sharp point just touches `bottom` (or `top`, if
    top < bottom, for an upward point)."""
    half_angle = math.atan2(abs(x1 - x0) / 2, abs(top - bottom))
    offset = half / math.sin(half_angle)
    return ((x0 + x1) / 2, bottom + (offset if top > bottom else -offset))


def vee(x0, x1, top, bottom, half):
    v = tip(x0, x1, top, bottom, half)
    return Clipped([poly([beyond((x0, top), v), v, beyond((x1, top), v)])], bottom, top)


def accent_parts(kind, base):
    """Accent centred on x=0, sitting `base` units up (the gap above the letter)."""
    if kind == "acute":
        return [Clipped([Stroke(-80, base - 30).line(80, base + 200)], base, base + 150)]
    if kind == "grave":
        return [Clipped([Stroke(80, base - 30).line(-80, base + 200)], base, base + 150)]
    if kind == "circumflex":
        return [Clipped([poly([(-150, base - 30), (0, base + 120), (150, base - 30)])], base, base + 170)]
    if kind == "dieresis":
        return [Disc(-105, base + 65, 60), Disc(105, base + 65, 60)]
    if kind == "tilde":
        return [Stroke(-140, base + 20).curve((-70, base + 140), (70, base - 30), (140, base + 90))]
    raise ValueError(kind)


def accents(x_height, cap_height):
    """The accents for the composites: ".lc" above the x-height and ".case"
    above the capitals, plus the cedilla."""
    marks = {}
    for kind in ("grave", "acute", "circumflex", "dieresis", "tilde"):
        marks[kind + ".lc"] = accent_parts(kind, x_height + 75)
        marks[kind + ".case"] = accent_parts(kind, cap_height + 65)
    marks["cedilla"] = [poly([(0, 20), (0, -120), (-120, -120)], 60)]
    return marks
