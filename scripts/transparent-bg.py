#!/usr/bin/env python3
"""
Convert white background to transparent alpha. Local only.

Modes:
  simple: classic threshold — any pixel with min(R,G,B)>=hi becomes transparent.
          Fast but removes "trapped" whites (e.g., sparkle interiors).
  border: flood-fill from image borders — only white pixels reachable from
          any border become transparent. Trapped whites (inside sparkles,
          eyes, loops) stay opaque. This is the default.

Gradient smoothing:
  min(R,G,B) >= hi  -> fully transparent (only in bg region for border mode)
  min(R,G,B) <= lo  -> fully opaque
  in between        -> linear alpha ramp for smooth anti-aliased edges

Usage:
  python transparent-bg.py [--mode border|simple] [--hi 240] [--lo 200] \\
      --backup file1.png file2.png ...
"""
from __future__ import annotations
import argparse
import pathlib
import sys
from PIL import Image, ImageChops, ImageDraw


def _gradient_lut(hi: int, lo: int) -> list[int]:
    lut = []
    for p in range(256):
        if p >= hi:
            lut.append(0)
        elif p <= lo:
            lut.append(255)
        else:
            lut.append(int(255 * (hi - p) / (hi - lo)))
    return lut


def white_to_alpha_simple(img: Image.Image, hi: int, lo: int) -> Image.Image:
    img = img.convert("RGBA")
    r, g, b, _ = img.split()
    rgb_min = ImageChops.darker(ImageChops.darker(r, g), b)
    new_alpha = rgb_min.point(_gradient_lut(hi, lo))
    return Image.merge("RGBA", (r, g, b, new_alpha))


def white_to_alpha_border(
    img: Image.Image,
    hi: int,
    lo: int,
    trapped_color: tuple[int, int, int] | None = None,
) -> Image.Image:
    """Only border-connected white gets alpha=0. Trapped whites preserved.
    If trapped_color is given, recolor trapped-white pixels to that RGB.

    If input image already has transparency (alpha channel with zeros),
    return as-is to avoid corrupting Nano Banana outputs that were
    delivered already-transparent.
    """
    img = img.convert("RGBA")
    r, g, b, orig_alpha = img.split()
    # Passthrough: input already has transparency (any alpha < 250 detected)
    alpha_min, _ = orig_alpha.getextrema()
    if alpha_min < 250:
        return img

    # Detect background color from corners to choose bg mode
    rgb_min_full = ImageChops.darker(ImageChops.darker(r, g), b)
    rgb_max_full = ImageChops.lighter(ImageChops.lighter(r, g), b)
    w, h = img.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corner_max_vals = [rgb_max_full.getpixel(c) for c in corners]

    if max(corner_max_vals) < 30:
        # Dark/black opaque bg — flood-fill from border using rgb_max <= low threshold
        candidate = rgb_max_full.point(lambda p: 255 if p < 30 else 0)
        is_bg = candidate.copy()
        seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                 (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
        for pt in seeds:
            try:
                if is_bg.getpixel(pt) == 255:
                    ImageDraw.floodfill(is_bg, pt, 128, thresh=0)
            except Exception:
                pass
        final_alpha = is_bg.point(lambda p: 0 if p == 128 else 255)
        if trapped_color is not None:
            # Treat "trapped dark" (rgb_max small but not border-connected) as target color
            trapped_mask = is_bg.point(lambda p: 255 if p == 255 else 0)
            color_fill = Image.new("RGB", img.size, trapped_color)
            rgb_img = Image.merge("RGB", (r, g, b))
            tinted = Image.composite(color_fill, rgb_img, trapped_mask)
            r, g, b = tinted.split()
        return Image.merge("RGBA", (r, g, b, final_alpha))

    rgb_min = rgb_min_full

    # Binary candidate: 255 if "near-white" (>= lo), else 0
    candidate = rgb_min.point(lambda p: 255 if p >= lo else 0)

    # Flood-fill from multiple border seed points, marking border-connected
    # whites with value 128 (distinct from 0 content and 255 trapped white)
    w, h = candidate.size
    is_bg = candidate.copy()
    seeds = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
        (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2),
        (w // 4, 0), (3 * w // 4, 0), (w // 4, h - 1), (3 * w // 4, h - 1),
    ]
    for pt in seeds:
        try:
            if is_bg.getpixel(pt) == 255:
                ImageDraw.floodfill(is_bg, pt, 128, thresh=0)
        except Exception:
            pass

    # Gradient alpha (what the alpha would be with simple mode)
    gradient_alpha = rgb_min.point(_gradient_lut(hi, lo))

    # "not border-bg" mask: 255 where pixel is content or trapped-white, 0 where bg
    not_bg_mask = is_bg.point(lambda p: 0 if p == 128 else 255)

    # Final alpha: where bg -> use gradient (transparent); else -> 255 (opaque)
    final_alpha = ImageChops.lighter(gradient_alpha, not_bg_mask)

    # Optionally recolor trapped-white pixels (where is_bg == 255)
    if trapped_color is not None:
        trapped_mask = is_bg.point(lambda p: 255 if p == 255 else 0)
        color_fill = Image.new("RGB", img.size, trapped_color)
        rgb_img = Image.merge("RGB", (r, g, b))
        tinted = Image.composite(color_fill, rgb_img, trapped_mask)
        r, g, b = tinted.split()

    return Image.merge("RGBA", (r, g, b, final_alpha))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["border", "simple"], default="border",
                   help="border: flood-fill from edges (preserves trapped whites). simple: threshold only.")
    p.add_argument("--hi", type=int, default=240, help="Above this min(RGB): fully transparent bg")
    p.add_argument("--lo", type=int, default=200, help="Below this min(RGB): fully opaque")
    p.add_argument("--suffix", default="", help="Output suffix (default: overwrite)")
    p.add_argument("--backup", action="store_true", help="Save original as .bak before overwrite")
    p.add_argument("--trapped-color", default=None,
                   help="Recolor border-trapped whites to R,G,B (e.g. '255,220,80' for golden yellow). border mode only.")
    p.add_argument("inputs", nargs="+")
    args = p.parse_args()

    trapped_color = None
    if args.trapped_color:
        trapped_color = tuple(int(x) for x in args.trapped_color.split(","))
        if len(trapped_color) != 3:
            print("--trapped-color must be R,G,B", file=sys.stderr)
            return 1

    for in_str in args.inputs:
        in_path = pathlib.Path(in_str)
        if not in_path.exists():
            print(f"missing: {in_path}", file=sys.stderr)
            continue

        img = Image.open(in_path)
        if args.mode == "border":
            transparent = white_to_alpha_border(img, args.hi, args.lo, trapped_color)
        else:
            transparent = white_to_alpha_simple(img, args.hi, args.lo)

        if args.suffix:
            out_path = in_path.with_stem(in_path.stem + args.suffix)
        else:
            out_path = in_path

        if args.backup and out_path == in_path:
            bak = in_path.with_suffix(in_path.suffix + ".bak")
            if not bak.exists():
                bak.write_bytes(in_path.read_bytes())

        transparent.save(out_path, "PNG")
        size_kb = out_path.stat().st_size / 1024
        print(f"  [{args.mode}] {in_path.name} -> {out_path.name} ({size_kb:.1f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
