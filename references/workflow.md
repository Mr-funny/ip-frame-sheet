# Reference-to-Frame-Sheet Workflow

## Default Sheet

- Layout: 4 rows x 6 columns.
- Count: 24 frames.
- Playback: 24 fps for 1 second.
- Order: left-to-right, top-to-bottom.
- Output stage 1: one GPT Image generated combined sprite sheet, not 24 separate files.
- Output stage 2: crop that sprite sheet into 24 ordered frame files.
- Output stage 3: assemble the cropped frame files into video.

## Frame Planning

Plan the action as small increments:

- Frames 1-4: establish start pose and first anticipation.
- Frames 5-10: begin the main motion.
- Frames 11-16: strongest action or expression change.
- Frames 17-21: settle or follow-through.
- Frames 22-24: loop-friendly return or held final pose.

For looped GIFs, make frame 24 close to frame 1. For one-shot videos, let frame 24 be the final pose.

Avoid rigid sticker animation. The sprite sheet should show independent part motion:

- Body breathing or weight shift.
- Head, face, eye glow, or expression changes.
- Hair, flame, cloth, smoke, or glow effects flickering on their own timing.
- Arms, hands, claws, or tools moving in contact with the action.
- Tail, wing, ears, or secondary appendages following through.
- Props responding to the action, such as key presses or cursor flicker.

## Identity Anchors

Before writing the prompt, extract stable anchors from the reference:

- Head and body silhouette.
- Eye shape, face markings, expression style.
- Hair, helmet, ears, horns, wings, tail, claws, or other outline-defining parts.
- Outfit, armor, mechanical pieces, accessories, and props.
- Dominant colors and material finish.
- Camera angle and character scale.

Put these anchors in the prompt. Do not rely on "same as reference" alone.

## Strong Prompt Template

```text
Using the attached reference image as the identity source, generate one combined animation frame sheet of [subject].

The character must remain the same in every frame: [identity anchors].

Action: [action]. Show this as 24 smooth micro-poses over 1 second.
Natural movement: do not move the whole character as one rigid sticker. Animate separate parts with overlapping timing: body breathing, head/eyes, arms/hands, effects, tail/wing/secondary appendages, and prop contact.
Grid: 4 rows x 6 columns, exactly 24 equal cells, left-to-right and top-to-bottom order.
Composition: [full body / bust / close-up], consistent camera angle, consistent lighting, consistent scale.
Background: [white / transparent / simple scene].

No text, no labels, no frame numbers, no watermark, no extra characters. Keep clear gutters between cells. Each cell should be crop-ready for GIF or video assembly.
```

## Output QA

Check:

- The grid has exactly 4 rows and 6 columns.
- The same character appears in all cells.
- The motion can be read by scanning frames in order.
- The subject is not cut off unless the requested composition is close-up.
- There are no text artifacts or numbers.
- Lighting and camera angle do not jump.

If QA fails, request a revision with the specific failure, not a broad retry.

## Local Sprite-Sheet-To-Video Assembly

When an actual file is required, first use built-in image generation to create the 4x6 sprite sheet from the reference image, then run `scripts/sprite_to_video.py` to crop and assemble it:

```bash
python scripts/sprite_to_video.py \
  --sprite-sheet /path/to/gpt-image-sprite-sheet.png \
  --outdir /path/to/output
```

Keep these validation checks:

- One 4x6 `sprite_sheet.png`.
- 24 PNG frames cropped from that sprite sheet.
- MP4 encoded at 24 fps.
- Duration close to 1.000 seconds.
- No missing or duplicated frame numbers.
- Visible internal character motion, not just a whole-image transform.
