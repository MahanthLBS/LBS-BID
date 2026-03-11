from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Set

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from .edl_parser import parse_edl
from .xml_parser import parse_xml
from .thumbnail import generate_thumbnails
from .excel import build_workbook

app = FastAPI(title="Bid XLS Generator")
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")



@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


def _parse_shots(file_name: str, content: str, fps: float) -> List[dict]:
    lower_name = file_name.lower()
    if lower_name.endswith(".xml"):
        return parse_xml(content, fps)
    if lower_name.endswith(".edl"):
        return parse_edl(content, fps)
    if "<" in content[:1000]:
        return parse_xml(content, fps)
    return parse_edl(content, fps)




@app.post("/generate")
async def generate(
    request: Request,
    edl_file: UploadFile = File(...),
    video_file: UploadFile | None = File(None),
    fps: float = Form(24.0),
) -> FileResponse:
    if fps <= 0:
        raise HTTPException(status_code=400, detail="fps must be positive")

    content = (await edl_file.read()).decode("utf-8", errors="replace")
    try:
        shots = _parse_shots(edl_file.filename or "input.edl", content, fps)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    temp_dir = TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    try:
        if video_file:
            video_path = temp_path / (video_file.filename or "input.mp4")
            video_path.write_bytes(await video_file.read())
            try:
                generate_thumbnails(video_path, shots, fps, temp_path / "thumbs")
            except RuntimeError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        xlsx_path = temp_path / "bid.xlsx"
        build_workbook(shots, xlsx_path)
    except Exception:
        temp_dir.cleanup()
        raise

    return FileResponse(
        path=str(xlsx_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="bid.xlsx",
        background=BackgroundTask(temp_dir.cleanup),
    )
