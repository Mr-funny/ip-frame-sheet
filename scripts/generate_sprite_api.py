#!/usr/bin/env python3
"""Generate a 4x6 sprite sheet from a reference image using the OpenAI Images API.

This is the non-Codex fallback path. In Codex, prefer the built-in image
generation tool because it does not require the user to manage an API key.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path

from openai import OpenAI

DEFAULT_PROMPT = """Use the input image as the exact character identity reference.
Generate a single clean 4 rows x 6 columns sprite sheet, exactly 24 equal cells.
No text, no numbers, no labels, no watermark.

The character must remain the same in every cell.
Action sequence: natural typing/coding animation at a computer over one second.
Each cell is a smooth sequential micro-pose, read left to right, top to bottom.

Make the motion natural, not rigid sticker movement:
body breathing, head/eye glow changes, flame flicker, arm shifts, claws/hand tapping,
tail and wing follow-through.

Consistent camera angle, consistent lighting, consistent scale, white or light background,
clear gutters between cells, crop-ready square cells."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a GPT Image sprite sheet from a reference image.")
    parser.add_argument("--reference", required=True, help="Input reference character image path.")
    parser.add_argument("--output", required=True, help="Output sprite sheet PNG path.")
    parser.add_argument("--prompt-file", help="Optional text file containing the full image prompt.")
    parser.add_argument("--model", default="gpt-image-1.5", help="GPT Image model. Check current OpenAI docs before changing.")
    parser.add_argument("--size", default="1536x1024", help="Output size. 1536x1024 fits a 6x4 sheet well.")
    parser.add_argument("--quality", default="high", help="Image quality setting supported by the selected model.")
    args = parser.parse_args()

    reference = Path(args.reference)
    if not reference.exists():
        raise SystemExit(f"Reference image not found: {reference}")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    prompt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else DEFAULT_PROMPT
    client = OpenAI()

    with reference.open("rb") as image_file:
        result = client.images.edit(
            model=args.model,
            image=image_file,
            prompt=prompt,
            size=args.size,
            quality=args.quality,
            response_format="b64_json",
        )

    image_b64 = result.data[0].b64_json
    if not image_b64:
        raise SystemExit("Image API response did not include b64_json output")
    output.write_bytes(base64.b64decode(image_b64))
    print(output)


if __name__ == "__main__":
    main()
