#!/usr/bin/env python3
"""Build a reference-based animation frame-sheet prompt."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_REFERENCE = Path(__file__).resolve().parents[1] / "assets" / "reference-character.png"
DEFAULT_SUBJECT = (
    "chibi cyber monster reference character with black armored body, tall ear-like helmet fins, "
    "flame crest, glowing blue eye orb, red visor, large silver mechanical cannon arm, wing, tail, "
    "clawed limbs, red armor bands, and white background"
)


def parse_layout(value: str) -> tuple[int, int]:
    normalized = value.lower().replace(" ", "")
    if "x" not in normalized:
        raise argparse.ArgumentTypeError("layout must look like 4x6")
    rows_text, cols_text = normalized.split("x", 1)
    rows, cols = int(rows_text), int(cols_text)
    if rows <= 0 or cols <= 0:
        raise argparse.ArgumentTypeError("layout dimensions must be positive")
    return rows, cols


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a prompt for a sequential animation frame sheet.")
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE), help="Path to the reference character image.")
    parser.add_argument("--subject", default=DEFAULT_SUBJECT, help="Stable character identity description.")
    parser.add_argument("--action", required=True, help="Action to animate across the sheet.")
    parser.add_argument("--layout", type=parse_layout, default=parse_layout("4x6"), help="Rows x columns. Default: 4x6.")
    parser.add_argument("--duration", default="1 second", help="Target animation duration. Default: 1 second.")
    parser.add_argument("--fps", type=int, default=24, help="Target frames per second. Default: 24.")
    parser.add_argument("--background", default="clean white background", help="Background style.")
    args = parser.parse_args()

    rows, cols = args.layout
    frame_count = rows * cols
    reference = Path(args.reference)
    if not reference.exists():
        raise SystemExit(f"Reference image not found: {reference}")

    prompt = f"""Use the attached/reference image as the character identity anchor: {reference}.

Generate one combined animation frame sheet for this character.

Subject identity to preserve: {args.subject}
Action sequence: {args.action}
Layout: {rows} rows x {cols} columns, exactly {frame_count} equal-size frames.
Timing: {args.duration}, intended for {args.fps} fps playback.
Reading order: left to right, top to bottom, frame 1 through frame {frame_count}.
Background: {args.background}.

Requirements:
- Keep the same character design, silhouette, proportions, face, colors, outfit, accessories, and material finish in every cell.
- Show smooth micro-pose changes from frame to frame, with no abrupt jumps.
- Use a consistent camera angle, focal length, lighting, and scale.
- Keep each frame fully inside its cell with clear gutters between cells.
- Do not add labels, frame numbers, captions, UI, watermarks, borders around the whole image, or extra characters.
- Make the final sheet easy to crop into individual frames for a GIF or one-second video."""

    negative = """Negative prompt:
identity drift, different character per frame, changing outfit, changing colors, inconsistent face, inconsistent camera angle, missing frames, extra frames, merged cells, uneven grid, text, labels, numbers, watermark, logo, cropped subject, blurry details, low resolution, chaotic motion"""

    print(prompt)
    print()
    print(negative)


if __name__ == "__main__":
    main()
