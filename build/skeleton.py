"""Centre-line ("skeleton") drawing helpers.

The capitals in Foundation Titles Hand are monoline strokes with round caps
and joins. New glyphs are drawn the same way: as centre lines that are then
expanded to outlines at the stroke width of each weight, so they match the
capitals in both Regular and SemiBold.
"""
import math

import pathops


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

    def path(self, width):
        p = pathops.Path()
        p.moveTo(*self.start)
        for kind, data in self.segments:
            if kind == "line":
                p.lineTo(*data)
            else:
                p.cubicTo(*data[0], *data[1], *data[2])
        if self.closed:
            p.close()
        p.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        p.convertConicsToQuads()
        return p


class Disc:
    """A filled circle. With no radius it is sized like the font's full stop."""

    def __init__(self, x, y, r=None):
        self.x, self.y, self.r = x, y, r

    def path(self, width):
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


def outline(parts, width):
    """Expand skeleton parts to a single overlap-free, clockwise outline."""
    result = pathops.Path()
    for part in parts:
        piece = part.path(width)
        piece.simplify()
        result = pathops.op(result, piece, pathops.PathOp.UNION)
    result.simplify(clockwise=True)
    result.convertConicsToQuads()
    return result
