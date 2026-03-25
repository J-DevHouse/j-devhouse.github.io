#!/usr/bin/env python3
"""
MultiSize ID Photo - App Store Screenshot Generator
====================================================
Uses actual app screenshots to create App Store marketing images.

Usage:
  1. Place screenshots in ./原截图/ folder
  2. Run: python3 generate.py
  3. Find exports in ./screenshots_6.7/, ./screenshots_6.5/, etc.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# Configuration
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "原截图")

# Font configuration (macOS)
FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
for fp in [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
]:
    if os.path.exists(fp):
        FONT_PATH = fp
        break

LATIN_FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
for fp in [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSDisplay.ttf",
]:
    if os.path.exists(fp):
        LATIN_FONT_PATH = fp
        break

WHITE = (255, 255, 255)
BLACK = (26, 26, 26)

# App Store sizes
SIZES = {
    "screenshots_6.7": (1290, 2796),   # iPhone 6.7"
    "screenshots_6.5": (1284, 2778),   # iPhone 6.5"
    "screenshots_5.5": (1242, 2208),   # iPhone 5.5"
    "screenshots_iPad_12.9": (2048, 2732),  # iPad 12.9"
}

# Screenshot definitions
SCREENSHOTS = [
    {
        "file": "IMG_4998.PNG",
        "headline": "ワンタップで\n背景を自動除去",
        "sub": "白・青・グレー・カスタム色から選択",
        "bg": ((0, 102, 204), (0, 71, 153)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_4999.PNG",
        "headline": "9種類の証明写真を\n1枚にまとめて印刷",
        "sub": "300DPI高画質・サイズ標注つきプレビュー",
        "bg": ((45, 85, 135), (30, 60, 100)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_5001.PNG",
        "headline": "サイズも枚数も\n自由自在に設定",
        "sub": "パスポート・履歴書・運転免許証 etc.",
        "bg": ((0, 122, 255), (0, 90, 200)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_5003.PNG",
        "headline": "背景色を\n自由にカスタマイズ",
        "sub": "プリセット＋カラーピッカーで自在に",
        "bg": ((200, 80, 50), (160, 55, 35)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_4869.PNG",
        "headline": "プロ級の美肌加工を\n指でなぞるだけ",
        "sub": "美肌・クマ除去・シワ除去",
        "bg": ((90, 60, 150), (65, 40, 115)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_4870.PNG",
        "headline": "履歴からいつでも\n無料で再利用",
        "sub": "一度共有した写真は何度でも無料",
        "bg": ((34, 139, 87), (25, 105, 65)),
        "text_color": WHITE,
    },
    {
        "file": "IMG_5002.PNG",
        "headline": "写真館より\n断然おトク",
        "sub": "作成・プレビュー・美肌加工は無料",
        "bg": ((50, 50, 55), (35, 35, 38)),
        "text_color": WHITE,
    },
]


def is_cjk_char(ch):
    cp = ord(ch)
    return (
        (0x3000 <= cp <= 0x303F) or
        (0x3040 <= cp <= 0x309F) or
        (0x30A0 <= cp <= 0x30FF) or
        (0x4E00 <= cp <= 0x9FFF) or
        (0xFF00 <= cp <= 0xFFEF) or
        (0x3400 <= cp <= 0x4DBF)
    )


def draw_mixed_text(draw, pos, text, cjk_font, latin_font, fill):
    x, y = pos
    for ch in text:
        if ch == ' ':
            bbox = draw.textbbox((0, 0), ' ', font=latin_font)
            x += bbox[2] - bbox[0]
            continue
        font = cjk_font if is_cjk_char(ch) else latin_font
        draw.text((x, y), ch, fill=fill, font=font)
        bbox = draw.textbbox((0, 0), ch, font=font)
        x += bbox[2] - bbox[0]
    return x


def measure_mixed_text(draw, text, cjk_font, latin_font):
    total_w = 0
    for ch in text:
        font = cjk_font if is_cjk_char(ch) else latin_font
        bbox = draw.textbbox((0, 0), ch, font=font)
        total_w += bbox[2] - bbox[0]
    return total_w


def create_gradient(width, height, color_top, color_bottom):
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return img


def add_rounded_corners(img, radius):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return result


def add_shadow(canvas, pos, size, radius=30, shadow_offset=8, shadow_blur=20, shadow_color=(0, 0, 0, 60)):
    sx, sy = pos[0] + shadow_offset, pos[1] + shadow_offset
    sw, sh = size
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(sx, sy), (sx + sw, sy + sh)],
        radius=radius,
        fill=shadow_color,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.paste(Image.alpha_composite(
        Image.new("RGBA", canvas.size, (0, 0, 0, 0)),
        shadow
    ), mask=shadow)


def is_ipad_size(target_width, target_height):
    return (target_width / target_height) > 0.6


def generate_screenshot(ss_config, target_width, target_height, raw_dir):
    file_path = os.path.join(raw_dir, ss_config["file"])
    if not os.path.exists(file_path):
        print(f"  ⚠ Missing: {ss_config['file']} - skipping")
        return None

    src = Image.open(file_path).convert("RGBA")
    src_w, src_h = src.size

    bg_top, bg_bottom = ss_config["bg"]
    canvas = create_gradient(target_width, target_height, bg_top, bg_bottom).convert("RGBA")

    ipad = is_ipad_size(target_width, target_height)

    if ipad:
        header_height = int(target_height * 0.22)
        bottom_padding = int(target_height * 0.01)
    else:
        header_height = int(target_height * 0.28)
        bottom_padding = int(target_height * 0.02)

    screenshot_area_height = target_height - header_height

    # Draw text
    draw = ImageDraw.Draw(canvas)

    if ipad:
        headline_font_size = int(target_width * 0.055)
        sub_font_size = int(target_width * 0.026)
    else:
        headline_font_size = int(target_width * 0.072)
        sub_font_size = int(target_width * 0.032)

    headline_cjk_font = ImageFont.truetype(FONT_PATH, headline_font_size)
    headline_latin_font = ImageFont.truetype(LATIN_FONT_PATH, headline_font_size)
    sub_cjk_font = ImageFont.truetype(FONT_PATH, sub_font_size)
    sub_latin_font = ImageFont.truetype(LATIN_FONT_PATH, sub_font_size)

    text_color = ss_config["text_color"]

    headline = ss_config["headline"]
    headline_y = int(header_height * 0.15)

    for i, line in enumerate(headline.split("\n")):
        tw = measure_mixed_text(draw, line, headline_cjk_font, headline_latin_font)
        tx = (target_width - tw) // 2
        ty = headline_y + i * int(headline_font_size * 1.35)
        draw_mixed_text(draw, (tx, ty), line, headline_cjk_font, headline_latin_font, fill=text_color)

    sub_text = ss_config["sub"]
    sub_tw = measure_mixed_text(draw, sub_text, sub_cjk_font, sub_latin_font)
    sub_y = headline_y + len(headline.split("\n")) * int(headline_font_size * 1.35) + int(sub_font_size * 0.8)
    sub_fill = (*text_color[:3], 200) if len(text_color) == 3 else text_color
    draw_mixed_text(
        draw,
        ((target_width - sub_tw) // 2, sub_y),
        sub_text,
        sub_cjk_font, sub_latin_font,
        fill=sub_fill,
    )

    # Place screenshot
    avail_h = screenshot_area_height - bottom_padding
    side_padding = int(target_width * 0.06)

    if ipad:
        crop_top = int(src_h * 0.05)
        src_cropped = src.crop((0, crop_top, src_w, src_h))
        crop_w, crop_h = src_cropped.size
        ipad_side_padding = int(target_width * 0.04)
        max_w = target_width - ipad_side_padding * 2
        scale = max_w / crop_w
        new_w = int(crop_w * scale)
        new_h = int(crop_h * scale)
        if new_h > avail_h * 1.2:
            scale = (avail_h * 1.2) / crop_h
            new_w = int(crop_w * scale)
            new_h = int(crop_h * scale)
        screenshot = src_cropped.resize((new_w, new_h), Image.LANCZOS)
        corner_radius = int(new_w * 0.025)
    else:
        avail_w = target_width - side_padding * 2
        scale = avail_w / src_w
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)
        if new_h > avail_h * 1.15:
            scale = (avail_h * 1.15) / src_h
            new_w = int(src_w * scale)
            new_h = int(src_h * scale)
        screenshot = src.resize((new_w, new_h), Image.LANCZOS)
        corner_radius = int(new_w * 0.04)

    screenshot = add_rounded_corners(screenshot, corner_radius)

    ss_x = (target_width - new_w) // 2
    ss_y = header_height

    add_shadow(canvas, (ss_x, ss_y), (new_w, new_h), radius=corner_radius)
    canvas.paste(screenshot, (ss_x, ss_y), screenshot)

    return canvas.convert("RGB")


def main():
    if not os.path.exists(RAW_DIR):
        print(f"  Error: {RAW_DIR}/ not found")
        sys.exit(1)

    raw_files = [f for f in os.listdir(RAW_DIR) if f.upper().endswith((".PNG", ".JPG", ".JPEG"))]

    if not raw_files:
        print(f"  No screenshots found in {RAW_DIR}/")
        sys.exit(1)

    print("=" * 60)
    print("  MultiSize ID Photo - Screenshot Generator")
    print("=" * 60)
    print(f"\n  Found {len(raw_files)} screenshots in 原截图/")
    print(f"  Font: {FONT_PATH}")
    print()

    for size_name, (width, height) in SIZES.items():
        size_dir = os.path.join(SCRIPT_DIR, size_name)
        os.makedirs(size_dir, exist_ok=True)

        # Clear old files
        for f in os.listdir(size_dir):
            os.remove(os.path.join(size_dir, f))

        print(f"--- {size_name} ({width}x{height}) ---")

        count = 0
        for idx, ss in enumerate(SCREENSHOTS):
            result = generate_screenshot(ss, width, height, RAW_DIR)
            if result:
                output_name = f"{idx + 1:02d}_screenshot.png"
                output_path = os.path.join(size_dir, output_name)
                result.save(output_path, "PNG", optimize=True)
                print(f"  ✓ {output_name}")
                count += 1

        print(f"  → {count} screenshots exported\n")

    print("✅ Done!")


if __name__ == "__main__":
    main()
