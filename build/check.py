#!/usr/bin/env python3
"""Check that freshly built fonts match the committed ones.

Usage: check.py BUILT_DIR COMMITTED_DIR

Builds on one platform are byte-identical, but skia-pathops' floating point
differs slightly between CPUs and compilers: points can land one unit apart,
and contours can come out in a different order. So when files differ, this
compares what matters instead:

- the same files, and the same CSS;
- for each TTF: the same glyph order, advance widths, cmap, names and
  OpenType layout tables, and every glyph outline within TOLERANCE of the
  committed one;
- each WOFF and WOFF2 holding the same tables as its TTF (apart from head,
  where WOFF2 sets a flag and checksum).

Exits 1 and lists the differences if the fonts don't match.
"""
import math
import sys
from pathlib import Path

import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

# The area where two outlines differ, divided by the outline's length: the
# average distance between them, in font units. Platform noise measures
# under 0.6; moving one side of an o by 15 units measures 2.4 to 5.
TOLERANCE = 1.0
EXACT_TABLES = ("cmap", "name", "GDEF", "GPOS", "GSUB", "post", "gasp")


def outline(glyph_set, name):
    path = pathops.Path()
    glyph_set[name].draw(path.getPen(glyphSet=glyph_set))
    path.simplify()
    return path


def length(path):
    """Length of an outline, measured along its control polygon."""
    pen = RecordingPen()
    path.draw(pen)
    total, start, current = 0, None, None
    for op, points in pen.value:
        if op == "moveTo":
            start = current = points[0]
        elif op == "closePath":
            if start is not None:
                total += math.dist(current, start)
            start = current = None
        elif points:
            # A contour of only off-curve points has no moveTo.
            chain = [p for p in (current, *points) if p is not None]
            start = chain[0] if start is None else start
            total += sum(math.dist(p, q) for p, q in zip(chain, chain[1:]))
            current = chain[-1]
    return total


def compare_ttf(built, committed):
    problems = []
    a, b = TTFont(built), TTFont(committed)
    if a.getGlyphOrder() != b.getGlyphOrder():
        return ["glyph order differs"]
    for tag in EXACT_TABLES:
        if (tag in a) != (tag in b) or (tag in a and a.reader[tag] != b.reader[tag]):
            problems.append(f"{tag} table differs")
    ga, gb = a.getGlyphSet(), b.getGlyphSet()
    for name in a.getGlyphOrder():
        if a["hmtx"][name][0] != b["hmtx"][name][0]:
            problems.append(f"{name}: advance {a['hmtx'][name][0]} != {b['hmtx'][name][0]}")
            continue
        pa, pb = outline(ga, name), outline(gb, name)
        union = pathops.op(pa, pb, pathops.PathOp.UNION)
        if not union.area:
            continue
        distance = pathops.op(pa, pb, pathops.PathOp.XOR).area / length(union)
        if distance > TOLERANCE:
            problems.append(f"{name}: outline differs by {distance:.1f} units on average")
    return problems


def compare_webfont(webfont, ttf):
    a, b = TTFont(webfont), TTFont(ttf)
    differ = [t for t in sorted(b.reader.keys())
              if t != "head" and (t not in a.reader or a.reader[t] != b.reader[t])]
    return [f"tables differ from {ttf.name}: {', '.join(differ)}"] if differ else []


def main(built_dir, committed_dir):
    built_dir, committed_dir = Path(built_dir), Path(committed_dir)
    files = lambda d: {p.relative_to(d) for p in d.rglob("*") if p.is_file() and p.name != ".DS_Store"}
    built, committed = files(built_dir), files(committed_dir)
    report = [f"{p}: only in the build" for p in sorted(built - committed)]
    report += [f"{p}: not produced by the build" for p in sorted(committed - built)]
    loose = 0
    for rel in sorted(built & committed):
        a, b = built_dir / rel, committed_dir / rel
        if a.read_bytes() == b.read_bytes():
            continue
        if rel.suffix == ".ttf":
            problems = compare_ttf(a, b)
        elif rel.suffix in (".woff", ".woff2"):
            ttf = committed_dir / rel.parent.parent / "ttf" / (rel.stem + ".ttf")
            problems = compare_webfont(b, ttf)
        else:
            problems = ["contents differ"]
        report += [f"{rel}: {p}" for p in problems]
        loose += not problems
    if report:
        print("Built fonts differ from the committed ones:\n  " + "\n  ".join(report))
        print("Run make fonts and commit fonts/.")
        return 1
    if loose:
        print(f"Fonts match ({loose} files differ only by floating-point noise between platforms).")
    else:
        print("Fonts match byte for byte.")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
