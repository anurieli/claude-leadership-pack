#!/usr/bin/env python3
"""QA snapshot checker for site-to-video projects.

Reads PNG snapshots from a directory and flags scenes that look empty or
under-populated. Empty-frame check: pixels with low chroma + low luminance
spread (i.e. flat solid background) — scenes below 40% non-flat coverage
are flagged.

Usage: qa-snapshots.py [snapshot-dir]   (defaults to ./snapshots)
Exits 1 if any scene is flagged.
"""
import sys, glob
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(2)


def coverage(img: Image.Image) -> float:
    """Fraction of pixels that aren't part of a flat background.

    A pixel counts as non-flat if its R/G/B spread > 5 (has chroma) OR
    its sum > 30 (isn't near-black). 100x100 downsample for speed.
    """
    small = img.resize((100, 100))
    px = list(small.getdata())
    nonflat = sum(
        1 for p in px if (max(p[:3]) - min(p[:3]) > 5) or sum(p[:3]) > 30
    )
    return nonflat / len(px)


def main(snap_dir: str) -> int:
    paths = sorted(glob.glob(f"{snap_dir}/*.png"))
    if not paths:
        print(f"No PNGs found in {snap_dir}/", file=sys.stderr)
        return 2

    fail = False
    print(f"{'status':<6} {'cov':>7}  file")
    print("-" * 60)
    for p in paths:
        img = Image.open(p).convert("RGB")
        cov = coverage(img)
        if cov < 0.40:
            status = "FAIL"
            fail = True
        elif cov < 0.55:
            status = "WARN"
        else:
            status = "ok"
        print(f"{status:<6} {cov*100:6.1f}%  {Path(p).name}")

    if fail:
        print("\nAt least one scene looks empty. Re-snapshot at the beat midpoint, "
              "or add density (background texture, midground content, foreground accents).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "snapshots"))
