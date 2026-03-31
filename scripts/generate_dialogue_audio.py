from __future__ import annotations

import argparse
import asyncio
import tempfile
from pathlib import Path

import edge_tts

try:
    from moviepy import AudioFileClip, concatenate_audioclips
except ImportError:
    from moviepy.editor import AudioFileClip, concatenate_audioclips

from media_utils import parse_dialogue_groups, resolve_lessons


DEFAULT_PARENT_VOICE = "en-US-GuyNeural"
DEFAULT_CHILD_VOICE = "en-US-AnaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"
DEFAULT_RETRIES = 3


async def save_audio(text: str, output_path: Path, voice: str, rate: str, volume: str) -> None:
    last_error: Exception | None = None
    for attempt in range(1, DEFAULT_RETRIES + 1):
        try:
            communicator = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
            await communicator.save(str(output_path))
            return
        except edge_tts.exceptions.NoAudioReceived as error:
            last_error = error
            if attempt == DEFAULT_RETRIES:
                break
            wait_seconds = attempt
            print(f"    retrying after transient TTS failure ({attempt}/{DEFAULT_RETRIES})...")
            await asyncio.sleep(wait_seconds)

    if last_error is not None:
        raise last_error


def voice_for_speaker(speaker: str, parent_voice: str, child_voice: str) -> str:
    return parent_voice if speaker == "Parent" else child_voice


def combine_audio_files(audio_paths: list[Path], output_path: Path) -> None:
    clips = [AudioFileClip(str(path)) for path in audio_paths]
    final_clip = concatenate_audioclips(clips)
    try:
        final_clip.write_audiofile(str(output_path), codec="mp3", logger=None)
    finally:
        final_clip.close()
        for clip in clips:
            clip.close()


async def generate_lesson_dialogue_audio(
    lesson_dir: Path,
    parent_voice: str,
    child_voice: str,
    rate: str,
    volume: str,
) -> None:
    dialogue_path = lesson_dir / "dialogues.md"
    output_dir = lesson_dir / "audio" / "dialogues"
    output_dir.mkdir(parents=True, exist_ok=True)
    for existing_file in output_dir.glob("*.mp3"):
        existing_file.unlink()

    print(f"Generating dialogue audio for {lesson_dir.name}...")
    for entry in parse_dialogue_groups(dialogue_path):
        output_path = output_dir / str(entry["file"])
        print(f"  - {output_path.name}")

        with tempfile.TemporaryDirectory(prefix=f"{lesson_dir.name}_dialogue_") as temp_dir:
            temp_paths: list[Path] = []
            for line_index, line in enumerate(entry["lines"], start=1):
                temp_path = Path(temp_dir) / f"{line_index:02d}_{str(line['speaker']).lower()}.mp3"
                await save_audio(
                    str(line["text"]),
                    temp_path,
                    voice_for_speaker(str(line["speaker"]), parent_voice, child_voice),
                    rate,
                    volume,
                )
                temp_paths.append(temp_path)

            combine_audio_files(temp_paths, output_path)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one MP3 per dialogue from dialogues.md")
    parser.add_argument("--lesson", help="Lesson directory name, for example lesson1")
    parser.add_argument("--all", action="store_true", help="Generate dialogue audio for all lessons")
    parser.add_argument("--parent-voice", default=DEFAULT_PARENT_VOICE, help="Edge TTS voice for Parent lines")
    parser.add_argument("--child-voice", default=DEFAULT_CHILD_VOICE, help="Edge TTS voice for Child lines")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speech rate, for example +0%% or -10%%")
    parser.add_argument("--volume", default=DEFAULT_VOLUME, help="Volume, for example +0%%")
    args = parser.parse_args()

    lesson_dirs = resolve_lessons(args.lesson, args.all)
    if not lesson_dirs:
        raise SystemExit("No lessons with dialogues.md were found.")

    for lesson_dir in lesson_dirs:
        await generate_lesson_dialogue_audio(
            lesson_dir,
            parent_voice=args.parent_voice,
            child_voice=args.child_voice,
            rate=args.rate,
            volume=args.volume,
        )

    print("Finished.")


if __name__ == "__main__":
    asyncio.run(main())