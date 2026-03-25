#!/usr/bin/env python3
"""
家計簿 App Preview Video Generator
====================================
Combines screen recordings + screenshot slides into an App Store preview.
Uses ffmpeg for efficient processing.

Input:
  raw/widget.mov            - ホーム画面ウィジェット操作の録画
  raw/screenlock widget.mov - ロック画面ウィジェット操作の録画
  exports/{size}/            - generate.py で作成したスクリーンショット

Output:
  exports/previews/preview_{size}.mp4

App Store 要件:
  - 15〜30秒
  - iPhone 6.9": 1320x2868 / 6.5": 1284x2778 / 5.5": 1080x1920
"""

import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")

# Font
FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
LATIN_FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

THEME_COLOR = (79, 121, 113)
THEME_DARK = (61, 94, 88)
WHITE = (255, 255, 255)

PREVIEW_SIZES = {
    "5.5": (886, 1920),
    "ipad": (1200, 1600),
}

# Preview構成：各クリップの秒数
# 合計 ~28秒（App Store は 15-30秒）
# video の speed は再生速度倍率（2.0 = 2倍速）
STRUCTURE = [
    # (type, source, duration, headline, sub, speed)
    ("title", None, 2.0, "家計簿", "レシート撮影で簡単家計管理", None),
    ("slide", "01_calendar.png", 2.0, "カレンダーで\n支出を管理", None, None),
    ("slide", "02_scan.png", 2.0, "レシートを撮るだけ\n自動で読取", None, None),
    ("slide", "03_5006.png", 2.0, "ワンタップで\n記録完了", None, None),
    ("slide", "04_statistics.png", 2.0, "グラフで\n支出を分析", None, None),
    ("video", "widget.mov", None, "ウィジェットで\nすぐアクセス", None, 2.5),
    ("video", "screenlock widget.mov", None, "ロック画面から\nワンタップ起動", None, 2.5),
    ("slide", "08_5009.png", 2.0, "Excel / CSV\nエクスポート", None, None),
    ("ending", None, 2.0, "今すぐ無料で\n家計管理を始めよう", None, None),
]


def is_cjk(ch):
    cp = ord(ch)
    return ((0x3000 <= cp <= 0x303F) or (0x3040 <= cp <= 0x309F) or
            (0x30A0 <= cp <= 0x30FF) or (0x4E00 <= cp <= 0x9FFF) or
            (0xFF00 <= cp <= 0xFFEF))


def draw_text_centered(draw, cx, y, text, cjk_f, lat_f, fill):
    """Draw centered text with CJK/Latin font fallback."""
    tw = 0
    for ch in text:
        f = cjk_f if is_cjk(ch) else lat_f
        bb = draw.textbbox((0, 0), ch, font=f)
        tw += bb[2] - bb[0]
    x = cx - tw // 2
    for ch in text:
        if ch == ' ':
            x += draw.textbbox((0, 0), ' ', font=lat_f)[2]
            continue
        f = cjk_f if is_cjk(ch) else lat_f
        draw.text((x, y), ch, fill=fill, font=f)
        bb = draw.textbbox((0, 0), ch, font=f)
        x += bb[2] - bb[0]


