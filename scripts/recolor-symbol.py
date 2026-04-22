#!/usr/bin/env python3
"""Recolor isolated dark clusters (e.g. "?" symbol) to a target color.

Uses connected-component analysis to find SMALL isolated dark clusters
(dark opaque pixels forming a blob), then recolors them. This avoids
accidentally flooding into the main character outline when clusters
happen to touch via anti-aliased pixels.
"""
from __future__ import annotations
import argparse
import pathlib
import sys
from PIL import Image


def find_dark_components(
    img: Image.Image,
    dark_threshold: int = 60,
    alpha_threshold: int = 180,
    region: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
):
    """Return list of connected components of dark-opaque pixels within region.
    Each component is {'size', 'bbox', 'pixels'}."""
    img = img.convert("RGBA")
    w, h = img.size
    x0 = int(w * region[0]); y0 = int(h * region[1])
    x1 = int(w * region[2]); y1 = int(h * region[3])

    pixels = img.load()
    is_dark = [[False] * w for _ in range(h)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = pixels[x, y]
            if a > alpha_threshold and max(r, g, b) < dark_threshold:
                is_dark[y][x] = True

    visited = [[False] * w for _ in range(h)]
    components = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not is_dark[y][x] or visited[y][x]:
                continue
            stack = [(x, y)]
            pts = []
            while stack:
                cx, cy = stack.pop()
                if cx < 0 or cx >= w or cy < 0 or cy >= h:
                    continue
                if visited[cy][cx] or not is_dark[cy][cx]:
                    continue
                visited[cy][cx] = True
                pts.append((cx, cy))
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
            if pts:
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                components.append({
                    "size": len(pts),
                    "bbox": (min(xs), min(ys), max(xs), max(ys)),
                    "pixels": pts,
                })
    return components


def recolor(
    img: Image.Image,
    target_rgb: tuple[int, int, int],
    region: tuple[float, float, float, float],
    min_size: int,
    max_size: int,
    dark_threshold: int = 60,
    alpha_threshold: int = 180,
):
    rgba = img.convert("RGBA")
    comps = find_dark_components(rgba, dark_threshold, alpha_threshold, region)
    comps = [c for c in comps if min_size <= c["size"] <= max_size]
    pixels = rgba.load()
    r2, g2, b2 = target_rgb
    for c in comps:
        for x, y in c["pixels"]:
            _, _, _, a = pixels[x, y]
            pixels[x, y] = (r2, g2, b2, a)
    return rgba, len(comps), comps


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--region", default="0.55,0.00,1.00,0.40",
                   help="x0,y0,x1,y1 fractions (default upper-right)")
    p.add_argument("--color", default="255,255,255", help="target RGB")
    p.add_argument("--min-size", type=int, default=50,
                   help="ignore components smaller than this many pixels")
    p.add_argument("--max-size", type=int, default=4000,
                   help="ignore components bigger than this (filters out character outline)")
    p.add_argument("--backup", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="just list components, don't save")
    p.add_argument("inputs", nargs="+")
    args = p.parse_args()

    region = tuple(float(x) for x in args.region.split(","))
    color = tuple(int(x) for x in args.color.split(","))

    for in_str in args.inputs:
        in_path = pathlib.Path(in_str)
        if not in_path.exists():
            print(f"missing: {in_path}", file=sys.stderr)
            continue
        img = Image.open(in_path)
        if args.dry_run:
            comps = find_dark_components(img.convert("RGBA"), region=region)
            print(f"{in_path.name}: components in region (size order):")
            for c in sorted(comps, key=lambda c: c["size"], reverse=True)[:10]:
                print(f"  size={c['size']:6d}  bbox={c['bbox']}")
            continue

        if args.backup:
            bak = in_path.with_suffix(in_path.suffix + ".bak")
            if not bak.exists():
                bak.write_bytes(in_path.read_bytes())

        result, n, comps = recolor(img, color, region, args.min_size, args.max_size)
        result.save(in_path, "PNG")
        sizes = sorted([c["size"] for c in comps], reverse=True)[:5]
        print(f"  {in_path.name}: recolored {n} components  sizes: {sizes}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
