"""
Video Frame Search API using FastAPI

Author: Mohammed Faris Sait

This is the main FastAPI app that:
- Accepts video uploads
- Extracts frames from the video
- Computes feature vectors for each frame
- Stores the vectors in Qdrant
- Provides an endpoint to query similar frames using an image

Endpoints:
- POST /upload-video/
- POST /query/
- GET /frame/{frame_name}
- GET /frames/
"""


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

import logging

from .video_utils import extract_frames
from .vector_utils import add_to_db, compute_feature_vector, search_similar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Frame Search API",
    version="1.0.0",
    description="Upload videos, extract frames, and query similar frames using Qdrant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_FRAMES_DIR = "static/frames"
os.makedirs(STATIC_FRAMES_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Video Frame Search API",
        "version": "1.0.0",
        "endpoints": ["/upload-video/", "/query/", "/frame/{frame_name}", "/frames/"]
    }

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail="Unsupported video format")

    video_path = f"temp_{file.filename}"
    try:
        with open(video_path, "wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty video file")
            f.write(content)

        frames = extract_frames(video_path, STATIC_FRAMES_DIR)
        if not frames:
            raise HTTPException(status_code=500, detail="No frames extracted")

        for frame in frames:
            add_to_db(frame)

        return {
            "message": "Video processed successfully",
            "frames_saved": len(frames),
            "output_directory": STATIC_FRAMES_DIR
        }

    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

@app.post("/query/")
async def query_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Unsupported image format")

    query_path = f"temp_query_{file.filename}"
    try:
        with open(query_path, "wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty image file")
            f.write(content)

        query_vector = compute_feature_vector(query_path)
        results = search_similar(query_vector)

        formatted = [
            {
                "frame_name": os.path.basename(path),
                "frame_url": f"/frame/{os.path.basename(path)}",
                "similarity_score": round(score, 4),
                "frame_path": path
            }
            for path, score in results
        ]
        return {
            "query_processed": True,
            "results_count": len(formatted),
            "results": formatted
        }

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {e}")
    finally:
        if os.path.exists(query_path):
            os.remove(query_path)

@app.get("/frame/{frame_name}")
async def get_frame(frame_name: str):
    frame_path = os.path.join(STATIC_FRAMES_DIR, frame_name)
    if not os.path.exists(frame_path):
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(frame_path)

@app.get("/frames/")
async def list_frames():
    try:
        frames = [
            f for f in os.listdir(STATIC_FRAMES_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        return {"frames": frames, "count": len(frames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frame listing failed: {e}")
