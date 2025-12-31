#!/usr/bin/env python3
"""Neuro-Parakeet MLX Server - German audio transcription server using parakeet-mlx."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import os
import re
import tempfile
import argparse
from datetime import datetime

try:
    from parakeet_mlx import from_pretrained
except ImportError:
    from_pretrained = None

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None

model = None
DEFAULT_MODEL = os.getenv("PARAKEET_MODEL", "mlx-community/parakeet-tdt-0.6b-v3")

class TranscriptionResponse(BaseModel):
    text: str
    recording_timestamp: Optional[str] = None
    segments: Optional[List[dict]] = None

def load_model(model_id: Optional[str] = None):
    global model
    if model is None and from_pretrained:
        model_id = model_id or os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
        if "/" in model_id and not os.path.exists(model_id) and snapshot_download:
            try:
                cache_dir = snapshot_download(repo_id=model_id, repo_type="model", local_files_only=True)
            except Exception:
                cache_dir = snapshot_download(repo_id=model_id, repo_type="model", local_files_only=False)
            model_id = cache_dir
        model = from_pretrained(model_id)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if from_pretrained:
        load_model()
    yield

app = FastAPI(lifespan=lifespan)

_PATH_NORM_RE = re.compile(r'/+')

class NormalizePathMiddleware(BaseHTTPMiddleware):
    """Middleware to normalize duplicate slashes in paths."""
    async def dispatch(self, request: Request, call_next):
        if '//' in request.url.path:
            s = dict(request.scope)
            s["path"] = s["path_info"] = _PATH_NORM_RE.sub('/', request.url.path)
            request = Request(s)
        return await call_next(request)

class ReverseProxyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle reverse proxy forwarded headers (nginx, etc.)."""
    async def dispatch(self, request: Request, call_next):
        # This middleware ensures the app works correctly behind a reverse proxy
        # The actual header handling is done by uvicorn's proxy_headers=True
        # We just add some response headers here
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        return response

# Add middlewares in order (reverse proxy first, then path normalization, then CORS)
app.add_middleware(ReverseProxyMiddleware)
app.add_middleware(NormalizePathMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def get_index_path():
    """Get the path to index.html, checking multiple possible locations."""
    # Try current file directory first
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "index.html"),
        os.path.join(os.getcwd(), "index.html"),
        "index.html",  # Current working directory
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path
    return None

@app.get("/")
async def root():
    """Root endpoint - serves index.html if available, otherwise returns status."""
    index_path = get_index_path()
    if index_path:
        return FileResponse(index_path, media_type="text/html")
    return {"status": "ok" if model else "error"}

@app.get("/transcription")
async def transcription_ui():
    """Serve the transcription UI interface."""
    index_path = get_index_path()
    if index_path:
        return FileResponse(index_path, media_type="text/html")
    return {"status": "ok" if model else "error", "message": "Transcription UI not found"}

def extract_text(r):
    if hasattr(r, 'text'):
        if hasattr(r, 'segments') and r.segments:
            return ' '.join(seg.text if hasattr(seg, 'text') else (seg.get('text', '') if isinstance(seg, dict) else str(seg)) for seg in r.segments)
        return r.text
    if isinstance(r, dict):
        if 'segments' in r and r['segments']:
            return ' '.join(seg.get('text', '') if isinstance(seg, dict) else str(seg) for seg in r['segments'])
        return r.get('text', '') or str(r)
    return str(r)

def clean_text(text: str) -> str:
    text = re.sub(r'\s*<unk>\s*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_segments(r):
    """Extract segment information with timing if available."""
    segments = []
    if hasattr(r, 'segments') and r.segments:
        for seg in r.segments:
            seg_dict = {
                'text': seg.text if hasattr(seg, 'text') else (seg.get('text', '') if isinstance(seg, dict) else str(seg))
            }
            if hasattr(seg, 'start'):
                seg_dict['start'] = seg.start
            elif isinstance(seg, dict) and 'start' in seg:
                seg_dict['start'] = seg['start']
            if hasattr(seg, 'end'):
                seg_dict['end'] = seg.end
            elif isinstance(seg, dict) and 'end' in seg:
                seg_dict['end'] = seg['end']
            segments.append(seg_dict)
    elif isinstance(r, dict) and 'segments' in r and r['segments']:
        for seg in r['segments']:
            seg_dict = {
                'text': seg.get('text', '') if isinstance(seg, dict) else str(seg)
            }
            if isinstance(seg, dict):
                if 'start' in seg:
                    seg_dict['start'] = seg['start']
                if 'end' in seg:
                    seg_dict['end'] = seg['end']
            segments.append(seg_dict)
    return segments if segments else None

@app.options("/v1/audio/transcriptions")
async def options_transcription():
    """Handle CORS preflight requests."""
    return {"status": "ok"}

@app.post("/v1/audio/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(file: UploadFile = File(...), model_name: str = Form("parakeet-tdt-0.6b-v3", alias="model"),
                               response_format: Optional[str] = Form("json"),
                               recording_timestamp: Optional[str] = Form(None)):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        p = tmp.name
    try:
        with open(p, 'wb') as f:
            f.write(await file.read())
        try:
            r = model.transcribe(p, language="de")
        except TypeError:
            r = model.transcribe(p)
        t = clean_text(extract_text(r))
        segments = extract_segments(r)
        
        if response_format == "text":
            return t
        else:
            return TranscriptionResponse(
                text=t,
                recording_timestamp=recording_timestamp,
                segments=segments
            )
    finally:
        try:
            os.remove(p)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--proxy-headers", action="store_true", default=True, help="Trust proxy headers (for reverse proxy)")
    a = p.parse_args()
    if a.model:
        os.environ["PARAKEET_MODEL"] = a.model
    
    # Configure uvicorn to trust proxy headers (important for nginx reverse proxy)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=a.port or int(os.getenv("PORT", 8002)),
        proxy_headers=True,  # Trust X-Forwarded-* headers from reverse proxy
        forwarded_allow_ips="*"  # Allow forwarded headers from any IP (adjust for production)
    )

