#!/usr/bin/env python3
"""Erase the eye regions in idle.png by filling them with sampled fur color.

Used so that the SVG <g id="eyes-js"> overlay can move freely without
revealing the PNG's original fixed eyes underneath.
"""
from __future__ import annotations
import sys
import pathlib
from PIL import Image, ImageDraw, ImageFilter


# Eye pixel coords in idle.png (1254x1254), found via find-eyes.py
LEFT_EYE_CENTER = (766, 385)
RIGHT_EYE_CENTER = (897, 385)
# Fill radius slightly larger than detected eye (~15x20)
FILL_RX = 22
FILL_RY = 28

# Sample points for fur color (tan regions near but not touching eyes)
SAMPLES = [(720, 400), (820, 360), (940, 400), (860, 350)]


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

    # Create an "eraser" layer: filled ellipses in fur color at eye positions
    eraser = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(eraser)
    for cx, cy in (LEFT_EYE_CENTER, RIGHT_EYE_CENTER):
        draw.ellipse(
            (cx - FILL_RX, cy - FILL_RY, cx + FILL_RX, cy + FILL_RY),
            fill=fur + (255,),
        )

    # Slight blur on the eraser so the painted patch blends with surrounding fur
    eraser = eraser.filter(ImageFilter.GaussianBlur(radius=2))

    # Composite eraser OVER the original image
    result = Image.alpha_composite(img, eraser)
    result.save(dst, "PNG")
    print(f"Saved: {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
