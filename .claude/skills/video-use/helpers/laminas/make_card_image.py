#!/usr/bin/env python3
"""Static fact-card images (no animation, no label, no sound) at reel size."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (245, 245, 245)
MARGIN_X = 90
TEXT_WIDTH = W - 2 * MARGIN_X


def make_background(bg_path: str) -> Image.Image:
    img = Image.open(bg_path).convert("RGB").resize((W, H), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(22))
    dark = Image.new("RGB", (W, H), (8, 8, 10))
    img = Image.blend(img, dark, 0.62)
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([-W * 0.3, -H * 0.15, W * 1.3, H * 1.05], fill=90)
    vignette = vignette.filter(ImageFilter.GaussianBlur(180))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, black, vignette)
    return img


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_image(text: str, out_path: str, bg_path: str, font_size: int = 52):
    bg = make_background(bg_path)
    d = ImageDraw.Draw(bg)
    font = ImageFont.truetype(FONT_BOLD, font_size)

    lines = wrap_text(d, text, font, TEXT_WIDTH)
    line_h = int(font_size * 1.38)
    block_h = line_h * len(lines)
    top = (H - block_h) // 2

    y = top
    for line in lines:
        lw = d.textlength(line, font=font)
        d.text(((W - lw) / 2, y), line, font=font, fill=WHITE)
        y += line_h

    bg.save(out_path)
    print(f"{out_path}: {len(lines)} lines, {len(text)} chars")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--bg", required=True)
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    for item in spec:
        render_image(text=item["text"], out_path=item["out"], bg_path=args.bg,
                      font_size=item.get("font_size", 52))
