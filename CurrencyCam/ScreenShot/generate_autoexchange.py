#!/usr/bin/env python3
"""
AutoExchange App Store Screenshot Generator
=============================================
Generates App Store marketing screenshots from raw app screenshots.

Usage:
  1. Place screenshots in ./raw/en/ and ./raw/jp/ folders
  2. Run: python3 generate_autoexchange.py
  3. Find exports in ./exports/{lang}/{size}/
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

# Font configuration (macOS) - per-language CJK fonts
CJK_FONT_PATHS = {
    "ja": "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "zh-Hans": "/System/Library/Fonts/STHeiti Medium.ttc",
    "zh-Hant": "/System/Library/Fonts/STHeiti Medium.ttc",
    "default": "/System/Library/Fonts/Hiragino Sans GB.ttc",
}
# Verify fonts exist, fall back gracefully
_CJK_FALLBACKS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
for key in list(CJK_FONT_PATHS.keys()):
    if not os.path.exists(CJK_FONT_PATHS[key]):
        for fb in _CJK_FALLBACKS:
            if os.path.exists(fb):
                CJK_FONT_PATHS[key] = fb
                break

LATIN_FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
for fp in [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Avenir Next.ttc",
]:
    if os.path.exists(fp):
        LATIN_FONT_PATH = fp
        break


def get_cjk_font_path(lang):
    """Get the appropriate CJK font for a given language."""
    return CJK_FONT_PATHS.get(lang, CJK_FONT_PATHS["default"])

# App theme colors - blue tones matching the app's UI
THEME_BLUE = (30, 110, 220)
THEME_DARK_BLUE = (20, 70, 160)
WHITE = (255, 255, 255)

# App Store sizes (iPhone only)
SIZES = {
    "6.9": (1320, 2868),     # iPhone 16 Pro Max
    "6.5": (1284, 2778),     # iPhone 15 Plus / 14 Pro Max
    "5.5": (1242, 2208),     # iPhone 8 Plus
    "ipad13": (2064, 2752),  # iPad Pro 13" (M4)
}

# Screenshot definitions per language
# Each entry: (raw_filename, headline, sub_headline, bg_gradient_colors)
SCREENSHOTS = {
    "en": [
        {
            "file": "IMG_4979.PNG",
            "headline": "Point Your Camera\nInstant Conversion",
            "sub": "Automatically detect amounts and convert currencies in real-time",
            "bg": ((30, 110, 220), (20, 70, 160)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4977.PNG",
            "headline": "Customize Rates\n& Currencies",
            "sub": "Set source currency and multiple target rates",
            "bg": ((44, 62, 80), (26, 37, 47)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4978.PNG",
            "headline": "30+ Currencies\nSupported",
            "sub": "Major and regional currencies from around the world",
            "bg": ((91, 134, 229), (54, 130, 200)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4993.PNG",
            "headline": "Multiple Languages\nSupported",
            "sub": "English, Japanese, Chinese, Spanish and more",
            "bg": ((79, 121, 113), (55, 90, 83)),
            "text_color": WHITE,
        },
    ],
    "jp": [
        {
            "file": "IMG_4973.PNG",
            "headline": "カメラをかざすだけ\n瞬時に為替換算",
            "sub": "金額を自動検出してリアルタイムで通貨換算",
            "bg": ((30, 110, 220), (20, 70, 160)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4974.PNG",
            "headline": "レートと通貨を\n自由にカスタマイズ",
            "sub": "元通貨と複数の目標通貨を設定可能",
            "bg": ((44, 62, 80), (26, 37, 47)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4975.PNG",
            "headline": "30以上の通貨に\n対応",
            "sub": "主要通貨からアジア・各地域の通貨まで幅広くサポート",
            "bg": ((91, 134, 229), (54, 130, 200)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4976.PNG",
            "headline": "多言語対応",
            "sub": "日本語・英語・中国語・スペイン語などに対応",
            "bg": ((79, 121, 113), (55, 90, 83)),
            "text_color": WHITE,
        },
    ],
    "zh-Hans": [
        {
            "file": "IMG_4990.PNG",
            "headline": "对准相机\n即刻换算",
            "sub": "自动识别金额，实时转换为目标货币",
            "bg": ((30, 110, 220), (20, 70, 160)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4985.PNG",
            "headline": "自定义汇率\n与目标货币",
            "sub": "设置源货币和多个目标汇率",
            "bg": ((44, 62, 80), (26, 37, 47)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4986.PNG",
            "headline": "支持50+种\n全球货币",
            "sub": "涵盖主要货币及各地区货币",
            "bg": ((91, 134, 229), (54, 130, 200)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4994.PNG",
            "headline": "多语言支持",
            "sub": "中文、英语、日语、西班牙语等",
            "bg": ((79, 121, 113), (55, 90, 83)),
            "text_color": WHITE,
        },
    ],
    "zh-Hant": [
        {
            "file": "IMG_4989.PNG",
            "headline": "對準相機\n即刻換算",
            "sub": "自動辨識金額，即時轉換為目標貨幣",
            "bg": ((30, 110, 220), (20, 70, 160)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4987.PNG",
            "headline": "自訂匯率\n與目標貨幣",
            "sub": "設定來源貨幣和多個目標匯率",
            "bg": ((44, 62, 80), (26, 37, 47)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4988.PNG",
            "headline": "支援50+種\n全球貨幣",
            "sub": "涵蓋主要貨幣及各地區貨幣",
            "bg": ((91, 134, 229), (54, 130, 200)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4995.PNG",
            "headline": "多語言支援",
            "sub": "中文、英語、日語、西班牙語等",
            "bg": ((79, 121, 113), (55, 90, 83)),
            "text_color": WHITE,
        },
    ],
    "es": [
        {
            "file": "IMG_4980.PNG",
            "headline": "Apunta tu Cámara\nConversión Instantánea",
            "sub": "Detecta importes automáticamente y convierte divisas en tiempo real",
            "bg": ((30, 110, 220), (20, 70, 160)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4983.PNG",
            "headline": "Personaliza Tasas\ny Monedas",
            "sub": "Configura la moneda origen y múltiples tasas destino",
            "bg": ((44, 62, 80), (26, 37, 47)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4984.PNG",
            "headline": "Más de 50 Monedas\nDisponibles",
            "sub": "Divisas principales y regionales de todo el mundo",
            "bg": ((91, 134, 229), (54, 130, 200)),
            "text_color": WHITE,
        },
        {
            "file": "IMG_4992.PNG",
            "headline": "Soporte\nMultiidioma",
            "sub": "Español, inglés, japonés, chino y más",
            "bg": ((79, 121, 113), (55, 90, 83)),
            "text_color": WHITE,
        },
    ],
}

# Languages without their own raw/ subfolder will fall back to en raw screenshots
RAW_DIR_FALLBACK = "en"


def is_cjk_char(ch):
    """Check if character is CJK (needs CJK font)."""
    cp = ord(ch)
    return (
        (0x3000 <= cp <= 0x303F) or
        (0x3040 <= cp <= 0x309F) or
        (0x30A0 <= cp <= 0x30FF) or
        (0x4E00 <= cp <= 0x9FFF) or
        (0xFF00 <= cp <= 0xFFEF) or
        (0x3400 <= cp <= 0x4DBF) or
        (0x20000 <= cp <= 0x2A6DF) or
        (0x2E80 <= cp <= 0x2FDF) or
        (0xF900 <= cp <= 0xFAFF) or
        (0xFE30 <= cp <= 0xFE4F)
    )


def draw_mixed_text(draw, pos, text, cjk_font, latin_font, fill):
    """Draw text with font fallback: CJK font for Japanese/Chinese, Latin font for ASCII."""
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
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)
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
    return target_width / target_height > 0.6  # iPad ~0.75, iPhone ~0.46


def generate_screenshot(ss_config, target_width, target_height, raw_dir, lang="en"):
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

    # Layout calculations
    if ipad:
        header_height = int(target_height * 0.22)
        side_padding = int(target_width * 0.18)
        bottom_padding = int(target_height * 0.01)
    else:
        header_height = int(target_height * 0.28)
        side_padding = int(target_width * 0.06)
        bottom_padding = int(target_height * 0.02)

    screenshot_area_height = target_height - header_height

    # Draw headline text
    draw = ImageDraw.Draw(canvas)

    if ipad:
        headline_font_size = int(target_width * 0.055)
        sub_font_size = int(target_width * 0.026)
    else:
        headline_font_size = int(target_width * 0.072)
        sub_font_size = int(target_width * 0.032)

    cjk_font_path = get_cjk_font_path(lang)
    headline_cjk_font = ImageFont.truetype(cjk_font_path, headline_font_size)
    headline_latin_font = ImageFont.truetype(LATIN_FONT_PATH, headline_font_size)
    sub_cjk_font = ImageFont.truetype(cjk_font_path, sub_font_size)
    sub_latin_font = ImageFont.truetype(LATIN_FONT_PATH, sub_font_size)

    text_color = ss_config["text_color"]

    # Headline - centered
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

    # If sub text is too wide, wrap it
    max_text_width = int(target_width * 0.88)
    if sub_tw > max_text_width:
        words = list(sub_text)
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word
            test_tw = measure_mixed_text(draw, test_line, sub_cjk_font, sub_latin_font)
            if test_tw > max_text_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_tw = measure_mixed_text(draw, line, sub_cjk_font, sub_latin_font)
            sub_fill = (*text_color[:3], 200) if len(text_color) == 3 else text_color
            draw_mixed_text(
                draw,
                ((target_width - line_tw) // 2, sub_y + i * int(sub_font_size * 1.4)),
                line,
                sub_cjk_font, sub_latin_font,
                fill=sub_fill,
            )
    else:
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

    if ipad:
        # iPad: crop iPhone status bar, scale to fill width with less padding
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
        screenshot = add_rounded_corners(screenshot, corner_radius)
    else:
        # iPhone
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
    print("=" * 60)
    print("  AutoExchange App Store Screenshot Generator")
    print("=" * 60)
    print(f"\n  CJK Fonts: {CJK_FONT_PATHS}")
    print(f"  Latin Font: {LATIN_FONT_PATH}")
    print()

    for lang, screenshots in SCREENSHOTS.items():
        lang_raw_dir = os.path.join(RAW_DIR, lang)
        if not os.path.exists(lang_raw_dir):
            # Fall back to default raw directory
            lang_raw_dir = os.path.join(RAW_DIR, RAW_DIR_FALLBACK)
            if not os.path.exists(lang_raw_dir):
                print(f"⚠ Raw directory not found for {lang} - skipping")
                continue
            print(f"  [{lang.upper()}] Using {RAW_DIR_FALLBACK}/ raw screenshots as base")

        raw_files = [f for f in os.listdir(lang_raw_dir)
                     if f.upper().endswith((".PNG", ".JPG", ".JPEG"))]
        print(f"  [{lang.upper()}] Found {len(raw_files)} screenshots in {lang_raw_dir}/")

        for size_name, (width, height) in SIZES.items():
            size_dir = os.path.join(EXPORT_DIR, lang, size_name)
            os.makedirs(size_dir, exist_ok=True)
            device = "iPad" if size_name.startswith("ipad") else "iPhone"
            print(f"\n  --- [{lang.upper()}] {device} {size_name} ({width}x{height}) ---")

            count = 0
            for idx, ss in enumerate(screenshots):
                result = generate_screenshot(ss, width, height, lang_raw_dir, lang=lang)
                if result:
                    # Name based on screenshot content
                    base = os.path.splitext(ss["file"])[0]
                    output_name = f"{idx + 1:02d}_{base}.png"
                    output_path = os.path.join(size_dir, output_name)
                    result.save(output_path, "PNG", optimize=True)
                    print(f"    ✓ {output_name}")
                    count += 1

            print(f"    → {count} screenshots exported")

    print(f"\n✅ Done! Exports saved to: {EXPORT_DIR}/")
    print()
    print("Next steps:")
    print("  1. Review the exports in each lang/size folder")
    print("  2. Upload to App Store Connect")
    print("     - en/6.9/ → English, iPhone 6.9\" Display")
    print("     - en/6.5/ → English, iPhone 6.5\" Display")
    print("     - en/5.5/ → English, iPhone 5.5\" Display")
    print("     - jp/6.9/ → Japanese, iPhone 6.9\" Display")
    print("     - (etc.)")


if __name__ == "__main__":
    main()
