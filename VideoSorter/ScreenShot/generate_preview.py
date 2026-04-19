#!/usr/bin/env python3
"""
MManager App Preview Video Generator (Memory-efficient)
========================================================
Streams frames directly to ffmpeg to avoid memory issues.
"""

import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")

FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
LATIN_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FPS = 30
SLIDE_HOLD = 3.0        # seconds per slide (static hold)
TRANSITION = 0.5         # seconds for crossfade
INTRO_HOLD = 2.0
OUTRO_HOLD = 2.0
FADE_DUR = 0.4           # fade in/out from black

THEME_COLOR = (79, 121, 113)
THEME_DARK = (61, 94, 88)
WHITE = (255, 255, 255)

PREVIEW_SIZES = {
    "6.9": (1320, 2868),
    "6.5": (1284, 2778),
    "5.5": (1080, 1920),
}

SLIDES = [
    "01_calendar.png",
    "02_scan.png",
    "03_input.png",
    "04_statistics.png",
    "05_widget.png",
    "06_scanlist.png",
]


def is_cjk(ch):
    cp = ord(ch)
    return ((0x3000 <= cp <= 0x303F) or (0x3040 <= cp <= 0x309F) or
            (0x30A0 <= cp <= 0x30FF) or (0x4E00 <= cp <= 0x9FFF) or
            (0xFF00 <= cp <= 0xFFEF) or (0x3400 <= cp <= 0x4DBF) or
            (0x2E80 <= cp <= 0x2FDF) or (0xF900 <= cp <= 0xFAFF))


def draw_text_c(draw, cx, y, text, cjk_f, lat_f, fill):
    tw = sum(draw.textbbox((0,0), ch, font=(cjk_f if is_cjk(ch) else lat_f))[2] -
             draw.textbbox((0,0), ch, font=(cjk_f if is_cjk(ch) else lat_f))[0] for ch in text)
    x = cx - tw // 2
    for ch in text:
        if ch == ' ':
            x += draw.textbbox((0,0), ' ', font=lat_f)[2]
            continue
        f = cjk_f if is_cjk(ch) else lat_f
        draw.text((x, y), ch, fill=fill, font=f)
        x += draw.textbbox((0,0), ch, font=f)[2] - draw.textbbox((0,0), ch, font=f)[0]


def make_gradient(w, h, c1, c2):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / h
        arr[y, :] = [int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)]
    return arr


