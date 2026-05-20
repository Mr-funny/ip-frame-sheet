#!/usr/bin/env python3
"""Sprite-sheet-first pipeline: generate sheet, crop frames, assemble video."""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = SKILL_DIR / "assets" / "reference-character.png"


def trim_to_subject(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    bbox = rgba.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def make_canvas(frame_size: int) -> Image.Image:
    canvas = Image.new("RGBA", (frame_size, frame_size), (248, 250, 252, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, int(frame_size * 0.72), frame_size, frame_size), fill=(91, 64, 45, 255))
    draw.rectangle((0, int(frame_size * 0.72), frame_size, int(frame_size * 0.75)), fill=(126, 88, 55, 255))

    mx0, my0 = int(frame_size * 0.05), int(frame_size * 0.24)
    mx1, my1 = int(frame_size * 0.34), int(frame_size * 0.66)
    draw.rounded_rectangle((mx0, my0, mx1, my1), radius=12, fill=(28, 31, 36, 255))
    draw.rounded_rectangle((mx0 + 10, my0 + 10, mx1 - 10, my1 - 10), radius=8, fill=(11, 18, 27, 255))
    for i in range(8):
        y = my0 + 28 + i * 23
        color = [(75, 215, 125, 255), (90, 180, 255, 255), (240, 190, 80, 255)][i % 3]
        draw.line((mx0 + 24, y, mx0 + 52 + (i % 4) * 22, y), fill=color, width=3)
    draw.rectangle((int(frame_size * 0.17), int(frame_size * 0.66), int(frame_size * 0.22), int(frame_size * 0.72)), fill=(45, 48, 54, 255))
    draw.rounded_rectangle((int(frame_size * 0.11), int(frame_size * 0.71), int(frame_size * 0.29), int(frame_size * 0.74)), radius=6, fill=(42, 44, 49, 255))

    kx0, ky0 = int(frame_size * 0.38), int(frame_size * 0.76)
    draw.rounded_rectangle((kx0, ky0, int(frame_size * 0.84), int(frame_size * 0.88)), radius=10, fill=(34, 36, 41, 255))
    for row in range(3):
        for col in range(9):
            x = kx0 + 16 + col * 29 + (row % 2) * 8
            y = ky0 + 12 + row * 24
            draw.rounded_rectangle((x, y, x + 18, y + 12), radius=3, fill=(82, 86, 96, 255))
    return canvas


def render_cell(subject: Image.Image, index: int, count: int, frame_size: int) -> Image.Image:
    t = index / count
    pulse = (math.sin(t * math.tau * 2) + 1) / 2
    breathe = math.sin(t * math.tau * 2)
    slow = math.sin(t * math.tau)
    fast = math.sin(t * math.tau * 8)
    canvas = make_canvas(frame_size)
    draw = ImageDraw.Draw(canvas)

    def s(value: float) -> int:
        return int(value * frame_size / 768)

    def pt(x: float, y: float, dx: float = 0, dy: float = 0) -> tuple[int, int]:
        return (s(x + dx), s(y + dy))

    # The default character is redrawn as separate parts so the video does not
    # look like a single rigid sticker moving across the screen.
    base_x = 325 + slow * 10
    base_y = 50 + breathe * 5
    head_y = base_y + math.sin(t * math.tau * 3 + 0.6) * 7
    arm_swing = math.sin(t * math.tau * 4 + 0.8) * 14
    tail_swing = math.sin(t * math.tau * 2 + 1.4) * 22
    wing_lift = math.sin(t * math.tau * 3 + 2.2) * 10
    tap_l = math.sin(t * math.tau * 12) * 12
    tap_r = math.sin(t * math.tau * 12 + math.pi) * 12

    # Tail and wing sit behind the body and move independently.
    draw.line([pt(base_x + 88, base_y + 300), pt(base_x + 150 + tail_swing, base_y + 318), pt(base_x + 185 + tail_swing, base_y + 286)], fill=(18, 18, 22, 255), width=s(15))
    draw.polygon([pt(base_x + 168 + tail_swing, base_y + 303), pt(base_x + 218 + tail_swing, base_y + 315), pt(base_x + 178 + tail_swing, base_y + 280)], fill=(20, 20, 25, 255), outline=(160, 0, 30, 255))
    draw.polygon([pt(base_x + 74, base_y + 142), pt(base_x + 168, base_y + 112 + wing_lift), pt(base_x + 124, base_y + 170), pt(base_x + 188, base_y + 168 + wing_lift), pt(base_x + 114, base_y + 212)], fill=(235, 235, 235, 255), outline=(45, 45, 45, 255))
    for offset in (96, 118, 141, 164):
        draw.line([pt(base_x + 86, base_y + 152), pt(base_x + offset, base_y + 206 + wing_lift * 0.4)], fill=(85, 85, 85, 255), width=s(2))

    # Body breathing changes width/height instead of moving the entire asset.
    body_w = 112 + breathe * 7
    body_h = 154 - breathe * 6
    body_top = base_y + 138
    body_box = (s(base_x - body_w / 2), s(body_top), s(base_x + body_w / 2), s(body_top + body_h))
    draw.ellipse(body_box, fill=(20, 23, 28, 255), outline=(60, 60, 65, 255), width=s(3))
    draw.line([pt(base_x - 20, base_y + 124), pt(base_x - 18, body_top + 12)], fill=(18, 20, 24, 255), width=s(18))
    draw.line([pt(base_x - 18, body_top + 32), pt(base_x - 2, body_top + 87)], fill=(62, 66, 75, 255), width=s(4))
    draw.line([pt(base_x + 20, body_top + 30), pt(base_x + 45, body_top + 82)], fill=(62, 66, 75, 255), width=s(4))

    # Legs flex subtly with the typing rhythm.
    for side, tap in [(-1, tap_l * 0.25), (1, tap_r * 0.25)]:
        hip_x = base_x + side * 38
        draw.polygon([pt(hip_x, base_y + 285), pt(hip_x + side * 45, base_y + 354 + tap), pt(hip_x + side * 10, base_y + 342), pt(hip_x + side * 20, base_y + 395 + tap), pt(hip_x + side * -10, base_y + 330)], fill=(18, 20, 24, 255), outline=(55, 55, 60, 255))
        draw.polygon([pt(hip_x + side * 40, base_y + 354 + tap), pt(hip_x + side * 82, base_y + 372 + tap), pt(hip_x + side * 45, base_y + 376 + tap)], fill=(225, 225, 232, 255), outline=(160, 0, 30, 255))
        draw.polygon([pt(hip_x + side * 12, base_y + 392 + tap), pt(hip_x + side * 2, base_y + 430 + tap), pt(hip_x + side * 35, base_y + 402 + tap)], fill=(225, 225, 232, 255), outline=(160, 0, 30, 255))

    # Red armor bands track body/leg movement.
    for x, y, w in [(-54, 272, 34), (20, 270, 34), (-82, 332, 38), (70, 330, 38)]:
        draw.rounded_rectangle((s(base_x + x), s(base_y + y), s(base_x + x + w), s(base_y + y + 16)), radius=s(5), fill=(120, 0, 26, 255), outline=(230, 30, 55, 255), width=s(2))

    # Mechanical cannon arm rocks and the barrel compresses slightly.
    arm_x = base_x + 42 + arm_swing
    arm_y = base_y + 150 + math.cos(t * math.tau * 4) * 5
    draw.line([pt(base_x + 40, body_top + 55), pt(arm_x + 60, arm_y + 25)], fill=(25, 25, 30, 255), width=s(18))
    draw.ellipse((s(arm_x), s(arm_y), s(arm_x + 118), s(arm_y + 82)), fill=(184, 184, 184, 255), outline=(35, 35, 35, 255), width=s(3))
    draw.rounded_rectangle((s(arm_x + 22), s(arm_y + 16), s(arm_x + 105), s(arm_y + 68)), radius=s(12), fill=(210, 210, 210, 255), outline=(50, 50, 50, 255), width=s(2))
    barrel = 48 + math.sin(t * math.tau * 4) * 4
    draw.rectangle((s(arm_x + 86), s(arm_y + 25), s(arm_x + 86 + barrel), s(arm_y + 58)), fill=(154, 154, 154, 255), outline=(30, 30, 30, 255), width=s(3))
    for x in range(94, 132, 8):
        draw.line([pt(arm_x + x, arm_y + 28), pt(arm_x + x, arm_y + 56)], fill=(60, 60, 60, 255), width=s(2))

    # Left claw reaches toward the keyboard with finger taps.
    claw_x = base_x - 82 + math.sin(t * math.tau * 8) * 8
    claw_y = base_y + 285 + tap_l
    draw.line([pt(base_x - 48, body_top + 80), pt(claw_x, claw_y)], fill=(24, 25, 31, 255), width=s(16))
    for i, spread in enumerate([-34, 0, 34]):
        draw.polygon([pt(claw_x, claw_y), pt(claw_x - 45, claw_y + spread * 0.25 + i * 7), pt(claw_x - 12, claw_y + spread * 0.45 + 18)], fill=(220, 230, 255, 255), outline=(20, 25, 140, 255))

    # Head, fins, flame, visor, and eye each have their own motion.
    head_x = base_x - 26 + math.sin(t * math.tau * 3) * 5
    draw.ellipse((s(head_x - 70), s(head_y + 25), s(head_x + 34), s(head_y + 126)), fill=(22, 23, 28, 255), outline=(55, 55, 60, 255), width=s(3))
    fin_wobble = math.sin(t * math.tau * 3 + 1.0) * 6
    draw.polygon([pt(head_x - 56, head_y + 50), pt(head_x - 58 + fin_wobble, head_y - 6), pt(head_x - 28, head_y + 12), pt(head_x - 20, head_y + 80)], fill=(245, 245, 245, 255), outline=(55, 0, 35, 255))
    draw.polygon([pt(head_x + 2, head_y + 46), pt(head_x + 70 + fin_wobble, head_y - 4), pt(head_x + 56, head_y + 64), pt(head_x + 12, head_y + 82)], fill=(245, 245, 245, 255), outline=(55, 0, 35, 255))
    for i, flame_x in enumerate([-28, -10, 8, 26, 42]):
        flame_h = 52 + math.sin(t * math.tau * 6 + i) * 16
        color = [(255, 36, 0, 255), (255, 130, 0, 255), (255, 228, 0, 255)][i % 3]
        draw.polygon([pt(head_x + flame_x, head_y + 42), pt(head_x + flame_x + 9, head_y + 42 - flame_h), pt(head_x + flame_x + 22, head_y + 52)], fill=color, outline=(120, 0, 0, 255))

    glow_layer = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    eye_x, eye_y = pt(head_x - 42, head_y + 72)
    for radius, alpha in [(42, 45 + int(30 * pulse)), (28, 85), (18, 140)]:
        glow_draw.ellipse((eye_x - s(radius), eye_y - s(radius), eye_x + s(radius), eye_y + s(radius)), fill=(0, 190, 255, alpha))
    canvas.alpha_composite(glow_layer.filter(ImageFilter.GaussianBlur(s(3))))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((eye_x - s(22), eye_y - s(22), eye_x + s(22), eye_y + s(22)), fill=(35, 185, 255, 255), outline=(255, 255, 255, 255), width=s(3))
    draw.ellipse((eye_x - s(10), eye_y - s(14), eye_x + s(5), eye_y + s(3)), fill=(155, 235, 255, 255))
    draw.ellipse((eye_x - s(13), eye_y - s(17), eye_x - s(4), eye_y - s(8)), fill=(255, 255, 255, 230))
    draw.polygon([pt(head_x - 20, head_y + 74), pt(head_x + 35, head_y + 58), pt(head_x + 24, head_y + 90), pt(head_x - 18, head_y + 98)], fill=(180, 0, 32, 255), outline=(40, 40, 45, 255))

    # Right hand/cannon-side tap cue on keyboard, separate from the arm.
    right_hand_y = s(585 + tap_r)
    draw.ellipse((s(520), right_hand_y, s(590), right_hand_y + s(28)), fill=(18, 21, 27, 235), outline=(180, 20, 45, 255), width=s(3))
    if index % 2 == 0:
        draw.rectangle((int(frame_size * 0.275), int(frame_size * 0.385), int(frame_size * 0.282), int(frame_size * 0.43)), fill=(120, 230, 255, 255))
    return canvas.convert("RGB")


def generate_sprite_sheet(reference: Path, rows: int, cols: int, frame_size: int, out: Path) -> None:
    subject = trim_to_subject(Image.open(reference))
    count = rows * cols
    sheet = Image.new("RGB", (cols * frame_size, rows * frame_size), "white")
    for i in range(count):
        cell = render_cell(subject, i, count, frame_size)
        sheet.paste(cell, ((i % cols) * frame_size, (i // cols) * frame_size))
    sheet.save(out)


def crop_sprite_sheet(sprite_sheet: Path, rows: int, cols: int, frames_dir: Path) -> list[Path]:
    sheet = Image.open(sprite_sheet).convert("RGB")
    if sheet.width % cols or sheet.height % rows:
        raise SystemExit(f"Sprite sheet dimensions {sheet.size} are not divisible by {cols}x{rows}")
    cell_w = sheet.width // cols
    cell_h = sheet.height // rows
    frames_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for old in frames_dir.glob("frame_*.png"):
        old.unlink()
    for i in range(rows * cols):
        left = (i % cols) * cell_w
        top = (i // cols) * cell_h
        frame = sheet.crop((left, top, left + cell_w, top + cell_h))
        path = frames_dir / f"frame_{i:03d}.png"
        frame.save(path)
        paths.append(path)
    return paths


def encode_outputs(frames_dir: Path, frame_count: int, fps: int, mp4_out: Path, gif_out: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required to encode MP4")
    frames = [Image.open(frames_dir / f"frame_{i:03d}.png").convert("RGB") for i in range(frame_count)]
    frames[0].save(gif_out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%03d.png"),
        "-frames:v",
        str(frame_count),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(mp4_out),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate/use sprite sheet, crop frames, assemble a one-second video.")
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE), help="Reference character image for generated sprite sheet.")
    parser.add_argument("--sprite-sheet", help="Existing sprite sheet to crop. If omitted, one is generated from --reference.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    parser.add_argument("--action", default="typing", help="Action label for metadata/logging.")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second.")
    parser.add_argument("--seconds", type=float, default=1.0, help="Duration in seconds.")
    parser.add_argument("--frame-size", type=int, default=768, help="Cell size for generated sprite sheet.")
    parser.add_argument("--rows", type=int, default=4, help="Sprite sheet rows.")
    parser.add_argument("--cols", type=int, default=6, help="Sprite sheet columns.")
    args = parser.parse_args()

    expected = args.rows * args.cols
    frame_count = int(round(args.fps * args.seconds))
    if frame_count != expected:
        raise SystemExit(f"fps * seconds must equal rows * cols: got {frame_count}, expected {expected}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sprite_sheet = outdir / "sprite_sheet.png"
    if args.sprite_sheet:
        source_sheet = Path(args.sprite_sheet)
        if not source_sheet.exists():
            raise SystemExit(f"Sprite sheet not found: {source_sheet}")
        Image.open(source_sheet).convert("RGB").save(sprite_sheet)
        source_text = f"existing_sprite_sheet={source_sheet}"
    else:
        reference = Path(args.reference)
        if not reference.exists():
            raise SystemExit(f"Reference image not found: {reference}")
        generate_sprite_sheet(reference, args.rows, args.cols, args.frame_size, sprite_sheet)
        source_text = f"reference={reference}"

    frames_dir = outdir / "cropped_frames"
    frame_paths = crop_sprite_sheet(sprite_sheet, args.rows, args.cols, frames_dir)
    encode_outputs(frames_dir, frame_count, args.fps, outdir / "one_second_animation.mp4", outdir / "one_second_animation.gif")

    (outdir / "metadata.txt").write_text(
        "\n".join(
            [
                source_text,
                f"action={args.action}",
                f"sprite_sheet={sprite_sheet}",
                f"cropped_frames_dir={frames_dir}",
                f"fps={args.fps}",
                f"seconds={args.seconds}",
                f"frames={len(frame_paths)}",
                "pipeline=sprite_sheet -> crop_frames -> assemble_video",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(sprite_sheet)
    print(frames_dir)
    print(outdir / "one_second_animation.mp4")
    print(outdir / "one_second_animation.gif")


if __name__ == "__main__":
    main()
