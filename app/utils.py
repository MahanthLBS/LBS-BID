from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimecodeRange:
    rec_in: str
    rec_out: str


def timecode_to_frames(timecode: str, fps: float) -> int:
    parts = timecode.split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid timecode: {timecode}")
    hours, minutes, seconds, frames = (int(p) for p in parts)
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return int(round(total_seconds * fps + frames))


def frames_to_timecode(frame_count: int, fps: float) -> str:
    if fps <= 0:
        raise ValueError("fps must be positive")
    total_seconds = int(frame_count // fps)
    frames = int(round(frame_count - (total_seconds * fps)))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def timecode_to_seconds(timecode: str, fps: float) -> float:
    parts = timecode.split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid timecode: {timecode}")
    hours, minutes, seconds, frames = (int(p) for p in parts)
    base_seconds = hours * 3600 + minutes * 60 + seconds
    return base_seconds + (frames / fps)
