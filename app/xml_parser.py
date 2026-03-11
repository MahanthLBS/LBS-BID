from __future__ import annotations

from typing import List, Dict
import xml.etree.ElementTree as ET

from .utils import frames_to_timecode


def parse_xml(xml_text: str, fps: float) -> List[Dict[str, object]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML: {exc}") from exc

    shots: List[Dict[str, object]] = []
    for clip in root.findall(".//clipitem"):
        start = clip.findtext("start")
        end = clip.findtext("end")
        if start is None or end is None:
            continue
        try:
            start_frame = int(start)
            end_frame = int(end)
        except ValueError:
            continue
        duration = max(0, end_frame - start_frame)
        rec_in = frames_to_timecode(start_frame, fps)
        rec_out = frames_to_timecode(end_frame, fps)
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
        raise ValueError("No clip items with start/end frames found")
    return shots