def make_intro(w, h):
    bg = Image.fromarray(make_gradient(w, h, THEME_COLOR, THEME_DARK))
    draw = ImageDraw.Draw(bg)
    ts = int(w * 0.09)
    ss = int(w * 0.038)
    tc = ImageFont.truetype(FONT_PATH, ts)
    tl = ImageFont.truetype(LATIN_FONT_PATH, ts)
    sc = ImageFont.truetype(FONT_PATH, ss)
    sl = ImageFont.truetype(LATIN_FONT_PATH, ss)

    # App icon
    icon_sz = int(w * 0.2)
    ix = (w - icon_sz) // 2
    iy = int(h * 0.3)
    icon_path = os.path.join(SCRIPT_DIR, "..", "MManager", "Assets.xcassets",
                              "AppIcon.appiconset", "_084c8976-001e-492d-be8d-411e014fd76e.jpeg")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).resize((icon_sz, icon_sz), Image.LANCZOS)
        mask = Image.new("L", (icon_sz, icon_sz), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0,0),(icon_sz-1,icon_sz-1)], radius=int(icon_sz*0.22), fill=255)
        bg.paste(icon, (ix, iy), mask)

    ty = iy + icon_sz + int(h * 0.035)
    draw_text_c(draw, w//2, ty, "家計簿", tc, tl, WHITE)
    draw_text_c(draw, w//2, ty + int(ts*1.3), "支出管理アプリ", tc, tl, WHITE)
    draw_text_c(draw, w//2, ty + int(ts*1.3)*2 + int(h*0.025),
                "レシート撮影で簡単家計管理", sc, sl, (230, 240, 242))
    return np.array(bg)


def make_outro(w, h):
    bg = Image.fromarray(make_gradient(w, h, THEME_COLOR, THEME_DARK))
    draw = ImageDraw.Draw(bg)
    ts = int(w * 0.075)
    ss = int(w * 0.038)
    tc = ImageFont.truetype(FONT_PATH, ts)
    tl = ImageFont.truetype(LATIN_FONT_PATH, ts)
    sc = ImageFont.truetype(FONT_PATH, ss)
    sl = ImageFont.truetype(LATIN_FONT_PATH, ss)

    cy = int(h * 0.38)
    draw_text_c(draw, w//2, cy, "今すぐ無料で", tc, tl, WHITE)
    draw_text_c(draw, w//2, cy + int(ts*1.4), "家計管理を始めよう", tc, tl, WHITE)
    return np.array(bg)


def ease(t):
    return t * t * (3 - 2 * t)


def blend(a, b, t):
    return ((1 - t) * a.astype(np.float32) + t * b.astype(np.float32)).astype(np.uint8)


def generate_video(w, h, size_name):
    export_dir = os.path.join(EXPORT_DIR, size_name)
    preview_dir = os.path.join(EXPORT_DIR, "previews")
    os.makedirs(preview_dir, exist_ok=True)
    output_path = os.path.join(preview_dir, f"preview_{size_name}.mp4")

    # Load slides (only 6, manageable)
    slides = []
    for sf in SLIDES:
        p = os.path.join(export_dir, sf)
        if os.path.exists(p):
            img = Image.open(p).convert("RGB")
            if img.size != (w, h):
                img = img.resize((w, h), Image.LANCZOS)
            slides.append(np.array(img))

    if not slides:
        print(f"  ✗ No slides for {size_name}")
        return

    intro = make_intro(w, h)
    outro = make_outro(w, h)
    black = np.zeros((h, w, 3), dtype=np.uint8)

    # Start ffmpeg pipe
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{w}x{h}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    def write_frame(frame):
        proc.stdin.write(frame.tobytes())

    n_fade = int(FADE_DUR * FPS)
    n_hold_intro = int(INTRO_HOLD * FPS)
    n_hold_slide = int(SLIDE_HOLD * FPS)
    n_trans = int(TRANSITION * FPS)
    n_hold_outro = int(OUTRO_HOLD * FPS)
    total_frames = 0

    # 1) Fade in from black -> intro
    for i in range(n_fade):
        write_frame(blend(black, intro, ease(i / n_fade)))
        total_frames += 1

    # 2) Hold intro
    for _ in range(n_hold_intro):
        write_frame(intro)
        total_frames += 1

    # 3) Crossfade intro -> first slide
    for i in range(n_trans):
        write_frame(blend(intro, slides[0], ease(i / n_trans)))
        total_frames += 1

    # 4) Slides with crossfade transitions
    for idx, slide in enumerate(slides):
        for _ in range(n_hold_slide):
            write_frame(slide)
            total_frames += 1
        if idx < len(slides) - 1:
            nxt = slides[idx + 1]
            for i in range(n_trans):
                write_frame(blend(slide, nxt, ease(i / n_trans)))
                total_frames += 1

    # 5) Crossfade last slide -> outro
    for i in range(n_trans):
        write_frame(blend(slides[-1], outro, ease(i / n_trans)))
        total_frames += 1

    # 6) Hold outro
    for _ in range(n_hold_outro):
        write_frame(outro)
        total_frames += 1

    # 7) Fade out to black
    for i in range(n_fade):
        write_frame(blend(outro, black, ease(i / n_fade)))
        total_frames += 1

    proc.stdin.close()
    proc.wait()

    duration = total_frames / FPS
    if proc.returncode == 0:
        mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ✓ {os.path.basename(output_path)}: {duration:.1f}s, {mb:.1f}MB, {total_frames} frames")
    else:
        err = proc.stderr.read().decode()[-300:]
        print(f"  ✗ Error: {err}")

    # Free memory
    del slides
    return output_path


def main():
    print("=" * 55)
    print("  MManager App Preview Video Generator")
    print("=" * 55)

    for size_name, (w, h) in PREVIEW_SIZES.items():
        print(f"\n--- iPhone {size_name}\" ({w}x{h}) ---")
        generate_video(w, h, size_name)

    print(f"\n✅ All previews in: {os.path.join(EXPORT_DIR, 'previews')}/")


if __name__ == "__main__":
    main()
