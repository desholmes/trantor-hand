#!/usr/bin/env python3
"""Build the Trantor fonts.

Usage: build.py [family ...]   (hand, caption; all families when none are given)

Writes fonts/<family>/ttf/*.ttf and fonts/<family>/webfonts/ (WOFF2, WOFF
and a CSS @font-face stylesheet) for each family.
"""
import os
import sys

from common import RELEASE_EPOCH
from caption.family import Caption
from hand.family import Hand

FAMILIES = {cls.KEY: cls for cls in (Hand, Caption)}


def main(names):
    unknown = [n for n in names if n not in FAMILIES]
    if unknown:
        sys.exit(f"Unknown family: {', '.join(unknown)} (choose from {', '.join(FAMILIES)})")
    os.environ.setdefault("SOURCE_DATE_EPOCH", RELEASE_EPOCH)
    for name in names or FAMILIES:
        FAMILIES[name].build_family()


if __name__ == "__main__":
    main(sys.argv[1:])
