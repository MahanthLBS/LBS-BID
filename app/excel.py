from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional

from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage


DEFAULT_COLUMNS = [
    "Shot",
    "Start Frame",
    "End Frame",
    "Duration",
    "Thumbnail",
    "Description",
    "Bid",
]


def build_workbook(
    shots: List[Dict[str, object]],
    output_path: Path,
    columns: Optional[List[str]] = None,
) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Bid"

    header = columns or DEFAULT_COLUMNS
    sheet.append(header)

    for idx, shot in enumerate(shots, start=2):
        row = [
            shot.get("shot"),
            shot.get("start_frame"),
            shot.get("end_frame"),
            shot.get("duration"),
            "",
            "",
            "",
        ]
        sheet.append(row)

        thumbnail_path = shot.get("thumbnail_path")
        if thumbnail_path:
            try:
                image = ExcelImage(thumbnail_path)
                image.height = 90
                image.width = 160
                cell = f"E{idx}"
                sheet.add_image(image, cell)
                sheet.row_dimensions[idx].height = 70
            except Exception:
                sheet[f"E{idx}"] = str(thumbnail_path)

    workbook.save(output_path)
