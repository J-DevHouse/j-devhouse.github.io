#!/usr/bin/env python3
"""
VideoSorter App Store Screenshot Generator
=============================================
Generates App Store marketing screenshots from raw app screenshots.

Usage:
  1. Place screenshots in ./raw/{lang}/ folders (en, jp, zh-Hans, zh-Hant, es, ko)
     Each folder needs 3 screenshots (main screen, video list, directory creation)
  2. Run: python3 generate_videosorter.py
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
    "ko": "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "default": "/System/Library/Fonts/Hiragino Sans GB.ttc",
}
_CJK_FALLBACKS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
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
    return CJK_FONT_PATHS.get(lang, CJK_FONT_PATHS["default"])

WHITE = (255, 255, 255)

# App Store sizes
SIZES = {
    "6.5": (1284, 2778),     # iPhone 15 Plus / 14 Pro Max
    "ipad13": (2064, 2752),  # iPad Pro 13" (M4)
}

# Slot background colors (3 slots)
SLOT_BG = [
    ((30, 110, 220), (20, 70, 160)),     # 1. Main screen - blue
    ((79, 121, 113), (55, 90, 83)),      # 2. Video list - teal
    ((103, 82, 171), (66, 51, 119)),     # 3. Create directory - purple
]

# Screenshot definitions per language
# Each language has 3 screenshots: main screen, video list, create directory
SCREENSHOTS = {
    "en": [
        {
            "file": "IMG_5116.PNG",
            "headline": "Auto-Organize\nYour Videos",
            "sub": "Smart folders sort your recordings by weekday, time, and date",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5117.PNG",
            "headline": "Browse Videos\nby Folder",
            "sub": "Play, pin, and manage videos within each classified directory",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5118.PNG",
            "headline": "Set Your Own\nClassification Rules",
            "sub": "Filter by weekday, time range, date range, and duration",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
    "jp": [
        {
            "file": "IMG_5119.PNG",
            "headline": "動画を自動で\nフォルダに整理",
            "sub": "曜日・時間帯・日付のルールで録画を自動分類",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5120.PNG",
            "headline": "フォルダごとに\n動画を閲覧",
            "sub": "再生・ピン留め・管理を分類フォルダ内で完結",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5121.PNG",
            "headline": "分類ルールを\n自由に設定",
            "sub": "曜日・時間帯・期間・動画の長さでフィルタリング",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
    "zh-Hans": [
        {
            "file": "IMG_5128.PNG",
            "headline": "自动整理\n你的视频",
            "sub": "智能文件夹按星期、时间、日期自动分类录像",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5129.PNG",
            "headline": "按文件夹\n浏览视频",
            "sub": "在每个分类目录中播放、置顶和管理视频",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5130.PNG",
            "headline": "自定义\n分类规则",
            "sub": "按星期、时间段、日期范围和时长进行筛选",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
    "zh-Hant": [
        {
            "file": "IMG_5125.PNG",
            "headline": "自動整理\n你的影片",
            "sub": "智慧資料夾按星期、時間、日期自動分類錄影",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5126.PNG",
            "headline": "按資料夾\n瀏覽影片",
            "sub": "在每個分類目錄中播放、置頂和管理影片",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5127.PNG",
            "headline": "自訂\n分類規則",
            "sub": "按星期、時段、日期範圍和時長進行篩選",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
    "es": [
        {
            "file": "IMG_5122.PNG",
            "headline": "Organiza tus\nVideos Automáticamente",
            "sub": "Carpetas inteligentes clasifican tus grabaciones por día, hora y fecha",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5123.PNG",
            "headline": "Explora Videos\npor Carpeta",
            "sub": "Reproduce, fija y gestiona videos dentro de cada directorio",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5124.PNG",
            "headline": "Define tus Reglas\nde Clasificación",
            "sub": "Filtra por día de la semana, horario, rango de fechas y duración",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
    "ko": [
        {
            "file": "IMG_5131.PNG",
            "headline": "동영상을\n자동으로 정리",
            "sub": "스마트 폴더가 요일, 시간, 날짜별로 녹화를 자동 분류",
            "bg": SLOT_BG[0],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5132.PNG",
            "headline": "폴더별로\n동영상 탐색",
            "sub": "분류된 디렉토리에서 재생, 고정, 관리까지 한 번에",
            "bg": SLOT_BG[1],
            "text_color": WHITE,
        },
        {
            "file": "IMG_5133.PNG",
            "headline": "나만의\n분류 규칙 설정",
            "sub": "요일, 시간대, 날짜 범위, 영상 길이로 필터링",
            "bg": SLOT_BG[2],
            "text_color": WHITE,
        },
    ],
}

RAW_DIR_FALLBACK = "en"


def is_cjk_char(ch):
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
        (0xFE30 <= cp <= 0xFE4F) or
        (0xAC00 <= cp <= 0xD7AF) or
        (0x1100 <= cp <= 0x11FF) or
        (0x3130 <= cp <= 0x318F)
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
    return target_width / target_height > 0.6


def generate_screenshot(ss_config, target_width, target_height, raw_dir, lang="en"):
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
        side_padding = int(target_width * 0.18)
        bottom_padding = int(target_height * 0.01)
    else:
        header_height = int(target_height * 0.28)
        side_padding = int(target_width * 0.06)
        bottom_padding = int(target_height * 0.02)

    screenshot_area_height = target_height - header_height

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

    avail_h = screenshot_area_height - bottom_padding

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
        screenshot = add_rounded_corners(screenshot, corner_radius)
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
    print("=" * 60)
    print("  VideoSorter App Store Screenshot Generator")
    print("=" * 60)
    print(f"\n  CJK Fonts: {CJK_FONT_PATHS}")
    print(f"  Latin Font: {LATIN_FONT_PATH}")
    print()

    for lang, screenshots in SCREENSHOTS.items():
        lang_raw_dir = os.path.join(RAW_DIR, lang)
        if not os.path.exists(lang_raw_dir):
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
    print("     - {lang}/6.5/    → iPhone 6.5\" Display (required)")
    print("     - {lang}/ipad13/ → iPad 13\" Display (required)")


if __name__ == "__main__":
    main()
