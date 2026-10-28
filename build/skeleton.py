"""Centre-line ("skeleton") drawing helpers.

The capitals of the upstream fonts are monoline strokes: Foundation Titles
Hand has round ends and joins, Foundation Logo and Foundation One have flat
ends and sharp corners. New glyphs are drawn the same way: as centre lines
that are then expanded to outlines at the stroke width of each weight, so
they match the capitals in both Regular and SemiBold.
"""
import math
from dataclasses import dataclass

import pathops

CAPS = {"round": pathops.LineCap.ROUND_CAP, "flat": pathops.LineCap.BUTT_CAP}
JOINS = {"round": pathops.LineJoin.ROUND_JOIN, "sharp": pathops.LineJoin.MITER_JOIN}


@dataclass
class Glyph:
    """A glyph drawn from skeleton parts. `sb` is the (left, right) side bearing
    measured from the ink, and `top` is the centre-line x used to place
    accents (it defaults to the middle of the ink)."""

    parts: list
    sb: tuple
    unicode: int = None
    top: float = None


def _point(cx, cy, rx, ry, angle):
    a = math.radians(angle)
    return (cx + rx * math.cos(a), cy + ry * math.sin(a))


class Stroke:
    """An open (or closed) centre line made of lines, cubics and arcs."""

    def __init__(self, x, y):
        self.start = (x, y)
        self.current = (x, y)
        self.segments = []
        self.closed = False

    def line(self, x, y):
        self.segments.append(("line", (x, y)))
        self.current = (x, y)
        return self

    def curve(self, c1, c2, p):
        self.segments.append(("curve", (c1, c2, p)))
        self.current = p
        return self

    def arc(self, cx, cy, r, a0, a1, ry=None):
        """Elliptical arc from angle a0 to a1 (degrees; a1 > a0 runs anticlockwise)."""
        rx, ry = r, r if ry is None else ry
        sx, sy = _point(cx, cy, rx, ry, a0)
        if math.hypot(sx - self.current[0], sy - self.current[1]) > 0.5:
            raise ValueError(f"arc starts at {(sx, sy)}, stroke is at {self.current}")
        n = max(1, math.ceil(abs(a1 - a0) / 90))
        step = (a1 - a0) / n
        for i in range(n):
            t0 = math.radians(a0 + i * step)
            t1 = math.radians(a0 + (i + 1) * step)
            k = 4 / 3 * math.tan((t1 - t0) / 4)
            p0 = (cx + rx * math.cos(t0), cy + ry * math.sin(t0))
            p3 = (cx + rx * math.cos(t1), cy + ry * math.sin(t1))
            c1 = (p0[0] - k * rx * math.sin(t0), p0[1] + k * ry * math.cos(t0))
            c2 = (p3[0] + k * rx * math.sin(t1), p3[1] - k * ry * math.cos(t1))
            self.curve(c1, c2, p3)
        return self

    def close(self):
        self.closed = True
        return self

    def path(self, width, cap="round", join="round"):
        p = pathops.Path()
        p.moveTo(*self.start)
        for kind, data in self.segments:
            if kind == "line":
                p.lineTo(*data)
            else:
                p.cubicTo(*data[0], *data[1], *data[2])
        if self.closed:
            p.close()
        p.stroke(width, CAPS[cap], JOINS[join], 4)
        p.convertConicsToQuads()
        return p


class Disc:
    """A filled circle. With no radius it is sized like the font's full stop."""

    def __init__(self, x, y, r=None):
        self.x, self.y, self.r = x, y, r

    def path(self, width, cap="round", join="round"):
        r = self.r if self.r is not None else width / 2 + 18
        s = Stroke(self.x + r, self.y).arc(self.x, self.y, r, 0, 360).close()
        p = pathops.Path()
        p.moveTo(*s.start)
        for _, (c1, c2, pt) in s.segments:
            p.cubicTo(*c1, *c2, *pt)
        p.close()
        return p


def arc(cx, cy, r, a0, a1, ry=None):
    """Start a new stroke with an arc."""
    return Stroke(*_point(cx, cy, r, r if ry is None else ry, a0)).arc(cx, cy, r, a0, a1, ry)


def circle(cx, cy, r, ry=None):
    return arc(cx, cy, r, 0, 360, ry).close()


def poly(points, r=0, closed=False):
    """A stroke through points with each corner rounded to radius r.

    A point given as (x, y, r) has its own radius; 0 keeps the corner sharp.
    The rounding is shrunk where a segment is too short for it.
    """
    pts = [(p[0], p[1]) for p in points]
    radii = [p[2] if len(p) > 2 else r for p in points]
    n = len(pts)
    corners = range(n) if closed else range(1, n - 1)
    start = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2) if closed else pts[0]
    s = Stroke(*start)
    for i in list(corners)[1:] + [0] if closed else corners:
        p, prev, nxt = pts[i], pts[i - 1], pts[(i + 1) % n]
        din, dout = math.dist(prev, p), math.dist(p, nxt)
        u = ((p[0] - prev[0]) / din, (p[1] - prev[1]) / din)
        v = ((nxt[0] - p[0]) / dout, (nxt[1] - p[1]) / dout)
        turn = math.acos(max(-1, min(1, u[0] * v[0] + u[1] * v[1])))
        if not radii[i] or turn < 1e-6:
            s.line(*p)
            continue
        t = min(radii[i] * math.tan(turn / 2), din / 2, dout / 2)
        rr = t / math.tan(turn / 2)
        h = 4 / 3 * math.tan(turn / 4) * rr
        a = (p[0] - u[0] * t, p[1] - u[1] * t)
        b = (p[0] + v[0] * t, p[1] + v[1] * t)
        s.line(*a).curve((a[0] + u[0] * h, a[1] + u[1] * h), (b[0] - v[0] * h, b[1] - v[1] * h), b)
    if closed:
        s.line(*start).close()
    else:
        s.line(*pts[-1])
    return s


class Clipped:
    """Parts cut off below y0 and above y1, for stroke ends that sit level on
    the baseline or x-height instead of square to a diagonal stroke."""

    def __init__(self, parts, y0, y1):
        self.parts, self.y0, self.y1 = parts, y0, y1

    def path(self, width, cap="round", join="round"):
        box = pathops.Path()
        box.moveTo(-5000, self.y0)
        box.lineTo(5000, self.y0)
        box.lineTo(5000, self.y1)
        box.lineTo(-5000, self.y1)
        box.close()
        return pathops.op(outline(self.parts, width, cap, join), box, pathops.PathOp.INTERSECTION)


def outline(parts, width, cap="round", join="round"):
    """Expand skeleton parts to a single overlap-free, clockwise outline."""
    result = pathops.Path()
    for part in parts:
        piece = part.path(width, cap, join)
        piece.simplify()
        result = pathops.op(result, piece, pathops.PathOp.UNION)
    result.simplify(clockwise=True)
    result.convertConicsToQuads()
    return result
