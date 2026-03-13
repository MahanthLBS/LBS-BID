# LBS-BID
Bid XLS Generator for VFX bidding.

## What it does
- Accepts EDL or XML input
- Extracts shot ranges
- Optionally embeds thumbnails from a video
- Generates a bid-ready Excel file

## Requirements
- Python 3.10+
- ffmpeg in PATH (only needed if you upload video)

## Run locally
1) Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Start the server:

```bash
uvicorn app.main:app --reload
```

3) Open http://127.0.0.1:8000

## Notes
- EDL parsing supports common CMX3600 event lines with timecodes.
- XML parsing supports basic Final Cut Pro XML clipitems with start/end frames.
# LBS-BID
