---
name: ip-frame-sheet
description: Generate one-second videos from user-provided reference character images through a GPT Image sprite-sheet workflow. Use when the user provides or points to a character/IP/reference image and wants Codex to generate a 4x6/24-frame sprite sheet, crop it into frames, and export MP4/GIF video while preserving the reference character identity and natural motion.
---

# IP Frame Sheet

## Overview

Convert the user's reference character image into a video. The required end-to-end workflow is: user input reference image -> built-in GPT Image generates one combined 4x6/24-frame sprite sheet -> crop that sprite sheet into ordered frames -> assemble the cropped frames into a 1-second MP4/GIF.

Use this skill to produce either:
- A generation prompt for an image model.
- A concrete frame plan for a character action.
- A GPT Image generated sprite sheet, cropped frame sequence, and 1-second MP4/GIF when a reference image is available.
- QA guidance for checking whether the resulting sheet can become a GIF or short video.

If the user asks for a video and provides a reference image, do the complete workflow. Do not stop at a prompt or at the sprite sheet unless the user explicitly asks for only that intermediate artifact.

## Inputs

Collect or infer:
- Reference image path or attachment.
- Subject description, especially identity markers that must remain stable.
- Action to animate, such as typing, walking, turning, attacking, waving, blinking, or breathing.
- Sheet layout, defaulting to `4x6`.
- Duration and frame rate, defaulting to `1 second at 24 fps`.
- Background preference, defaulting to clean white or transparent.

When the reference is a recognizable third-party IP and the user has not stated they own or may use it, avoid claiming ownership or making commercial licensing assumptions. For public outputs, offer an original character variant that preserves only high-level traits.

## Workflow

1. Inspect the reference image and list persistent identity anchors: silhouette, head shape, eyes, outfit, color palette, accessories, proportions, and material finish.
2. Use the built-in image generation tool with the reference image to generate one combined sprite sheet only. Do not generate 24 separate images first.
3. The sprite sheet must contain 24 micro-poses in a 4x6 grid. Keep body proportions and camera angle stable; change only pose, expression, limbs, cloth, effects, or small secondary motion.
4. Keep the prompt explicit about reading order: row 1 frame 1-6, row 2 frame 7-12, row 3 frame 13-18, row 4 frame 19-24.
5. Crop the sprite sheet into 24 equal cells in reading order. The cropped files are the source frames for video assembly.
6. Assemble the cropped frames at 24 fps for a 1-second video. Validate the video against the cropped frames, not against any pre-sheet intermediate frames.

Natural motion requirement: the generated sprite sheet must not show one rigid pasted character moving from cell to cell. Prompt GPT Image to animate independent parts: body breathing, head or face, eyes/glow, hair/flame/cloth effects, arms/hands, props, tail/wing/secondary appendages, and contact motion with the environment.

## Generate A Video

Use the built-in image generation tool first with the user's reference image visible in the conversation. The prompt must reference the input character image and ask for a single 4x6 sprite sheet. After the generated sprite sheet is saved locally, run `scripts/sprite_to_video.py`:

```bash
python scripts/sprite_to_video.py \
  --sprite-sheet /path/to/gpt-image-sprite-sheet.png \
  --outdir /tmp/ip-frame-sheet-output
```

The script creates:
- `sprite_sheet.png`
- `cropped_frames/frame_000.png` through `cropped_frames/frame_023.png`
- `one_second_animation.gif`
- `one_second_animation.mp4`

`scripts/sprite_to_video.py` does not draw or invent frames. It only crops the GPT Image generated sprite sheet and encodes the cropped cells into video. `scripts/make_one_second_video.py` is a procedural preview fallback only; do not use it as the main workflow when image generation is available.

End-to-end completion means these final files exist:
- the GPT Image generated `sprite_sheet.png`
- 24 cropped files in `cropped_frames/`
- `one_second_animation.mp4`
- `one_second_animation.gif`

## Prompt Builder

Use `scripts/build_prompt.py` to draft a reusable prompt:

```bash
python scripts/build_prompt.py \
  --action "typing code at a computer, focused expression, subtle head and hand movement"
```

The script defaults to `assets/reference-character.png`, a local reference asset based on the user's provided second image. Override `--reference` and `--subject` when the user supplies a different character.

## Quality Bar

Reject or revise outputs with:
- Fewer or more than 24 frames when a 4x6 sheet was requested.
- Major identity drift between cells.
- Rigid sticker motion where the entire character moves but limbs, face, effects, tail, wing, or props do not animate.
- Random camera jumps, changing outfits, changing species, or changing object placement.
- Overlapping cells, missing gutters, text overlays, watermarks, labels, or UI chrome.
- Motion that skips from start to end without readable in-between frames.

## References

Read `references/workflow.md` when the user needs detailed frame planning, video assembly notes, or a stronger prompt template.
