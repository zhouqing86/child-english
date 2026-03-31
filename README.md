# Child English

Sentence-first English lessons for young children, organized by daily-life scenarios.

## Structure

- `Spec.md`: overall curriculum plan and project specification
- `lesson1` to `lesson24`: lesson content, audio manifests, and supporting materials
- `scripts`: project-level tooling for audio generation and other helpers

## Quick Start

1. Create or activate the local Python environment.
2. Install dependencies with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
3. Generate audio for one lesson with `.\.venv\Scripts\python.exe .\scripts\generate_audio.py --lesson lesson1`.
4. Generate audio for all completed lessons with `.\.venv\Scripts\python.exe .\scripts\generate_audio.py --all`.
5. Generate one MP3 per dialogue with `.\.venv\Scripts\python.exe .\scripts\generate_dialogue_audio.py --all`.
6. Generate one MP4 lesson video per lesson with `.\.venv\Scripts\python.exe .\scripts\generate_lesson_video.py --all`.