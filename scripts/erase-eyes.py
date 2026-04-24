#!/usr/bin/env python3
"""Erase the eye regions in idle.png by filling them with sampled fur color.

Used so that the SVG <g id="eyes-js"> overlay can move freely without
revealing the PNG's original fixed eyes underneath.
"""
from __future__ import annotations
import sys
import pathlib
from PIL import Image


# Eye pixel coords in idle.png (1254x1254), found via find-eyes.py
LEFT_EYE_CENTER = (766, 385)
RIGHT_EYE_CENTER = (897, 385)
# Measured eye bbox: 30x41 (half = 15x20.5).
# Ellipse math: corners of the eye bbox must satisfy (dx/rx)^2 + (dy/ry)^2 <= 1
# so rx/ry need enough margin to cover the corners, not just the half-width/height.
FILL_RX = 24
FILL_RY = 30

# Sample points for fur color — ALL inside the LIGHT cream mask around the
# cheeks (NOT the darker head tan between eyes, NOT the black nose/mouth below).
# Eyes are at y=385 on 1254 canvas; cream mask expected ~(231, 203, 166).
SAMPLES = [(700, 430), (750, 420), (910, 420), (960, 430)]


def sample_fur(img: Image.Image) -> tuple[int, int, int]:
    rgb = img.convert("RGB")
    pix = rgb.load()
    rs, gs, bs = [], [], []
    for x, y in SAMPLES:
        r, g, b = pix[x, y]
        # skip if too dark (accidental outline)
        if r + g + b < 300:
            continue
        rs.append(r); gs.append(g); bs.append(b)
    if not rs:
        return (210, 180, 130)
    return (sum(rs) // len(rs), sum(gs) // len(gs), sum(bs) // len(bs))


def main(src: str, dst: str) -> None:
    img = Image.open(src).convert("RGBA")
    fur = sample_fur(img)
    print(f"Sampled fur color: {fur}")

    # Paste a solid-fur-color rectangle directly onto the image — avoids any
    # ImageDraw.rectangle outline quirks and avoids GaussianBlur edge artifacts
    # that produce semi-transparent rings revealing the black eye underneath.
    result = img.copy()
    patch_w = FILL_RX * 2 + 1
    patch_h = FILL_RY * 2 + 1
    patch = Image.new("RGBA", (patch_w, patch_h), fur + (255,))
    for cx, cy in (LEFT_EYE_CENTER, RIGHT_EYE_CENTER):
        result.paste(patch, (cx - FILL_RX, cy - FILL_RY))
    result.save(dst, "PNG")
    print(f"Saved: {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
