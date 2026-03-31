from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from media_utils import load_manifest, parse_dialogue_groups, resolve_lessons

try:
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips


VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280
FPS = 24
MIN_SLIDE_SECONDS = 2.8
SLIDE_PADDING = 64


def pick_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = []
    windows_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    if bold:
        font_candidates.extend([windows_dir / "arialbd.ttf", windows_dir / "segoeuib.ttf"])
    else:
        font_candidates.extend([windows_dir / "arial.ttf", windows_dir / "segoeui.ttf"])

    for candidate in font_candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)

    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    if not words:
        return text

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.multiline_textbbox((0, 0), candidate, font=font, spacing=12)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return "\n".join(lines)


def render_slide(title: str, subtitle: str, text: str, accent: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(248, 244, 235))
    draw = ImageDraw.Draw(image)

    draw.ellipse((420, -120, 860, 320), fill=(255, 214, 153))
    draw.ellipse((-160, 900, 260, 1320), fill=(191, 221, 212))
    draw.rounded_rectangle((40, 40, VIDEO_WIDTH - 40, VIDEO_HEIGHT - 40), radius=48, outline=accent, width=5)

    title_font = pick_font(40, bold=True)
    subtitle_font = pick_font(28, bold=True)
    body_font = pick_font(54, bold=True)

    draw.text((SLIDE_PADDING, 120), title, font=title_font, fill=(70, 63, 58))
    draw.rounded_rectangle((SLIDE_PADDING, 200, 360, 260), radius=24, fill=accent)
    draw.text((SLIDE_PADDING + 24, 214), subtitle, font=subtitle_font, fill=(255, 255, 255))

    wrapped = wrap_text(draw, text, body_font, VIDEO_WIDTH - (SLIDE_PADDING * 2))
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=body_font, spacing=18, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (VIDEO_WIDTH - text_width) / 2
    text_y = max(360, (VIDEO_HEIGHT - text_height) / 2)
    draw.multiline_text(
        (text_x, text_y),
        wrapped,
        font=body_font,
        fill=(34, 34, 34),
        spacing=18,
        align="center",
    )

    return image


def with_duration(clip, duration: float):
    return clip.with_duration(duration) if hasattr(clip, "with_duration") else clip.set_duration(duration)


def with_audio(clip, audio_clip):
    return clip.with_audio(audio_clip) if hasattr(clip, "with_audio") else clip.set_audio(audio_clip)


def collect_items(lesson_dir: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for index, entry in enumerate(load_manifest(lesson_dir / "audio-manifest.json"), start=1):
        items.append(
            {
                "section": lesson_dir.name.replace("lesson", "Lesson "),
                "label": f"Sentence {index}",
                "text": entry["text"],
                "audio_path": lesson_dir / "audio" / entry["file"],
                "accent": (214, 116, 82),
            }
        )

    for entry in parse_dialogue_groups(lesson_dir / "dialogues.md"):
        items.append(
            {
                "section": lesson_dir.name.replace("lesson", "Lesson "),
                "label": f"Dialogue {entry['dialogue_index']}",
                "text": str(entry["text"]),
                "audio_path": lesson_dir / "audio" / "dialogues" / str(entry["file"]),
                "accent": (88, 149, 118),
            }
        )

    return items


def build_clip(item: dict[str, object]):
    image = render_slide(
        title=str(item["section"]),
        subtitle=str(item["label"]),
        text=str(item["text"]),
        accent=tuple(item["accent"]),
    )
    clip = ImageClip(np.array(image))

    audio_path = Path(item["audio_path"])
    if audio_path.exists():
        audio_clip = AudioFileClip(str(audio_path))
        duration = max(audio_clip.duration + 0.6, MIN_SLIDE_SECONDS)
        return with_audio(with_duration(clip, duration), audio_clip)

    return with_duration(clip, MIN_SLIDE_SECONDS)


def generate_lesson_video(lesson_dir: Path) -> Path:
    output_path = lesson_dir / "video" / f"{lesson_dir.name}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clips = [build_clip(item) for item in collect_items(lesson_dir)]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )
    final_clip.close()
    for clip in clips:
        clip.close()
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one MP4 lesson video from sentence and dialogue audio.")
    parser.add_argument("--lesson", help="Lesson directory name, for example lesson1")
    parser.add_argument("--all", action="store_true", help="Generate videos for all lessons")
    args = parser.parse_args()

    lesson_dirs = resolve_lessons(args.lesson, args.all)
    if not lesson_dirs:
        raise SystemExit("No lessons with dialogues.md were found.")

    for lesson_dir in lesson_dirs:
        print(f"Generating video for {lesson_dir.name}...")
        output_path = generate_lesson_video(lesson_dir)
        print(f"Saved video to: {output_path}")

    print("Finished.")


if __name__ == "__main__":
    main()