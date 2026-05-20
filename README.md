# IP Frame Sheet

Codex skill for turning a reference character image into a one-second animation through a sprite-sheet-first workflow.

The intended pipeline is:

```text
reference image -> GPT Image generated 4x6 sprite sheet -> crop 24 frames -> encode 1-second MP4/GIF
```

This skill is designed for workflows where GPT Image can generate a strong still image but the final deliverable needs a short video-like animation. It keeps the image model responsible for generating the sprite sheet and uses local deterministic tooling only for cropping and video assembly.

## What This Skill Does

- Builds prompts for a reference-preserving 4x6 animation sprite sheet.
- Uses Codex's built-in image generation flow as the main way to create the sprite sheet.
- Crops the generated sprite sheet into 24 ordered frames.
- Encodes the cropped frames into a 24 fps, one-second MP4 and GIF.
- Includes QA guidance for rejecting rigid "sticker motion" outputs.

## Repository Layout

```text
.
├── SKILL.md                         # Codex skill instructions
├── agents/openai.yaml               # Codex UI metadata
├── assets/reference-character.png   # Small sample reference asset
├── references/workflow.md           # Detailed workflow and QA notes
└── scripts/
    ├── build_prompt.py              # Prompt builder for 4x6 sprite sheets
    ├── sprite_to_video.py           # Main crop-and-encode script
    └── make_one_second_video.py     # Procedural preview fallback only
```

## Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/<your-user>/ip-frame-sheet.git ~/.codex/skills/ip-frame-sheet
```

Restart Codex if needed, then invoke the skill as:

```text
Use $ip-frame-sheet with this reference image to make a one-second typing animation.
```

## Requirements

For the main Codex workflow:

- Codex with built-in image generation enabled.
- No `OPENAI_API_KEY` is required when using Codex's built-in image generation tool.

For local crop/video assembly:

- Python 3.10+
- Pillow
- ffmpeg

Install Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

Install ffmpeg with Homebrew on macOS:

```bash
brew install ffmpeg
```

## Usage

### 1. Generate The Sprite Sheet With GPT Image

Use the reference image as the character identity source and ask GPT Image for one combined sprite sheet, not separate images.

Prompt shape:

```text
Use the attached reference image as the exact character identity reference.
Generate a single clean 4 rows x 6 columns sprite sheet, exactly 24 equal cells.
No text, no numbers, no labels, no watermark.

The character must remain the same in every cell.
Action sequence: natural typing/coding animation at a computer over one second.
Each cell is a smooth sequential micro-pose, read left to right, top to bottom.

Make the motion natural, not rigid sticker movement:
body breathing, head/eye glow changes, flame flicker, arm shifts, claws/hand tapping,
tail and wing follow-through.

Consistent camera angle, consistent lighting, consistent scale, white or light background,
clear gutters between cells, crop-ready square cells.
```

Generated images are normally saved by Codex under `~/.codex/generated_images/...`. Copy the selected sprite sheet into your working directory.

### 2. Crop And Encode

```bash
python scripts/sprite_to_video.py \
  --sprite-sheet /path/to/gpt-image-sprite-sheet.png \
  --outdir /tmp/ip-frame-sheet-output
```

Outputs:

```text
/tmp/ip-frame-sheet-output/
├── sprite_sheet.png
├── cropped_frames/
│   ├── frame_000.png
│   ├── ...
│   └── frame_023.png
├── one_second_animation.gif
├── one_second_animation.mp4
└── metadata.txt
```

### 3. Verify

Use `ffprobe`:

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=nb_frames,r_frame_rate,duration,width,height \
  -of default=nw=1 \
  /tmp/ip-frame-sheet-output/one_second_animation.mp4
```

Expected for the default flow:

```text
r_frame_rate=24/1
duration=1.000000
nb_frames=24
```

## QA Checklist

Reject or regenerate the sprite sheet if:

- The sheet is not a clean 4x6 grid.
- The character identity drifts across cells.
- The output contains text, labels, numbers, watermarks, or UI chrome.
- The sprite sheet shows rigid whole-image movement instead of internal character motion.
- Cells are uneven, overlapping, or not safely crop-ready.

## Notes

`scripts/make_one_second_video.py` is included only as a local procedural preview fallback. It is not the main workflow and should not be used when Codex/GPT Image generation is available.

## License

MIT
