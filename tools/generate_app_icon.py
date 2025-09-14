#!/usr/bin/env python3
"""
Generate a 1024x1024 PNG app icon (no transparency) and iOS icon set variants.

Requirements: Pillow
  pip install pillow

Usage examples:
  python tools/generate_app_icon.py                   # default blue/purple gradient with "AI" monogram
  python tools/generate_app_icon.py --text AIL        # custom text
  python tools/generate_app_icon.py --bg #4F46E5      # solid background color
  python tools/generate_app_icon.py --from icon.png   # use an existing 1024x1024 image as base (solid bg enforced)

This script will:
- Create frontend/public/icon_1024.png (for web/marketing convenience)
- Create iOS icon PNGs in ios/Runner/Assets.xcassets/AppIcon.appiconset/
- Update the AppIcon Contents.json to reference the generated filenames
"""

import argparse
import json
import os
from pathlib import Path
from typing import Tuple, List

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IOS_APPICON_DIR = ROOT / "flutter_app/ios/Runner/Assets.xcassets/AppIcon.appiconset"
FRONTEND_PUBLIC = ROOT / "frontend/public"

# Mapping of iOS app icon entries (idiom, size points, scale) to filenames
IOS_ICON_SPECS = [
    ("iphone", (20, 20), 2, "Icon-20@2x.png"),
    ("iphone", (20, 20), 3, "Icon-20@3x.png"),
    ("iphone", (29, 29), 2, "Icon-29@2x.png"),
    ("iphone", (29, 29), 3, "Icon-29@3x.png"),
    ("iphone", (40, 40), 2, "Icon-40@2x.png"),
    ("iphone", (40, 40), 3, "Icon-40@3x.png"),
    ("iphone", (60, 60), 2, "Icon-60@2x.png"),
    ("iphone", (60, 60), 3, "Icon-60@3x.png"),
    ("ipad", (20, 20), 1, "Icon-20~ipad.png"),
    ("ipad", (20, 20), 2, "Icon-20@2x~ipad.png"),
    ("ipad", (29, 29), 1, "Icon-29~ipad.png"),
    ("ipad", (29, 29), 2, "Icon-29@2x~ipad.png"),
    ("ipad", (40, 40), 1, "Icon-40~ipad.png"),
    ("ipad", (40, 40), 2, "Icon-40@2x~ipad.png"),
    ("ipad", (76, 76), 2, "Icon-76@2x~ipad.png"),
    ("ipad", (83.5, 83.5), 2, "Icon-83.5@2x~ipad.png"),
    ("ios-marketing", (1024, 1024), 1, "Icon-Marketing-1024.png"),
]


def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)


def ensure_dirs():
    IOS_APPICON_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)


def draw_gradient(size: int, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (size, size), start)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        ratio = y / (size - 1)
        r = int(start[0] * (1 - ratio) + end[0] * ratio)
        g = int(start[1] * (1 - ratio) + end[1] * ratio)
        b = int(start[2] * (1 - ratio) + end[2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    return img


def create_base_icon(text: str, bg: str = None, use_image: Path = None) -> Image.Image:
    size = 1024
    if use_image and use_image.exists():
        img = Image.open(use_image).convert("RGB")  # enforce no alpha
        img = img.resize((size, size), Image.LANCZOS)
    else:
        if bg:
            color = hex_to_rgb(bg)
            img = Image.new("RGB", (size, size), color)
        else:
            # default gradient: indigo -> purple
            img = draw_gradient(size, hex_to_rgb("#667eea"), hex_to_rgb("#764ba2"))

    # Draw centered monogram text
    draw = ImageDraw.Draw(img)
    # Try to find a decent font
    font_paths: List[str] = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    font = None
    for p in font_paths:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 360)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    # Newer versions of Pillow use textbbox. The origin (0,0) is fine for getting size.
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older Pillow versions
        w, h = draw.textsize(text, font=font)

    x = (size - w) // 2
    y = (size - h) // 2
    # Text with subtle shadow for contrast
    shadow_color = (0, 0, 0)
    draw.text((x+4, y+4), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    return img


def save_ios_icons(base_img: Image.Image):
    for idiom, (pt_w, pt_h), scale, filename in IOS_ICON_SPECS:
        px = int(round(pt_w * scale))
        # Account for marketing icon specified directly in px
        if idiom == "ios-marketing":
            px = 1024
        icon = base_img.resize((px, px), Image.LANCZOS)
        out_path = IOS_APPICON_DIR / filename
        icon.save(out_path, format="PNG")


def update_contents_json():
    contents_path = IOS_APPICON_DIR / "Contents.json"
    if contents_path.exists():
        with open(contents_path, "r") as f:
            data = json.load(f)
    else:
        data = {"images": [], "info": {"version": 1, "author": "xcode"}}

    # Build a lookup to match entries by idiom/size/scale
    def size_str(pt_w: float, pt_h: float) -> str:
        if float(pt_w).is_integer() and float(pt_h).is_integer():
            return f"{int(pt_w)}x{int(pt_h)}"
        return f"{pt_w}x{pt_h}"

    wanted = {}
    for idiom, (pt_w, pt_h), scale, filename in IOS_ICON_SPECS:
        wanted[(idiom, size_str(pt_w, pt_h), f"{scale}x")] = filename

    # Update or append
    images = data.get("images", [])
    for entry in images:
        key = (
            entry.get("idiom"),
            entry.get("size"),
            entry.get("scale"),
        )
        if key in wanted:
            entry["filename"] = wanted[key]

    existing_keys = {(e.get("idiom"), e.get("size"), e.get("scale")) for e in images}
    for (idiom, size_s, scale_s), filename in wanted.items():
        if (idiom, size_s, scale_s) not in existing_keys:
            images.append({
                "idiom": idiom,
                "size": size_s,
                "scale": scale_s,
                "filename": filename,
            })

    data["images"] = images
    with open(contents_path, "w") as f:
        json.dump(data, f, indent=2)


def save_marketing_copy(base_img: Image.Image):
    out = FRONTEND_PUBLIC / "icon_1024.png"
    base_img.save(out, format="PNG")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="AI", help="Monogram text")
    parser.add_argument("--bg", default=None, help="Solid background HEX color (e.g., #4F46E5)")
    parser.add_argument("--from", dest="from_image", default=None, help="Use existing 1024x1024 image (path)")
    args = parser.parse_args()

    ensure_dirs()

    use_image = Path(args.from_image) if args.from_image else None
    base = create_base_icon(args.text[:4], bg=args.bg, use_image=use_image)

    save_marketing_copy(base)
    save_ios_icons(base)
    update_contents_json()

    print("Generated 1024x1024 icon and iOS icon set.\n")
    print(f"- Marketing: {FRONTEND_PUBLIC / 'icon_1024.png'}")
    print(f"- iOS AppIcon set in: {IOS_APPICON_DIR}")


if __name__ == "__main__":
    main()