def make_text_frame(w, h, headline, sub=None):
    """Create a gradient frame with centered text."""
    img = Image.new("RGB", (w, h))
    pixels = img.load()
    for y in range(h):
        t = y / h
        r = int(THEME_COLOR[0] + (THEME_DARK[0] - THEME_COLOR[0]) * t)
        g = int(THEME_COLOR[1] + (THEME_DARK[1] - THEME_COLOR[1]) * t)
        b = int(THEME_COLOR[2] + (THEME_DARK[2] - THEME_COLOR[2]) * t)
        for x in range(w):
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)
    ts = int(w * 0.08)
    ss = int(w * 0.038)
    tc = ImageFont.truetype(FONT_PATH, ts)
    tl = ImageFont.truetype(LATIN_FONT_PATH, ts)
    sc = ImageFont.truetype(FONT_PATH, ss)
    sl = ImageFont.truetype(LATIN_FONT_PATH, ss)

    # App icon for title/ending
    icon_path = os.path.join(SCRIPT_DIR, "..", "MManager", "Assets.xcassets",
                             "AppIcon.appiconset", "_084c8976-001e-492d-be8d-411e014fd76e.jpeg")
    if os.path.exists(icon_path) and "家計簿" in headline and "\n" not in headline:
        icon_sz = int(w * 0.2)
        icon = Image.open(icon_path).resize((icon_sz, icon_sz), Image.LANCZOS)
        mask = Image.new("L", (icon_sz, icon_sz), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (icon_sz-1, icon_sz-1)],
                                                radius=int(icon_sz*0.22), fill=255)
        ix = (w - icon_sz) // 2
        iy = int(h * 0.3)
        img.paste(icon, (ix, iy), mask)
        ty = iy + icon_sz + int(h * 0.035)
    else:
        lines = headline.split("\n")
        total_h = len(lines) * int(ts * 1.35)
        ty = (h - total_h) // 2 - int(h * 0.05)

    for i, line in enumerate(headline.split("\n")):
        draw_text_centered(draw, w // 2, ty + i * int(ts * 1.35), line, tc, tl, WHITE)

    if sub:
        sub_y = ty + len(headline.split("\n")) * int(ts * 1.35) + int(h * 0.025)
        draw_text_centered(draw, w // 2, sub_y, sub, sc, sl, (230, 240, 242))

    return img


def generate_preview(size_name, w, h):
    """Generate a preview video for the given size."""
    preview_dir = os.path.join(EXPORT_DIR, "previews")
    os.makedirs(preview_dir, exist_ok=True)
    output = os.path.join(preview_dir, f"preview_{size_name}.mp4")
    # iPad preview は ipad13 のスクリーンショットを使う
    slide_size = "ipad13" if size_name == "ipad" else size_name
    export_size_dir = os.path.join(EXPORT_DIR, slide_size)

    # 1. Generate intermediate clips
    clips = []
    tmp_dir = os.path.join(preview_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    for idx, (ctype, source, dur, headline, sub, speed) in enumerate(STRUCTURE):
        clip_path = os.path.join(tmp_dir, f"clip_{idx:02d}.mp4")

        if ctype in ("title", "ending"):
            # Static text frame → video
            frame = make_text_frame(w, h, headline, sub)
            frame_path = os.path.join(tmp_dir, f"frame_{idx:02d}.png")
            frame.save(frame_path)
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", frame_path,
                "-c:v", "libx264", "-t", str(dur), "-pix_fmt", "yuv420p",
                "-vf", f"scale={w}:{h}", "-r", "30",
                clip_path
            ], capture_output=True)
            clips.append(clip_path)

        elif ctype == "slide":
            # Screenshot slide → video (保持比例居中、背景色填充)
            slide_path = os.path.join(export_size_dir, source)
            if not os.path.exists(slide_path):
                print(f"  ⚠ Missing slide: {source}")
                continue
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                  f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=3D5E58")
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", slide_path,
                "-c:v", "libx264", "-t", str(dur), "-pix_fmt", "yuv420p",
                "-vf", vf, "-r", "30",
                clip_path
            ], capture_output=True)
            clips.append(clip_path)

        elif ctype == "video":
            # Screen recording → 加速 + scale + pad + headline overlay
            video_path = os.path.join(RAW_DIR, source)
            if not os.path.exists(video_path):
                print(f"  ⚠ Missing video: {source}")
                continue

            # Create headline overlay image
            overlay = make_text_frame(w, h, headline, sub)
            overlay_path = os.path.join(tmp_dir, f"overlay_{idx:02d}.png")
            overlay_rgba = overlay.convert("RGBA")
            px = overlay_rgba.load()
            header_h = int(h * 0.25)
            for y in range(header_h, h):
                for x in range(w):
                    px[x, y] = (0, 0, 0, 0)
            overlay_rgba.save(overlay_path)

            # 加速 + scale to fit lower 75% + pad + overlay
            vid_area_h = h - header_h
            spd = speed or 1.0
            pts_filter = f"setpts={1.0/spd}*PTS," if spd != 1.0 else ""
            vid_scale = f"scale=-1:{vid_area_h}:force_original_aspect_ratio=decrease"
            vid_pad = f"pad={w}:{h}:(ow-iw)/2:{header_h}:color=3D5E58"

            subprocess.run([
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", overlay_path,
                "-filter_complex",
                f"[0:v]{pts_filter}{vid_scale},{vid_pad}[bg];[bg][1:v]overlay=0:0[out]",
                "-map", "[out]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-an",
                clip_path
            ], capture_output=True)
            clips.append(clip_path)

    if not clips:
        print(f"  ✗ No clips generated for {size_name}")
        return

    # 2. Concatenate clips
    concat_path = os.path.join(tmp_dir, "concat.txt")
    with open(concat_path, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")

    concat_tmp = os.path.join(tmp_dir, "concat_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-crf", "20", concat_tmp
    ], capture_output=True)

    # 3. Add silent AAC audio track (App Store requires audio)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", concat_tmp,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart",
        output
    ], capture_output=True)

    # 4. Cleanup tmp
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    os.rmdir(tmp_dir)

    if os.path.exists(output):
        mb = os.path.getsize(output) / (1024 * 1024)
        dur_s = float(subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", output],
            capture_output=True, text=True
        ).stdout.strip() or "0")
        print(f"  ✓ preview_{size_name}.mp4: {dur_s:.1f}s, {mb:.1f}MB")
    else:
        print(f"  ✗ Failed to generate preview_{size_name}.mp4")


def main():
    print("=" * 55)
    print("  家計簿 App Preview Video Generator")
    print("=" * 55)

    for size_name, (w, h) in PREVIEW_SIZES.items():
        print(f"\n--- iPhone {size_name}\" ({w}x{h}) ---")
        generate_preview(size_name, w, h)

    print(f"\n✅ Previews saved to: {os.path.join(EXPORT_DIR, 'previews')}/")


if __name__ == "__main__":
    main()
