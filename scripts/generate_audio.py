import argparse
import asyncio
import json
from pathlib import Path

import edge_tts


DEFAULT_VOICE = "en-US-AnaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"
ROOT_DIR = Path(__file__).resolve().parents[1]


async def save_audio(text: str, output_path: Path, voice: str, rate: str, volume: str) -> None:
    communicator = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicator.save(str(output_path))


def load_manifest(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"{manifest_path} must contain a list.")

    normalized: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict) or "file" not in item or "text" not in item:
            raise ValueError(f"Each manifest item in {manifest_path} must contain 'file' and 'text'.")
        normalized.append({"file": str(item["file"]), "text": str(item["text"])})

    return normalized


def resolve_lessons(selected_lesson: str | None, generate_all: bool) -> list[Path]:
    if selected_lesson and generate_all:
        raise ValueError("Use either --lesson or --all, not both.")

    if selected_lesson:
        lesson_dir = (ROOT_DIR / selected_lesson).resolve()
        if not lesson_dir.exists():
            raise FileNotFoundError(f"Lesson directory not found: {lesson_dir}")
        return [lesson_dir]

    lesson_dirs = sorted(
        path for path in ROOT_DIR.glob("lesson*") if path.is_dir() and (path / "audio-manifest.json").exists()
    )
    if generate_all:
        return lesson_dirs

    default_lesson = ROOT_DIR / "lesson1"
    return [default_lesson] if (default_lesson / "audio-manifest.json").exists() else lesson_dirs[:1]


async def generate_lesson_audio(lesson_dir: Path, voice: str, rate: str, volume: str) -> None:
    manifest_path = lesson_dir / "audio-manifest.json"
    if not manifest_path.exists():
        print(f"Skipping {lesson_dir.name}: audio-manifest.json not found.")
        return

    audio_dir = lesson_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(manifest_path)

    print(f"Generating audio for {lesson_dir.name}...")
    for entry in manifest:
        output_path = audio_dir / entry["file"]
        print(f"  - {output_path.name}")
        await save_audio(entry["text"], output_path, voice, rate, volume)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate audio files for one lesson or all completed lessons.")
    parser.add_argument("--lesson", help="Lesson directory name, for example lesson1")
    parser.add_argument("--all", action="store_true", help="Generate audio for all lessons with audio-manifest.json")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Edge TTS voice name")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speech rate, for example +0%% or -10%%")
    parser.add_argument("--volume", default=DEFAULT_VOLUME, help="Volume, for example +0%%")
    args = parser.parse_args()

    lesson_dirs = resolve_lessons(args.lesson, args.all)
    if not lesson_dirs:
        raise SystemExit("No lessons with audio-manifest.json were found.")

    for lesson_dir in lesson_dirs:
        await generate_lesson_audio(lesson_dir, args.voice, args.rate, args.volume)

    print("Finished.")


if __name__ == "__main__":
    asyncio.run(main())