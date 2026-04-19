#!/usr/bin/env python3
"""
MManager App Store Screenshot Generator
========================================
Uses actual app screenshots to create App Store marketing images.

Usage:
  1. Place your screenshots in ./raw/ folder with these names:
     - 01_calendar.png     (カレンダー画面)
     - 02_scan.png          (レシートスキャン画面)
     - 03_input.png         (入力画面)
     - 04_statistics.png    (統計画面)
     - 05_widget.png        (ウィジェット画面)
     - 06_scanlist.png      (スキャン一覧画面)
     - 07_category.png      (カテゴリー選択画面)
     - 08_settings.png      (設定画面)

  2. Run: python3 generate.py

  3. Find exports in:
     ./exports/6.9/   (1320x2868 - iPhone 16 Pro Max)
     ./exports/6.5/   (1284x2778 - iPhone 15 Plus etc.)
     ./exports/5.5/   (1242x2208 - iPhone 8 Plus etc.)
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# Configuration
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")

# Japanese font (CJK)
FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
# Try better CJK fonts first
for fp in [
    "/sessions/blissful-ecstatic-pasteur/fonts/NotoSansCJKjp-Bold.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]:
    if os.path.exists(fp):
        FONT_PATH = fp
        break

# Latin/number fallback font
LATIN_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
for fp in [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]:
    if os.path.exists(fp):
        LATIN_FONT_PATH = fp
        break

# App theme colors
THEME_COLOR = (79, 121, 113)        # #4F7971
THEME_DARK = (61, 94, 88)           # #3D5E58
THEME_BG = (238, 246, 248)          # #EEF6F8
WHITE = (255, 255, 255)
BLACK = (26, 26, 26)

# App Store sizes
SIZES = {
    "6.9": (1320, 2868),   # iPhone 16 Pro Max
    "6.5": (1284, 2778),   # iPhone 15 Plus / 14 Pro Max
    "5.5": (1242, 2208),   # iPhone 8 Plus
    "ipad13": (2064, 2752),  # iPad Pro 13" (M4)
    "ipad12.9": (2048, 2732),  # iPad Pro 12.9" (3rd gen+)
}

# Screenshot definitions: (filename, headline, sub_headline, bg_colors)
# bg_colors = (top_color, bottom_color) for gradient
SCREENSHOTS = [
    {
        "file": "01_calendar.png",
        "headline": "日々の支出を\nカレンダーで管理",
        "sub": "日付ごとの合計が一目でわかる",
        "bg": ((79, 121, 113), (55, 90, 83)),
        "text_color": WHITE,
    },
    {
        "file": "02_scan.png",
        "headline": "レシートを撮るだけ\n自動でデータ化",
        "sub": "高精度な文字認識で日本語レシートを即座に読取",
        "bg": ((44, 62, 80), (26, 37, 47)),
        "text_color": WHITE,
    },
    {
        "file": "03_input.png",
        "headline": "スキャン結果から\nワンタップで記録",
        "sub": "金額・日付・カテゴリーを自動入力",
        "bg": ((0, 180, 219), (0, 131, 176)),
        "text_color": WHITE,
    },
    {
        "file": "04_statistics.png",
        "headline": "支出の傾向を\nグラフで分析",
        "sub": "月別・カテゴリー別に支出を把握",
        "bg": ((91, 134, 229), (54, 209, 220)),
        "text_color": WHITE,
    },
    {
        "file": "05_widget.png",
        "headline": "ウィジェットで\n素早くアクセス",
        "sub": "ホーム画面からワンタップで記録",
        "bg": ((142, 68, 173), (108, 52, 131)),
        "text_color": WHITE,
    },
    {
        "file": "06_scanlist.png",
        "headline": "スキャン履歴を\nまとめて管理",
        "sub": "過去のレシートをいつでも確認",
        "bg": ((79, 121, 113), (55, 90, 83)),
        "text_color": WHITE,
    },
    {
        "file": "07_category.png",
        "headline": "豊富なカテゴリで\n支出を簡単分類",
        "sub": "固定費・変動費を自動で整理",
        "bg": ((232, 131, 107), (214, 109, 85)),
        "text_color": WHITE,
    },
    {
        "file": "08_settings.png",
        "headline": "お好みに合わせて\nカスタマイズ",
        "sub": "画質設定・広告管理など",
        "bg": ((52, 73, 94), (44, 62, 80)),
        "text_color": WHITE,
    },
]


def is_cjk_char(ch):
    """Check if character is CJK (needs Japanese font)."""
    cp = ord(ch)
    return (
        (0x3000 <= cp <= 0x303F) or   # CJK Punctuation
        (0x3040 <= cp <= 0x309F) or   # Hiragana
        (0x30A0 <= cp <= 0x30FF) or   # Katakana
        (0x4E00 <= cp <= 0x9FFF) or   # CJK Unified Ideographs
        (0xFF00 <= cp <= 0xFFEF) or   # Fullwidth Forms
        (0x3400 <= cp <= 0x4DBF) or   # CJK Extension A
        (0x20000 <= cp <= 0x2A6DF) or # CJK Extension B
        (0x2E80 <= cp <= 0x2FDF) or   # CJK Radicals
        (0xF900 <= cp <= 0xFAFF) or   # CJK Compatibility
        (0xFE30 <= cp <= 0xFE4F)      # CJK Compatibility Forms
    )


def draw_mixed_text(draw, pos, text, cjk_font, latin_font, fill):
    """Draw text with font fallback: CJK font for Japanese, Latin font for ASCII."""
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
    return x  # return final x position


def measure_mixed_text(draw, text, cjk_font, latin_font):
    """Measure width of mixed CJK/Latin text."""
    total_w = 0
    for ch in text:
        font = cjk_font if is_cjk_char(ch) else latin_font
        bbox = draw.textbbox((0, 0), ch, font=font)
        total_w += bbox[2] - bbox[0]
    return total_w


def create_gradient(width, height, color_top, color_bottom):
    """Create a vertical gradient image."""
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
    """Add rounded corners to an image using alpha channel."""
    w, h = img.size
    # Create a rounded rectangle mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)

    # Apply mask
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return result


def add_shadow(canvas, pos, size, radius=30, shadow_offset=8, shadow_blur=20, shadow_color=(0, 0, 0, 60)):
    """Draw a soft shadow behind where the screenshot will go."""
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
    """Check if the target size is an iPad size (wider aspect ratio)."""
    aspect = target_width / target_height
    return aspect > 0.6  # iPad is ~0.75, iPhone is ~0.46


def generate_screenshot(ss_config, target_width, target_height, raw_dir):
    """Generate a single App Store screenshot."""
    file_path = os.path.join(raw_dir, ss_config["file"])
    if not os.path.exists(file_path):
        print(f"  ⚠ Missing: {ss_config['file']} - skipping")
        return None

    # Load source screenshot
    src = Image.open(file_path).convert("RGBA")
    src_w, src_h = src.size

    # Create canvas with gradient background
    bg_top, bg_bottom = ss_config["bg"]
    canvas = create_gradient(target_width, target_height, bg_top, bg_bottom).convert("RGBA")

    ipad = is_ipad_size(target_width, target_height)

    # --- Layout calculations ---
    if ipad:
        # iPad: smaller header, screenshot fills more of the canvas
        header_height = int(target_height * 0.22)
        side_padding = int(target_width * 0.18)  # more side padding to center narrow screenshot wider
        bottom_padding = int(target_height * 0.01)
    else:
        # iPhone: original layout
        header_height = int(target_height * 0.28)
        side_padding = int(target_width * 0.06)
        bottom_padding = int(target_height * 0.02)

    screenshot_area_height = target_height - header_height

    # --- Draw headline text ---
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

    # Headline - centered, with mixed font support
    headline = ss_config["headline"]
    headline_y = int(header_height * 0.15)

    for i, line in enumerate(headline.split("\n")):
        tw = measure_mixed_text(draw, line, headline_cjk_font, headline_latin_font)
        tx = (target_width - tw) // 2
        ty = headline_y + i * int(headline_font_size * 1.35)
        draw_mixed_text(draw, (tx, ty), line, headline_cjk_font, headline_latin_font, fill=text_color)

    # Sub-headline
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

    # --- Place screenshot ---
    avail_h = screenshot_area_height - bottom_padding

    if ipad:
        # iPad: crop iPhone status bar (top ~5%) to remove iPhone-specific UI,
        # then scale to fill the iPad canvas width as much as possible.
        crop_top = int(src_h * 0.05)
        src_cropped = src.crop((0, crop_top, src_w, src_h))
        crop_w, crop_h = src_cropped.size

        # Scale to fill available width with minimal padding
        ipad_side_padding = int(target_width * 0.04)
        max_w = target_width - ipad_side_padding * 2
        scale = max_w / crop_w
        new_w = int(crop_w * scale)
        new_h = int(crop_h * scale)

        # Cap height so it doesn't overflow too much
        if new_h > avail_h * 1.2:
            scale = (avail_h * 1.2) / crop_h
            new_w = int(crop_w * scale)
            new_h = int(crop_h * scale)

        screenshot = src_cropped.resize((new_w, new_h), Image.LANCZOS)
        corner_radius = int(new_w * 0.025)
        screenshot = add_rounded_corners(screenshot, corner_radius)
    else:
        # iPhone: original scaling logic
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

    # Position: centered horizontally, starting from header bottom
    ss_x = (target_width - new_w) // 2
    ss_y = header_height

    # Add shadow
    add_shadow(canvas, (ss_x, ss_y), (new_w, new_h), radius=corner_radius)

    # Paste screenshot
    canvas.paste(screenshot, (ss_x, ss_y), screenshot)

    return canvas.convert("RGB")


def main():
    # Check for raw screenshots
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR, exist_ok=True)

    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"))]

    if not raw_files:
        print("=" * 60)
        print("  MManager App Store Screenshot Generator")
        print("=" * 60)
        print()
        print(f"  Please place your screenshots in: {RAW_DIR}/")
        print()
        print("  Expected filenames:")
        for ss in SCREENSHOTS:
            print(f"    - {ss['file']}")
        print()
        print("  You can use any subset - missing files will be skipped.")
        print("  Filenames can also be .jpg or .jpeg.")
        print()

        # Also check for any files with different names
        print("  Tip: If your files have different names,")
        print("  just rename them to match the expected names above.")
        sys.exit(0)

    print("=" * 60)
    print("  MManager App Store Screenshot Generator")
    print("=" * 60)
    print(f"\n  Found {len(raw_files)} screenshots in {RAW_DIR}/")
    print(f"  Font: {FONT_PATH}")
    print()

    # Also support .jpg/.jpeg extensions
    for ss in SCREENSHOTS:
        base = os.path.splitext(ss["file"])[0]
        for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]:
            candidate = base + ext
            if os.path.exists(os.path.join(RAW_DIR, candidate)):
                ss["file"] = candidate
                break

    # Generate for each size
    for size_name, (width, height) in SIZES.items():
        size_dir = os.path.join(EXPORT_DIR, size_name)
        os.makedirs(size_dir, exist_ok=True)
        device = "iPad" if size_name.startswith("ipad") else "iPhone"
        print(f"--- {device} {size_name}\" ({width}x{height}) ---")

        count = 0
        for idx, ss in enumerate(SCREENSHOTS):
            result = generate_screenshot(ss, width, height, RAW_DIR)
            if result:
                output_name = f"{idx + 1:02d}_{os.path.splitext(ss['file'])[0].split('_', 1)[-1]}.png"
                output_path = os.path.join(size_dir, output_name)
                result.save(output_path, "PNG", optimize=True)
                print(f"  ✓ {output_name}")
                count += 1

        print(f"  → {count} screenshots exported\n")

    print(f"✅ Done! Exports saved to: {EXPORT_DIR}/")
    print()
    print("Next steps:")
    print("  1. Review the exports in each size folder")
    print("  2. Upload to App Store Connect")
    print("     - 6.9\" folder → iPhone 6.9\" Display")
    print("     - 6.5\" folder → iPhone 6.5\" Display")
    print("     - 5.5\" folder → iPhone 5.5\" Display")


if __name__ == "__main__":
    main()
