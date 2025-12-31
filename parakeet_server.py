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
import logging
import sys
import shutil
import socket
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from parakeet_mlx import from_pretrained
except ImportError as e:
    from_pretrained = None
    import sys
    error_msg = str(e)
    logger.warning(f"Failed to import parakeet_mlx: {e}")
    
    # Check if it's an MLX library issue (not available on non-Apple Silicon)
    if "libmlx.so" in error_msg or "cannot open shared object file" in error_msg:
        logger.error("=" * 60)
        logger.error("ERROR: MLX library not available!")
        logger.error("This server requires Apple Silicon (M1/M2/M3/M4) Mac.")
        logger.error("MLX (Apple's machine learning framework) is not available on Linux/Windows.")
        logger.error("=" * 60)
    else:
        logger.warning(f"Python path: {sys.path}")
        logger.warning(f"Python executable: {sys.executable}")

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None

model = None
DEFAULT_MODEL = os.getenv("PARAKEET_MODEL", "NeurologyAI/neuro-parakeet-mlx")

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    if sys.version_info < (3, 10):
        logger.error(f"Python 3.10+ required, but found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    return True

def check_disk_space(path, required_gb=5):
    """Check if there's enough disk space (default 5GB for model download)."""
    try:
        stat = shutil.disk_usage(path)
        free_gb = stat.free / (1024**3)
        if free_gb < required_gb:
            logger.warning(f"Low disk space: {free_gb:.2f}GB free, {required_gb}GB recommended for model download")
            return False
        return True
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return True  # Don't fail if we can't check

def check_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            if result == 0:
                logger.error(f"Port {port} is already in use!")
                return False
        return True
    except Exception as e:
        logger.warning(f"Could not check port availability: {e}")
        return True  # Don't fail if we can't check

def check_temp_directory():
    """Check if temp directory is writable."""
    try:
        test_file = tempfile.NamedTemporaryFile(delete=True)
        test_file.close()
        return True
    except Exception as e:
        logger.error(f"Temp directory is not writable: {e}")
        return False

def check_huggingface_cache():
    """Check HuggingFace cache directory."""
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(cache_dir):
        if not os.access(cache_dir, os.W_OK):
            logger.warning(f"HuggingFace cache directory is not writable: {cache_dir}")
            return False
    return True

def validate_system_requirements():
    """Validate system requirements and log warnings."""
    logger.info("Validating system requirements...")
    
    issues = []
    warnings = []
    
    # Check Python version
    if not check_python_version():
        issues.append("Python version < 3.10")
    
    # Check temp directory
    if not check_temp_directory():
        issues.append("Temp directory not writable")
    
    # Check HuggingFace cache
    if not check_huggingface_cache():
        warnings.append("HuggingFace cache may not be writable")
    
    # Check disk space (for model downloads)
    cache_dir = os.path.expanduser("~/.cache")
    if not check_disk_space(cache_dir, required_gb=5):
        warnings.append("Low disk space for model download")
    
    if issues:
        logger.error("=" * 60)
        logger.error("CRITICAL ISSUES FOUND:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.error("=" * 60)
        return False
    
    if warnings:
        logger.warning("=" * 60)
        logger.warning("WARNINGS:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
        logger.warning("=" * 60)
    
    logger.info("System requirements validation passed")
    return True

class TranscriptionResponse(BaseModel):
    text: str
    recording_timestamp: Optional[str] = None
    segments: Optional[List[dict]] = None

def load_model(model_id: Optional[str] = None):
    global model
    if model is None and from_pretrained:
        try:
        model_id = model_id or os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
            logger.info(f"Loading model: {model_id}")
        if "/" in model_id and not os.path.exists(model_id) and snapshot_download:
            try:
                    logger.info(f"Downloading model from HuggingFace (local only)...")
                cache_dir = snapshot_download(repo_id=model_id, repo_type="model", local_files_only=True)
                    model_id = cache_dir
                except Exception as e:
                    logger.warning(f"Local download failed: {e}, trying with network access...")
                cache_dir = snapshot_download(repo_id=model_id, repo_type="model", local_files_only=False)
            model_id = cache_dir
            logger.info(f"Loading model from: {model_id}")
        model = from_pretrained(model_id)
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            model = None
            raise
    elif model is None:
        logger.error("parakeet_mlx.from_pretrained is not available. Please install parakeet-mlx.")
        logger.error("Install with: pip install -r requirements.txt")
        logger.error("Or: pip install parakeet-mlx")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if from_pretrained:
        try:
        load_model()
            if model is None:
                logger.error("Model failed to load during startup!")
        except Exception as e:
            logger.error(f"Error during model loading in lifespan: {e}", exc_info=True)
    else:
        import sys
        import subprocess
        logger.error("=" * 60)
        logger.error("ERROR: parakeet_mlx is not available!")
        logger.error(f"Python executable: {sys.executable}")
        logger.error(f"Python version: {sys.version}")
        
        # Try to check if package is installed and diagnose the issue
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "parakeet-mlx"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Try to import to see the actual error
                import_result = subprocess.run(
                    [sys.executable, "-c", "import parakeet_mlx"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "libmlx.so" in import_result.stderr or "cannot open shared object file" in import_result.stderr:
                    logger.error("Package 'parakeet-mlx' is installed but MLX library is not available!")
                    logger.error("This server requires Apple Silicon (M1/M2/M3/M4) Mac.")
                    logger.error("MLX is Apple's framework and only works on macOS with Apple Silicon.")
                else:
                    logger.error("Package 'parakeet-mlx' is installed but cannot be imported!")
                    logger.error("This might be a Python path or environment issue.")
                    logger.error("Try: pip install --force-reinstall parakeet-mlx")
            else:
                logger.error("Package 'parakeet-mlx' is NOT installed!")
        except Exception as e:
            logger.error(f"Could not check package status: {e}")
        
        logger.error("")
        logger.error("Please install dependencies:")
        logger.error(f"  {sys.executable} -m pip install -r requirements.txt")
        logger.error("Or install directly:")
        logger.error(f"  {sys.executable} -m pip install parakeet-mlx")
        logger.error("=" * 60)
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

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        return response

# Add middlewares in order (security headers, path normalization, then CORS)
app.add_middleware(SecurityHeadersMiddleware)
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

@app.get("/health")
async def health_check():
    """Health check endpoint - returns server and model status."""
    import sys
    import shutil
    
    health_status = {
        "status": "healthy" if model else "unhealthy",
        "model_loaded": model is not None,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "system": sys.platform
    }
    
    # Add disk space info
    try:
        stat = shutil.disk_usage(os.path.expanduser("~"))
        health_status["disk_space_gb"] = round(stat.free / (1024**3), 2)
    except Exception:
        pass
    
    status_code = 200 if model else 503
    return health_status

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
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file size (limit to 100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB")
    
    # Check if file is empty
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty file provided")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        p = tmp.name
    try:
        with open(p, 'wb') as f:
            f.write(file_content)
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
    p.add_argument("--skip-validation", action="store_true", help="Skip system requirements validation")
    a = p.parse_args()
    if a.model:
        os.environ["PARAKEET_MODEL"] = a.model
    
    port = a.port or int(os.getenv("PORT", 8002))
    
    # Validate system requirements
    if not a.skip_validation:
        if not validate_system_requirements():
            logger.error("System requirements validation failed. Use --skip-validation to proceed anyway.")
            sys.exit(1)
        
        # Check port availability
        if not check_port_available(port):
            logger.error(f"Port {port} is already in use. Please choose a different port.")
            sys.exit(1)
    
    # Configure uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )

