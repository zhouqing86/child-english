import argparse
import os
from pathlib import Path

import requests


PEXELS_ENDPOINT = "https://api.pexels.com/videos/search"


def search_video(api_key: str, query: str) -> dict | None:
    response = requests.get(
        PEXELS_ENDPOINT,
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 1, "orientation": "portrait"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    videos = payload.get("videos", [])
    if not videos:
        return None
    return videos[0]


def choose_file(video: dict) -> str:
    files = video.get("video_files", [])
    if not files:
        raise ValueError("No downloadable video files were returned by Pexels.")

    mp4_files = [item for item in files if item.get("file_type") == "video/mp4"]
    if not mp4_files:
        raise ValueError("No MP4 video file found.")

    mp4_files.sort(key=lambda item: item.get("width", 0))
    return mp4_files[0]["link"]


def download_file(url: str, output_path: Path) -> None:
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    handle.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a stock video from Pexels into a lesson video folder.")
    parser.add_argument("--query", required=True, help="Search query, for example 'child brushing teeth'")
    parser.add_argument(
        "--output",
        required=True,
        help="Output mp4 path, for example lesson1/video/01_brush_your_teeth.mp4",
    )
    parser.add_argument("--api-key", default=os.getenv("PEXELS_API_KEY"), help="Pexels API key")
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit("Missing API key. Set PEXELS_API_KEY or pass --api-key.")

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    video = search_video(args.api_key, args.query)
    if video is None:
        raise SystemExit(f"No videos found for query: {args.query}")

    video_url = choose_file(video)
    download_file(video_url, output_path)
    print(f"Saved video to: {output_path}")


if __name__ == "__main__":
    main()