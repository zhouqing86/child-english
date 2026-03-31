import argparse
import asyncio
import json
from pathlib import Path

import edge_tts


DEFAULT_VOICE = "en-US-AnaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"


async def save_audio(text: str, output_path: Path, voice: str, rate: str, volume: str) -> None:
    communicator = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicator.save(str(output_path))


def load_manifest(manifest_path: Path) -> list[dict]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("audio-manifest.json must contain a list.")

    for item in data:
        if "file" not in item or "text" not in item:
            raise ValueError("Each manifest item must contain 'file' and 'text'.")

    return data


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lesson audio files from audio-manifest.json")
    parser.add_argument(
        "--lesson-dir",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to the lesson directory. Defaults to the current script's lesson folder.",
    )
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Edge TTS voice name")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speech rate, for example +0%% or -10%%")
    parser.add_argument("--volume", default=DEFAULT_VOLUME, help="Volume, for example +0%%")
    args = parser.parse_args()

    lesson_dir = Path(args.lesson_dir).resolve()
    manifest_path = lesson_dir / "audio-manifest.json"
    audio_dir = lesson_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(manifest_path)

    for entry in manifest:
        output_path = audio_dir / entry["file"]
        print(f"Generating {output_path.name}...")
        await save_audio(entry["text"], output_path, args.voice, args.rate, args.volume)

    print(f"Finished. Audio files saved to: {audio_dir}")


if __name__ == "__main__":
    asyncio.run(main())