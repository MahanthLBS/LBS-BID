from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Dict

from .utils import timecode_to_seconds


def generate_thumbnails(
    video_path: Path,
    shots: List[Dict[str, object]],
    fps: float,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        rec_in = str(shot["rec_in"])
        rec_out = str(shot["rec_out"])
        in_seconds = timecode_to_seconds(rec_in, fps)
        out_seconds = timecode_to_seconds(rec_out, fps)
        mid_seconds = max(in_seconds, (in_seconds + out_seconds) / 2.0)
        output_path = output_dir / f"shot_{shot['shot']:04d}.jpg"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            f"{mid_seconds:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed for shot {shot['shot']}: {result.stderr}")
        shot["thumbnail_path"] = str(output_path)
