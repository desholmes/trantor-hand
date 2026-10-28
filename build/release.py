#!/usr/bin/env python3
"""Package the built fonts for a GitHub release.

Usage: release.py [tag]

Writes to dist/:
  TrantorType.zip                 every family, the series stylesheet and licences
  TrantorHand.zip, ...            one family: ttf/, webfonts/, OFL.txt, FONTLOG.txt
  SHA256SUMS
  NOTES.md                        release notes: each family's latest FONTLOG entry

The file names carry no version, so the site can link to
releases/latest/download/<name>. The zips are byte-identical between runs:
entries are sorted and dated at the release epoch. With a tag, it must match
the series version (v1.0.0 for RELEASE 1.0.0).
"""
import hashlib
import shutil
import sys
import time
import zipfile

from build import FAMILIES
from common import RELEASE, RELEASE_EPOCH, ROOT, VERSION

DIST = ROOT / "dist"
SITE = "https://desholmes.github.io/trantor-type/"
DATE = time.gmtime(int(RELEASE_EPOCH))[:6]


def readme(title, body):
    return f"""{title} {RELEASE} (font version {VERSION})

{body}

Specimens and usage: {SITE}
Source: https://github.com/desholmes/trantor-type

Licensed under the SIL Open Font License 1.1 (OFL.txt): free to use, embed
and modify, but not to sell on its own. Keep OFL.txt with the fonts when you
redistribute them.

Foundation is an Apple TV+ series based on the Isaac Asimov books. These
fan-made fonts are not affiliated with or endorsed by Apple, Skydance or the
Asimov estate.
"""


def family_files(cls, prefix):
    """(path in zip, file on disk) for one family."""
    fonts = ROOT / "fonts" / cls.KEY
    files = [(f"{prefix}{path.parent.name}/{path.name}", path)
             for folder in ("ttf", "webfonts") for path in sorted((fonts / folder).iterdir())
             if not path.name.startswith(".")]
    for name in ("OFL.txt", "FONTLOG.txt"):
        files.append((prefix + name, ROOT / "families" / cls.KEY / name))
    return files


def latest_change(cls):
    """The newest ChangeLog entry in a family's FONTLOG."""
    log = (ROOT / "families" / cls.KEY / "FONTLOG.txt").read_text()
    entries = log.split("\nChangeLog\n", 1)[1].strip().split("\n\n")
    return entries[0]


def notes():
    parts = [f"Trantor {RELEASE} (font version {VERSION}). Specimens and usage: {SITE}\n"]
    for cls in FAMILIES.values():
        heading, *changes = latest_change(cls).splitlines()
        parts.append(f"### {heading}\n\n" + "\n".join(changes) + "\n")
    parts.append("Download `TrantorType.zip` for every family, or one family's zip. "
                 "Check downloads against `SHA256SUMS`.\n")
    return "\n".join(parts)


def write_zip(path, entries):
    """entries: (name in zip, bytes)."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)


def main(args):
    if args and args[0] != f"v{RELEASE}":
        sys.exit(f"Tag {args[0]} does not match the series version {RELEASE} (expected v{RELEASE})")
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()

    series = []
    for cls in FAMILIES.values():
        name = cls.FAMILY.replace(" ", "")
        files = [(n, p.read_bytes()) for n, p in family_files(cls, f"{name}/")]
        files.append((f"{name}/README.txt", readme(cls.FAMILY, (
            f"ttf/       desktop fonts (Regular and SemiBold)\n"
            f"webfonts/  WOFF2 and WOFF, with {cls.CSS_FILE} (@font-face rules)\n"
            f"FONTLOG.txt  what changed from the original font")).encode()))
        write_zip(DIST / f"{name}.zip", files)
        series += [(f"TrantorType/{cls.KEY}/{n.split('/', 1)[1]}", data) for n, data in files
                   if not n.endswith("README.txt")]

    series.append(("TrantorType/trantor.css", (ROOT / "fonts" / "trantor.css").read_bytes()))
    series.append(("TrantorType/OFL.txt", (ROOT / "OFL.txt").read_bytes()))
    series.append(("TrantorType/README.txt", readme("The Trantor font series", (
        "hand/, caption/, mark/  each family: ttf/, webfonts/, OFL.txt, FONTLOG.txt\n"
        "trantor.css             @font-face rules for every family and weight")).encode()))
    write_zip(DIST / "TrantorType.zip", series)

    sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(DIST.glob("*.zip"))]
    (DIST / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    (DIST / "NOTES.md").write_text(notes())
    for p in sorted(DIST.iterdir()):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
