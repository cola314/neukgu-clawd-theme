#!/usr/bin/env python3
"""Find eye positions in a PNG by detecting dark dot clusters."""
from __future__ import annotations
import sys
import pathlib
from PIL import Image


def main(path: str) -> None:
    img = Image.open(path)
    print(f"size: {img.size}, mode: {img.mode}")

    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()

    # Build binary mask of black dots (RGB all < 60, alpha > 200)
    black = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r < 60 and g < 60 and b < 60 and a > 200:
                black[y][x] = True

    # Flood-fill to find connected components of black pixels
    # Use iterative BFS
    visited = [[False] * w for _ in range(h)]
    components = []
    for y in range(h):
        for x in range(w):
            if not black[y][x] or visited[y][x]:
                continue
            stack = [(x, y)]
            pts = []
            while stack:
                cx, cy = stack.pop()
                if cx < 0 or cx >= w or cy < 0 or cy >= h:
                    continue
                if visited[cy][cx] or not black[cy][cx]:
                    continue
                visited[cy][cx] = True
                pts.append((cx, cy))
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
            if len(pts) > 1:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                components.append({
                    "size": len(pts),
                    "bbox": (min(xs), min(ys), max(xs), max(ys)),
                    "center": (sum(xs) / len(xs), sum(ys) / len(ys)),
                })

    components.sort(key=lambda c: c["size"], reverse=True)
    # Eyes: small isolated clusters in head region (top-center area, NOT huge outline)
    # Outline cluster will be by far the largest. Eyes are small (< 0.5% of image area)
    area = w * h
    eye_candidates = [c for c in components if 50 < c["size"] < area * 0.003]
    print(f"\nTop 10 black-pixel clusters (size order):")
    for c in components[:10]:
        pct = c["size"] / area * 100
        print(f"  size={c['size']:6d} ({pct:.2f}%)  bbox={c['bbox']}  center=({c['center'][0]:.0f}, {c['center'][1]:.0f})")

    print(f"\nEye candidates (50 < size < 0.3%): {len(eye_candidates)}")
    for c in eye_candidates[:8]:
        print(f"  size={c['size']}  center=({c['center'][0]:.0f}, {c['center'][1]:.0f})  bbox={c['bbox']}")


if __name__ == "__main__":
    main(sys.argv[1])
