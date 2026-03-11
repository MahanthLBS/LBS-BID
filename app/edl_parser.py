from __future__ import annotations

import re
from typing import List, Dict

from .utils import timecode_to_frames

_EDL_EVENT_RE = re.compile(
    r"^(?P<event>\d+)\s+\S+\s+\S+\s+\S+\s+"
    r"(?P<src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
    r"(?P<src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
    r"(?P<rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
    r"(?P<rec_out>\d{2}:\d{2}:\d{2}:\d{2})"
)


def parse_edl(text: str, fps: float) -> List[Dict[str, object]]:
    shots: List[Dict[str, object]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        match = _EDL_EVENT_RE.match(line)
        if not match:
            continue
        rec_in = match.group("rec_in")
        rec_out = match.group("rec_out")
        start_frame = timecode_to_frames(rec_in, fps)
        end_frame = timecode_to_frames(rec_out, fps)
        duration = max(0, end_frame - start_frame)
        shots.append(
            {
                "shot": len(shots) + 1,
                "rec_in": rec_in,
                "rec_out": rec_out,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "duration": duration,
            }
        )
    if not shots:
        raise ValueError("No EDL events with timecodes found")
    return shots
