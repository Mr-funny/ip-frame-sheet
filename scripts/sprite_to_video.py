#!/usr/bin/env python3
"""Crop a 4x6 sprite sheet and assemble the cropped frames into video."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from PIL import Image


def crop_sprite_sheet(sprite_sheet: Path, rows: int, cols: int, frames_dir: Path) -> list[Path]:
    sheet = Image.open(sprite_sheet).convert("RGB")
    if sheet.width % cols or sheet.height % rows:
        raise SystemExit(f"Sprite sheet dimensions {sheet.size} are not divisible by {cols}x{rows}")

    cell_w = sheet.width // cols
    cell_h = sheet.height // rows
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame_*.png"):
        old.unlink()

    frames: list[Path] = []
    for i in range(rows * cols):
        left = (i % cols) * cell_w
        top = (i // cols) * cell_h
        frame = sheet.crop((left, top, left + cell_w, top + cell_h))
        path = frames_dir / f"frame_{i:03d}.png"
        frame.save(path)
        frames.append(path)
    return frames


def encode_video(frames_dir: Path, frame_count: int, fps: int, mp4_out: Path, gif_out: Path) -> None:
    frames = [Image.open(frames_dir / f"frame_{i:03d}.png").convert("RGB") for i in range(frame_count)]
    frames[0].save(gif_out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required to encode MP4")
    subprocess.run(
        [
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
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a generated sprite sheet to a one-second video.")
    parser.add_argument("--sprite-sheet", required=True, help="GPT Image generated 4x6 sprite sheet.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    parser.add_argument("--rows", type=int, default=4, help="Sprite sheet rows.")
    parser.add_argument("--cols", type=int, default=6, help="Sprite sheet columns.")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second.")
    parser.add_argument("--seconds", type=float, default=1.0, help="Output duration in seconds.")
    args = parser.parse_args()

    sprite_sheet = Path(args.sprite_sheet)
    if not sprite_sheet.exists():
        raise SystemExit(f"Sprite sheet not found: {sprite_sheet}")

    frame_count = int(round(args.fps * args.seconds))
    expected = args.rows * args.cols
    if frame_count != expected:
        raise SystemExit(f"fps * seconds must equal rows * cols: got {frame_count}, expected {expected}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    saved_sheet = outdir / "sprite_sheet.png"
    Image.open(sprite_sheet).convert("RGB").save(saved_sheet)

    frames_dir = outdir / "cropped_frames"
    frames = crop_sprite_sheet(saved_sheet, args.rows, args.cols, frames_dir)
    mp4_out = outdir / "one_second_animation.mp4"
    gif_out = outdir / "one_second_animation.gif"
    encode_video(frames_dir, frame_count, args.fps, mp4_out, gif_out)

    (outdir / "metadata.txt").write_text(
        "\n".join(
            [
                f"source_sprite_sheet={sprite_sheet}",
                f"sprite_sheet={saved_sheet}",
                f"cropped_frames_dir={frames_dir}",
                f"rows={args.rows}",
                f"cols={args.cols}",
                f"fps={args.fps}",
                f"seconds={args.seconds}",
                f"frames={len(frames)}",
                "pipeline=gpt_image_sprite_sheet -> crop_frames -> assemble_video",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(saved_sheet)
    print(frames_dir)
    print(mp4_out)
    print(gif_out)


if __name__ == "__main__":
    main()
