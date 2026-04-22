#!/usr/bin/env python3
"""
Assemble PNG frames into an APNG loop. Local only, no API cost.

Usage:
  python assemble-apng.py \\
      --out ../../themes/neukgu/assets/typing.apng \\
      --duration 180 \\
      ../../themes/neukgu/assets/typing-f1.png \\
      ../../themes/neukgu/assets/typing-f2.png \\
      ../../themes/neukgu/assets/typing-f3.png
"""
from __future__ import annotations
import argparse
import pathlib
import sys
from PIL import Image


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, help="Output APNG path")
    p.add_argument("--duration", type=int, default=180, help="Frame duration in ms")
    p.add_argument("frames", nargs="+", help="Input PNG frames (in order)")
    args = p.parse_args()

    paths = [pathlib.Path(f) for f in args.frames]
    for fp in paths:
        if not fp.exists():
            print(f"missing: {fp}", file=sys.stderr)
            return 1

    imgs = [Image.open(fp).convert("RGBA") for fp in paths]

    # Normalize to same size (use first frame as canonical)
    w, h = imgs[0].size
    imgs = [im if im.size == (w, h) else im.resize((w, h), Image.LANCZOS) for im in imgs]

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    imgs[0].save(
        out_path,
        format="PNG",
        save_all=True,
        append_images=imgs[1:],
        duration=args.duration,
        loop=0,
        disposal=2,
    )

    size_kb = out_path.stat().st_size / 1024
    print(f"Saved: {out_path} ({size_kb:.1f} KB, {len(imgs)} frames x {args.duration}ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
