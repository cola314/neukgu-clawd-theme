#!/usr/bin/env python3
"""
Align frames to an anchor by bbox centering. Local only, no API cost.

Finds the bounding box of non-white content in each frame, then shifts
every frame so that its content-center matches the anchor's content-center.
Missing edges are filled with white.

Usage:
  python align-frames.py \\
      --anchor ../../themes/neukgu/assets/typing-f1.png \\
      --out-dir ../../themes/neukgu/assets/aligned/ \\
      ../../themes/neukgu/assets/typing-f1.png \\
      ../../themes/neukgu/assets/typing-f2.png \\
      ../../themes/neukgu/assets/typing-f3.png
"""
from __future__ import annotations
import argparse
import pathlib
import sys
from PIL import Image

WHITE_THRESHOLD = 240


def content_bbox(img: Image.Image, roi: tuple[int, int, int, int] | None = None) -> tuple[int, int, int, int] | None:
    """Return (x0, y0, x1, y1) of visible content, optionally restricted to ROI.
    Uses alpha for RGBA, threshold for RGB."""
    if roi is not None:
        cropped = img.crop(roi)
        inner = content_bbox(cropped, roi=None)
        if inner is None:
            return None
        return (inner[0] + roi[0], inner[1] + roi[1], inner[2] + roi[0], inner[3] + roi[1])

    if img.mode == "RGBA":
        return img.split()[3].getbbox()
    gray = img.convert("L")
    mask = gray.point(lambda p: 255 if p < WHITE_THRESHOLD else 0)
    return mask.getbbox()


def bbox_anchor(
    bbox: tuple[int, int, int, int],
    x_mode: str = "center",
    y_mode: str = "center",
) -> tuple[float, float]:
    x0, y0, x1, y1 = bbox
    ax = {"left": x0, "center": (x0 + x1) / 2.0, "right": x1}[x_mode]
    ay = {"top": y0, "center": (y0 + y1) / 2.0, "bottom": y1}[y_mode]
    return (ax, ay)


def shift_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    mode = img.mode if img.mode in ("RGB", "RGBA") else "RGB"
    # RGBA: fill exposed edges with TRANSPARENT (not opaque white)
    fill = (0, 0, 0, 0) if mode == "RGBA" else (255, 255, 255)
    new = Image.new(mode, img.size, fill)
    new.paste(img.convert(mode), (dx, dy))
    return new


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--anchor", required=True, help="Reference frame to align to")
    p.add_argument("--out-dir", required=True, help="Output directory for aligned frames")
    p.add_argument("--x-anchor", choices=["left", "center", "right"], default="center",
                   help="Which bbox edge to align horizontally")
    p.add_argument("--y-anchor", choices=["top", "center", "bottom"], default="center",
                   help="Which bbox edge to align vertically")
    p.add_argument("--roi", default=None,
                   help="Restrict bbox calculation to this region: x0,y0,x1,y1 (absolute pixel coords)")
    p.add_argument("inputs", nargs="+", help="Input frames (anchor is passed through)")
    args = p.parse_args()

    roi = None
    if args.roi:
        roi = tuple(int(x) for x in args.roi.split(","))
        if len(roi) != 4:
            print("--roi must be x0,y0,x1,y1", file=sys.stderr)
            return 1

    anchor_path = pathlib.Path(args.anchor).resolve()
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    anchor_img = Image.open(anchor_path)
    anchor_bbox = content_bbox(anchor_img, roi=roi)
    if anchor_bbox is None:
        print(f"anchor {anchor_path} has no content", file=sys.stderr)
        return 1
    anchor_cx, anchor_cy = bbox_anchor(anchor_bbox, args.x_anchor, args.y_anchor)
    print(f"Anchor: {anchor_path.name}  bbox={anchor_bbox}  anchor({args.x_anchor},{args.y_anchor})=({anchor_cx:.1f}, {anchor_cy:.1f})")

    for in_str in args.inputs:
        in_path = pathlib.Path(in_str).resolve()
        img = Image.open(in_path)
        out_path = out_dir / in_path.name

        if in_path == anchor_path:
            img.save(out_path)
            print(f"  {in_path.name}: ANCHOR, saved as-is")
            continue

        bbox = content_bbox(img, roi=roi)
        if bbox is None:
            print(f"  {in_path.name}: blank, skipping", file=sys.stderr)
            continue
        cx, cy = bbox_anchor(bbox, args.x_anchor, args.y_anchor)
        dx = int(round(anchor_cx - cx))
        dy = int(round(anchor_cy - cy))
        aligned = shift_image(img, dx, dy)
        aligned.save(out_path)
        print(f"  {in_path.name}: bbox={bbox}  anchor=({cx:.1f}, {cy:.1f})  shift=({dx:+d}, {dy:+d})")

    print(f"Aligned frames in: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
