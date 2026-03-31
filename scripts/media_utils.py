from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SPEAKER_PATTERN = re.compile(r"^(Parent|Child):\s*(.+?)\s*$")


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
        path for path in ROOT_DIR.glob("lesson*") if path.is_dir() and (path / "dialogues.md").exists()
    )
    if generate_all:
        return lesson_dirs

    default_lesson = ROOT_DIR / "lesson1"
    return [default_lesson] if (default_lesson / "dialogues.md").exists() else lesson_dirs[:1]


def slugify(value: str, fallback: str = "item", max_length: int = 48) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower()).strip("_")
    if not normalized:
        normalized = fallback
    return normalized[:max_length].rstrip("_") or fallback


def parse_dialogues(dialogues_path: Path) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    dialogue_index = 0
    line_index = 0

    for raw_line in dialogues_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            dialogue_index += 1
            continue

        match = SPEAKER_PATTERN.match(line)
        if not match:
            continue

        speaker, text = match.groups()
        line_index += 1
        entries.append(
            {
                "dialogue_index": max(dialogue_index, 1),
                "line_index": line_index,
                "speaker": speaker,
                "text": text,
                "file": f"{line_index:02d}_{speaker.lower()}_{slugify(text)}.mp3",
            }
        )

    if not entries:
        raise ValueError(f"No dialogue lines were found in {dialogues_path}")

    return entries


def parse_dialogue_groups(dialogues_path: Path) -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []
    current_lines: list[dict[str, str]] = []
    dialogue_index = 0

    def flush_current_group() -> None:
        nonlocal current_lines, dialogue_index
        if not current_lines:
            return

        current_index = max(dialogue_index, 1)
        groups.append(
            {
                "dialogue_index": current_index,
                "lines": current_lines,
                "text": "\n".join(f"{line['speaker']}: {line['text']}" for line in current_lines),
                "file": f"{current_index:02d}_dialogue.mp3",
            }
        )
        current_lines = []

    for raw_line in dialogues_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            flush_current_group()
            dialogue_index += 1
            continue

        match = SPEAKER_PATTERN.match(line)
        if not match:
            continue

        speaker, text = match.groups()
        current_lines.append({"speaker": speaker, "text": text})

    flush_current_group()

    if not groups:
        raise ValueError(f"No dialogue groups were found in {dialogues_path}")

    return groups