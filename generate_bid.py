from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Dict, Optional

from app.edl_parser import parse_edl
from app.xml_parser import parse_xml
from app.thumbnail import generate_thumbnails
from app.excel import build_workbook, DEFAULT_COLUMNS


def _parse_shots(file_name: str, content: str, fps: float) -> List[Dict[str, object]]:
    lower_name = file_name.lower()
    if lower_name.endswith(".xml"):
        return parse_xml(content, fps)
    if lower_name.endswith(".edl"):
        return parse_edl(content, fps)
    if "<" in content[:1000]:
        return parse_xml(content, fps)
    return parse_edl(content, fps)


def _find_inputs(input_path: Path) -> tuple[Path, Optional[Path]]:
    if input_path.is_dir():
        edl_candidates = sorted(
            list(input_path.glob("*.edl")) + list(input_path.glob("*.xml"))
        )
        if not edl_candidates:
            raise FileNotFoundError("No .edl or .xml files found in input directory")
        video_candidates = sorted(
            list(input_path.glob("*.mov"))
            + list(input_path.glob("*.mp4"))
            + list(input_path.glob("*.mxf"))
        )
        video_path = video_candidates[0] if video_candidates else None
        return edl_candidates[0], video_path

    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    return input_path, None


def _write_csv(
    shots: List[Dict[str, object]],
    output_path: Path,
    columns: Optional[List[str]] = None,
) -> None:
    header = columns or DEFAULT_COLUMNS
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for shot in shots:
            writer.writerow(
                [
                    shot.get("shot"),
                    shot.get("start_frame"),
                    shot.get("end_frame"),
                    shot.get("duration"),
                    shot.get("thumbnail_path") or "",
                    "",
                    "",
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate bid.xlsx and bid.csv from an EDL/XML and optional video."
    )
    parser.add_argument(
        "--input",
        default="bid",
        help="Input .edl/.xml file or a folder containing it (default: bid)",
    )
    parser.add_argument(
        "--video",
        default=None,
        help="Optional video file path (overrides auto-detect from folder)",
    )
    parser.add_argument("--fps", type=float, default=24.0, help="Frames per second")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write outputs (default: current directory)",
    )
    parser.add_argument(
        "--base-name",
        default="bid",
        help="Base name for outputs (default: bid -> bid.xlsx/bid.csv)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    edl_path, auto_video = _find_inputs(input_path)
    video_path = Path(args.video) if args.video else auto_video

    content = edl_path.read_text(encoding="utf-8", errors="replace")
    shots = _parse_shots(edl_path.name, content, args.fps)

    if video_path:
        generate_thumbnails(video_path, shots, args.fps, Path(args.output_dir) / "thumbs")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    build_workbook(shots, output_dir / f"{args.base_name}.xlsx")
    _write_csv(shots, output_dir / f"{args.base_name}.csv")


if __name__ == "__main__":
    main()
