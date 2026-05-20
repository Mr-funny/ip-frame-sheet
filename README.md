# IP Frame Sheet

[English](README.en.md)

一个 Codex skill：用户输入一张参考角色图，Codex 先用 GPT Image 生成 4x6 雪碧图，再裁剪 24 帧，最后合成 1 秒 MP4/GIF 视频。

目标管线：

```text
用户输入参考图 -> GPT Image 生成 4x6 雪碧图 -> 裁剪 24 帧 -> 编码 1 秒 MP4/GIF
```

这个 skill 适合“图像模型能生成高质量静态图，但最终想要一段短视频/动图”的场景。GPT Image 负责根据参考图生成完整雪碧图；本地脚本只做确定性的裁剪和视频合成。

## 功能

- 接收用户提供的参考角色图，完成从参考图到视频的端到端流程。
- 为“参考图保真”的 4x6 动画雪碧图生成提示词。
- 使用 Codex 内置图像生成能力作为主流程，不需要 `OPENAI_API_KEY`。
- 将生成好的雪碧图裁剪成 24 张有序帧。
- 将裁剪帧编码成 24 fps、1 秒的 MP4 和 GIF。
- 提供 QA 规则，避免“整张贴纸僵硬移动”的假动画。

## 目录结构

```text
.
├── SKILL.md                         # Codex skill 指令
├── agents/openai.yaml               # Codex UI 元数据
├── assets/reference-character.png   # 示例参考角色图
├── references/workflow.md           # 详细流程和质检规则
└── scripts/
    ├── build_prompt.py              # 4x6 雪碧图提示词生成器
    ├── sprite_to_video.py           # 主流程：裁剪雪碧图并合成视频
    └── make_one_second_video.py     # 程序化预览 fallback，非主流程
```

## 安装

克隆到 Codex skills 目录：

```bash
git clone https://github.com/Mr-funny/ip-frame-sheet.git ~/.codex/skills/ip-frame-sheet
```

如有需要，重启 Codex，然后这样调用：

```text
Use $ip-frame-sheet with this reference image to generate a one-second typing video.
```

## 环境要求

Codex 主流程：

- Codex 已启用内置图像生成能力。
- 使用 Codex 内置图像生成时，不需要 `OPENAI_API_KEY`。

本地裁剪和视频合成：

- Python 3.10+
- Pillow
- ffmpeg

安装 Python 依赖：

```bash
python3 -m pip install -r requirements.txt
```

macOS 可用 Homebrew 安装 ffmpeg：

```bash
brew install ffmpeg
```

## 使用方法

### Codex 端到端用法

在 Codex 里上传或提供一张参考角色图，然后直接说：

```text
Use $ip-frame-sheet with this reference image to generate a one-second typing video.
```

Codex 应该执行完整流程：

```text
1. 读取用户输入的参考图
2. 用内置 GPT Image 生成一张 4x6 / 24 帧雪碧图
3. 把生成的雪碧图保存到工作目录
4. 运行 scripts/sprite_to_video.py 裁剪 24 张帧
5. 输出 one_second_animation.mp4 和 one_second_animation.gif
6. 用 ffprobe 验证视频是 24 fps、24 帧、约 1 秒
```

### 1. 用 GPT Image 生成雪碧图

把参考图作为角色身份来源，让 GPT Image 输出一张合并雪碧图，不要先生成 24 张单独图片。

提示词结构：

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

Codex 生成的图片通常会保存在 `~/.codex/generated_images/...`。选中满意的雪碧图后，把它复制到工作目录。这个雪碧图是后续裁剪和视频合成的唯一输入。

### 2. 裁剪并合成视频

```bash
python scripts/sprite_to_video.py \
  --sprite-sheet /path/to/gpt-image-sprite-sheet.png \
  --outdir /tmp/ip-frame-sheet-output
```

输出：

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

### 3. 验证

使用 `ffprobe`：

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=nb_frames,r_frame_rate,duration,width,height \
  -of default=nw=1 \
  /tmp/ip-frame-sheet-output/one_second_animation.mp4
```

默认期望：

```text
r_frame_rate=24/1
duration=1.000000
nb_frames=24
```

## 质检清单

如果出现以下问题，应该重新生成雪碧图：

- 不是干净的 4x6 网格。
- 角色身份在不同格子之间漂移。
- 图片里出现文字、编号、标签、水印或 UI 元素。
- 只是整张角色图平移/旋转，没有身体、头部、眼睛、火焰、手臂、尾巴等内部动作。
- 单元格不均匀、重叠，或不适合稳定裁剪。

## 说明

`scripts/make_one_second_video.py` 只是本地程序化预览 fallback。它不是主流程；当 Codex/GPT Image 可用时，不应该用它代替图像生成。

## 许可证

MIT
