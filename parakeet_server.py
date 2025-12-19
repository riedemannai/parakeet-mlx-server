#!/usr/bin/env python3
"""
OpenAI-compatible FastAPI server for audio transcription using parakeet-mlx.
Compatible with open-webui and other OpenAI API clients.
Uses parakeet-mlx models optimized for Apple Silicon (MLX).
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
import re
import warnings
import tempfile
import argparse
import io

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import audio processing libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not installed. Audio preprocessing may not work properly. Install with: pip install librosa")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("soundfile not installed. Audio preprocessing may not work properly. Install with: pip install soundfile")

# Try to import parakeet-mlx
try:
    from parakeet_mlx import from_pretrained
    PARAKEET_MLX_AVAILABLE = True
except ImportError:
    PARAKEET_MLX_AVAILABLE = False
    logger.error("parakeet-mlx not installed. Please run: pip install -U parakeet-mlx")

# Try to import huggingface_hub for downloading models
try:
    from huggingface_hub import snapshot_download
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    logger.warning("huggingface_hub not installed. HF model downloads may not work.")

# Initialize FastAPI app
app = FastAPI(
    title="Parakeet MLX OpenAI-Compatible API",
    description="OpenAI-compatible API for audio transcription using parakeet-mlx",
    version="1.0.0"
)

# Middleware to normalize paths (remove double slashes)
class NormalizePathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Normalize path by replacing double slashes with single slash
        path = request.url.path
        normalized_path = re.sub(r'/+', '/', path)
        if normalized_path != path:
            # Create new request with normalized path
            new_scope = dict(request.scope)
            new_scope["path"] = normalized_path
            new_scope["path_info"] = normalized_path
            request = Request(new_scope)
        response = await call_next(request)
        return response

# Add path normalization middleware (before CORS)
app.add_middleware(NormalizePathMiddleware)

# CORS middleware for open-webui compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model
model = None

# Default model configuration
DEFAULT_MODEL = os.getenv("PARAKEET_MODEL", "mlx-community/parakeet-tdt-0.6b-v3")

# Supported audio MIME types (formats that librosa can decode)
SUPPORTED_MIME_TYPES = {
    # WAV formats
    "audio/wav", "audio/wave", "audio/x-wav", "audio/vnd.wave",
    # MP3 formats
    "audio/mpeg", "audio/mp3", "audio/x-mpeg", "audio/x-mpeg-3",
    # FLAC formats
    "audio/flac", "audio/x-flac",
    # OGG/Vorbis formats
    "audio/ogg", "audio/vorbis", "audio/opus",
    # M4A/AAC formats
    "audio/mp4", "audio/m4a", "audio/x-m4a", "audio/aac",
    # Other formats
    "audio/aiff", "audio/x-aiff",
    "audio/basic", "audio/au", "audio/x-au",
    "audio/wma", "audio/x-ms-wma",
    # Generic fallbacks
    "audio/*", "application/octet-stream"
}

def is_german_model(model_id: str) -> bool:
    """Check if the model is German-specific."""
    model_id_lower = model_id.lower()
    return "german" in model_id_lower or "neuro-german" in model_id_lower

# Response models
class TranscriptionResponse(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    text: str

def load_model(model_id: Optional[str] = None):
    """Load the parakeet-mlx model."""
    global model
    if model is None and PARAKEET_MLX_AVAILABLE:
        if model_id is None:
            model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
        print("\n" + "=" * 80)
        print("Loading Parakeet MLX Model")
        print("=" * 80)
        print(f"Model: {model_id}")
        print("=" * 80)
        
        # Check if model_id is a Hugging Face repository ID (contains /)
        # If so, check cache first, then download if needed
        if "/" in model_id and not os.path.exists(model_id) and HF_HUB_AVAILABLE:
            try:
                from pathlib import Path
                import glob
                
                # First, try to find existing cache
                cache_dir = None
                try:
                    cache_dir = snapshot_download(
                        repo_id=model_id,
                        repo_type="model",
                        local_files_only=True  # Only check cache, don't download
                    )
                    logger.info(f"✓ Model found in cache: {cache_dir}")
                    print(f"✓ Model found in cache")
                except Exception:
                    # Not in cache, need to download
                    pass
                
                # If not in cache, download it
                if cache_dir is None:
                    logger.info(f"Downloading model from Hugging Face: {model_id}")
                    print(f"📥 Downloading from Hugging Face...")
                    
                    # Download model to cache
                    cache_dir = snapshot_download(
                        repo_id=model_id,
                        repo_type="model",
                        local_files_only=False
                    )
                    
                    logger.info(f"✓ Model downloaded to: {cache_dir}")
                    print(f"✓ Model downloaded to cache")
                
                # Verify config.json exists
                config_path = os.path.join(cache_dir, "config.json")
                if not os.path.exists(config_path):
                    raise FileNotFoundError(f"config.json not found in downloaded model at {config_path}. The model may be incomplete.")
                
                # Update model_id to use the local cache path
                model_id = cache_dir
                
                # Fix for models with non-standard safetensors filename
                # Check which safetensors file exists and will be used
                model_safetensors = os.path.join(cache_dir, "model.safetensors")
                custom_safetensors = os.path.join(cache_dir, "parakeet_neuro_german-MLX.safetensors")
                
                # Determine which file will be used
                model_exists = os.path.exists(model_safetensors)
                custom_exists = os.path.exists(custom_safetensors)
                
                if model_exists and custom_exists:
                    # Both exist - check if they're the same file (symlink) or different
                    if os.path.islink(model_safetensors):
                        target = os.readlink(model_safetensors)
                        # Resolve to absolute path to see the actual blob
                        abs_target = os.path.abspath(os.path.join(cache_dir, target))
                        model_size = os.path.getsize(abs_target) if os.path.exists(abs_target) else os.path.getsize(model_safetensors)
                        blob_hash = os.path.basename(abs_target) if os.path.exists(abs_target) else "unknown"
                        logger.info(f"model.safetensors is a symlink -> {target} (blob: {blob_hash})")
                        print(f"ℹ️  Using model.safetensors (symlink to blob: {blob_hash[:16]}...)")
                        print(f"   Size: {model_size / (1024**3):.2f} GB")
                        
                        # Check if custom file points to different blob
                        if os.path.islink(custom_safetensors):
                            custom_target = os.readlink(custom_safetensors)
                            custom_abs_target = os.path.abspath(os.path.join(cache_dir, custom_target))
                            custom_blob_hash = os.path.basename(custom_abs_target) if os.path.exists(custom_abs_target) else "unknown"
                            if blob_hash != custom_blob_hash:
                                logger.info(f"parakeet_neuro_german-MLX.safetensors points to different blob: {custom_blob_hash}")
                                print(f"   Note: parakeet_neuro_german-MLX.safetensors points to different blob: {custom_blob_hash[:16]}...")
                    else:
                        # Check file sizes to see if they're the same
                        model_size = os.path.getsize(model_safetensors)
                        custom_size = os.path.getsize(custom_safetensors)
                        if model_size == custom_size:
                            logger.info(f"Both files exist with same size ({model_size} bytes). Using model.safetensors")
                            print(f"ℹ️  Using model.safetensors ({model_size / (1024**3):.2f} GB)")
                        else:
                            logger.warning(f"Both files exist but different sizes: model.safetensors={model_size}, custom={custom_size}")
                            print(f"⚠️  Both files exist with different sizes. Using model.safetensors")
                elif model_exists:
                    model_size = os.path.getsize(model_safetensors)
                    logger.info(f"Using model.safetensors ({model_size} bytes)")
                    print(f"ℹ️  Using model.safetensors ({model_size / (1024**3):.2f} GB)")
                elif custom_exists:
                    # Create symlink if model.safetensors doesn't exist but custom name does
                    logger.info(f"Creating symlink: {model_safetensors} -> {custom_safetensors}")
                    os.symlink("parakeet_neuro_german-MLX.safetensors", model_safetensors)
                    custom_size = os.path.getsize(custom_safetensors)
                    print(f"✓ Created symlink: model.safetensors -> parakeet_neuro_german-MLX.safetensors")
                    print(f"ℹ️  Using parakeet_neuro_german-MLX.safetensors ({custom_size / (1024**3):.2f} GB) via symlink")
                else:
                    logger.warning(f"Neither model.safetensors nor parakeet_neuro_german-MLX.safetensors found in {cache_dir}")
                    print(f"⚠️  Warning: No safetensors file found in cache directory")
                    
            except Exception as e:
                logger.error(f"Could not download from HF: {e}")
                raise RuntimeError(f"Failed to download model from Hugging Face: {e}. Make sure huggingface_hub is installed: pip install huggingface_hub")
        elif "/" in model_id and not HF_HUB_AVAILABLE:
            raise RuntimeError(f"Model ID '{model_id}' appears to be a Hugging Face repository, but huggingface_hub is not installed. Please install it: pip install huggingface_hub")
        else:
            # Fix for models with non-standard safetensors filename (for local paths)
            if "parakeet-neuro" in model_id or "parakeet-neuro-german-mlx" in model_id:
                try:
                    from pathlib import Path
                    import glob
                    # Find the cache directory for this model
                    cache_pattern = os.path.expanduser("~/.cache/huggingface/hub/models--*--parakeet-neuro-whisper-v2-mlx/snapshots/*")
                    cache_dirs = glob.glob(cache_pattern)
                    if not cache_dirs:
                        # Try alternative pattern
                        cache_pattern = os.path.expanduser("~/.cache/huggingface/hub/models--*--parakeet-neuro-german-mlx/snapshots/*")
                        cache_dirs = glob.glob(cache_pattern)
                    if cache_dirs:
                        cache_dir = cache_dirs[0]
                        model_safetensors = os.path.join(cache_dir, "model.safetensors")
                        custom_safetensors = os.path.join(cache_dir, "parakeet_neuro_german-MLX.safetensors")
                        
                        # Create symlink if model.safetensors doesn't exist but custom name does
                        if not os.path.exists(model_safetensors) and os.path.exists(custom_safetensors):
                            logger.info(f"Creating symlink: {model_safetensors} -> {custom_safetensors}")
                            os.symlink("parakeet_neuro_german-MLX.safetensors", model_safetensors)
                            print(f"✓ Created symlink for model.safetensors")
                except Exception as e:
                    logger.warning(f"Could not create symlink (may already exist): {e}")
        
        try:
            logger.info(f"Loading parakeet-mlx model: {model_id}")
            # Verify that if model_id is a local path, it exists and has required files
            if os.path.exists(model_id) and os.path.isdir(model_id):
                config_path = os.path.join(model_id, "config.json")
                if not os.path.exists(config_path):
                    logger.warning(f"config.json not found in {model_id}, but continuing...")
                logger.info(f"Using local model directory: {model_id}")
            
            # If model_id is a local cache directory path, from_pretrained should use it directly
            # without re-downloading. If it's still a HuggingFace repo ID, it will download.
            # Since we've already handled the download above, model_id should be a local path now.
            model = from_pretrained(model_id)
            logger.info(f"✓ Model loaded successfully: {model_id}")
            print(f"✓ SUCCESS: Model loaded: {model_id}")
            print("=" * 80 + "\n")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"✗ ERROR: Failed to load model: {e}")
            print("=" * 80 + "\n")
            raise
    elif not PARAKEET_MLX_AVAILABLE:
        raise RuntimeError("parakeet-mlx is not installed. Please run: pip install -U parakeet-mlx")

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    if PARAKEET_MLX_AVAILABLE:
        # Get model from environment variable (set by CLI args in __main__)
        model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
        load_model(model_id)
    else:
        logger.error("parakeet-mlx not available. Server will not function properly.")

@app.get("/")
async def root():
    """Health check endpoint."""
    model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
    return {
        "status": "ok" if (model is not None and PARAKEET_MLX_AVAILABLE) else "error",
        "model": model_id,
        "parakeet_mlx_available": PARAKEET_MLX_AVAILABLE
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
    model_name = model_id.split("/")[-1] if "/" in model_id else model_id
    return {
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 1700000000,
                "owned_by": "custom"
            }
        ],
        "object": "list"
    }

@app.post("/v1/audio/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    file: UploadFile = File(...),
    model_name: str = Form("parakeet-tdt-0.6b-v3", alias="model"),
    language: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    response_format: Optional[str] = Form("json"),
    temperature: Optional[float] = Form(None)
):
    """
    Create transcription from audio file (OpenAI-compatible endpoint).
    
    Args:
        file: Audio file to transcribe
        model_name: Model to use (for compatibility, actual model is from PARAKEET_MODEL env var)
        language: Language code (optional, parakeet-mlx may auto-detect)
        prompt: Optional prompt for context (may not be supported by parakeet-mlx)
        response_format: Response format (json, text, etc.)
        temperature: Temperature for generation (may not be supported by parakeet-mlx)
    
    Returns:
        TranscriptionResponse with transcribed text
    """
    if not PARAKEET_MLX_AVAILABLE:
        raise HTTPException(status_code=500, detail="parakeet-mlx is not installed. Please run: pip install -U parakeet-mlx")
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Validate MIME type
        content_type = file.content_type or ""
        # Check if MIME type is supported (allow generic types as fallback)
        if content_type and not any(
            content_type.startswith(mime.replace("*", "")) if "*" in mime else content_type == mime
            for mime in SUPPORTED_MIME_TYPES
        ):
            # Check file extension as fallback
            filename = file.filename or ""
            file_ext = os.path.splitext(filename)[1].lower()
            supported_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".aiff", ".au", ".wma"}
            if file_ext not in supported_extensions and content_type not in {"", "application/octet-stream"}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported audio format. Content-Type: {content_type}. Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, AIFF, AU, WMA"
                )
        
        # Determine language - force German for German-specific models
        model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
        if is_german_model(model_id):
            language = "de"
            logger.info(f"German model detected ({model_id}), forcing language to 'de'")
        elif language is None:
            logger.info("No language specified, model will auto-detect")
        
        # Read audio file
        audio_bytes = await file.read()
        logger.info(f"Processing audio file: {file.filename}, size: {len(audio_bytes)} bytes, content-type: {content_type}")
        
        # Create a temporary file to save the audio
        # parakeet-mlx expects a file path, not bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
        
        audio_duration = None
        
        # If librosa and soundfile are available, preprocess audio for better results
        if LIBROSA_AVAILABLE and SOUNDFILE_AVAILABLE:
            try:
                # Load and preprocess audio using librosa
                # This ensures proper format conversion (16kHz mono) and handles various input formats
                audio_file = io.BytesIO(audio_bytes)
                audio, sr = librosa.load(audio_file, sr=16000, mono=True)
                audio_duration = len(audio) / sr
                logger.info(f"Audio loaded: duration={audio_duration:.2f}s, sample_rate={sr}Hz, channels=mono")
                
                # Log warning for very long audio files (parakeet-mlx might have limits)
                if audio_duration > 60.0:
                    logger.warning(f"Audio file is long ({audio_duration:.2f}s). parakeet-mlx may have issues with very long files.")
                elif audio_duration > 30.0:
                    logger.info(f"Audio file is moderately long ({audio_duration:.2f}s). Processing...")
                
                # Save audio as WAV file (16kHz, mono, 16-bit PCM)
                sf.write(temp_file_path, audio, sr, format='WAV', subtype='PCM_16')
                logger.info(f"Audio preprocessed and saved to temporary file: {temp_file_path}")
                
            except Exception as e:
                logger.warning(f"Error preprocessing audio with librosa/soundfile: {e}. Falling back to direct file write.")
                # Fallback: write audio bytes directly (may not work for all formats)
                with open(temp_file_path, 'wb') as f:
                    f.write(audio_bytes)
                logger.info(f"Audio saved directly to temporary file (no preprocessing): {temp_file_path}")
        else:
            # Fallback: write audio bytes directly
            with open(temp_file_path, 'wb') as f:
                f.write(audio_bytes)
            logger.info(f"Audio saved directly to temporary file (librosa/soundfile not available): {temp_file_path}")
            logger.warning("Audio preprocessing not available. Install librosa and soundfile for better results: pip install librosa soundfile")
        
        try:
            # Transcribe using parakeet-mlx
            # The transcribe method may return different formats depending on the version
            duration_str = f" (duration: {audio_duration:.2f}s)" if audio_duration else ""
            lang_str = f", language: {language}" if language else ""
            logger.info(f"Transcribing audio with parakeet-mlx model{duration_str}{lang_str}")
            
            # Try to pass language parameter if specified (may not be supported by all parakeet-mlx versions)
            try:
                if language:
                    result = model.transcribe(temp_file_path, language=language)
                else:
                    result = model.transcribe(temp_file_path)
            except TypeError:
                # Language parameter not supported, fall back to no language parameter
                logger.debug("Language parameter not supported by this parakeet-mlx version, using auto-detect")
                result = model.transcribe(temp_file_path)
            
            # Handle different return types from parakeet-mlx
            # Log the raw result type to help debug
            logger.debug(f"Raw transcription result type: {type(result)}, value: {result}")
            
            if hasattr(result, 'text'):
                transcription = result.text
                # Check if result has segments or chunks (some parakeet-mlx versions return structured data)
                if hasattr(result, 'segments') and result.segments:
                    logger.info(f"Found {len(result.segments)} segments in transcription result")
                    # Combine all segments if available
                    segment_texts = []
                    for seg in result.segments:
                        if hasattr(seg, 'text'):
                            segment_texts.append(seg.text)
                        elif isinstance(seg, dict) and 'text' in seg:
                            segment_texts.append(seg['text'])
                    if segment_texts:
                        transcription = ' '.join(segment_texts)
                        logger.info(f"Combined {len(segment_texts)} segments into full transcription")
            elif isinstance(result, dict):
                transcription = result.get('text', '')
                # Check for segments in dict format
                if 'segments' in result and result['segments']:
                    logger.info(f"Found {len(result['segments'])} segments in transcription dict")
                    segment_texts = [seg.get('text', '') if isinstance(seg, dict) else str(seg) 
                                   for seg in result['segments']]
                    if any(segment_texts):
                        transcription = ' '.join(segment_texts)
                        logger.info(f"Combined {len(segment_texts)} segments from dict into full transcription")
                if not transcription:
                    transcription = str(result)
            elif isinstance(result, str):
                transcription = result
            else:
                transcription = str(result)
            
            # Normalize transcription: preserve all words but clean up whitespace
            # Only strip leading/trailing whitespace, preserve internal spacing and all words
            if transcription:
                # Store original for logging
                original_transcription = transcription
                # Remove leading/trailing whitespace but preserve the actual text content
                transcription = transcription.strip()
                # Normalize multiple spaces/newlines to single spaces (but preserve word boundaries)
                # This handles cases where there might be newlines between sentences
                transcription = re.sub(r'\s+', ' ', transcription)
                
                # Log if normalization changed anything significant
                if len(transcription) != len(original_transcription.strip()):
                    logger.debug(f"Normalization changed transcription length: {len(original_transcription)} -> {len(transcription)}")
            
            # Log transcription length and full content to help debug issues
            transcription_length = len(transcription) if transcription else 0
            word_count = len(transcription.split()) if transcription else 0
            logger.info(f"Transcription successful: length={transcription_length} chars, words={word_count}, preview: {transcription[:150] if transcription else 'EMPTY'}...")
            logger.debug(f"Full transcription: {transcription}")
            
            # Warn if transcription seems incomplete (very short for long audio)
            # Estimate: roughly 10-15 chars per second of speech is reasonable for German
            if audio_duration and transcription:
                estimated_chars = int(audio_duration * 12)  # Conservative estimate: 12 chars/sec
                if transcription_length < estimated_chars * 0.3:  # Less than 30% of expected
                    logger.warning(
                        f"Transcription seems incomplete: {transcription_length} chars for {audio_duration:.2f}s audio "
                        f"(expected ~{estimated_chars} chars). This might indicate partial transcription or early stopping."
                    )
                elif transcription_length < estimated_chars * 0.5:  # Less than 50% of expected
                    logger.info(
                        f"Transcription is shorter than expected: {transcription_length} chars for {audio_duration:.2f}s audio "
                        f"(expected ~{estimated_chars} chars). This might be normal for speech with pauses."
                    )
            
            # Ensure transcription ends properly (no trailing issues that might cause OpenWebUI truncation)
            # Add a trailing space if the transcription doesn't end with punctuation or space
            # This helps OpenWebUI's concatenation logic handle multiple transcriptions better
            if transcription and transcription.strip():
                # Only add trailing space if it doesn't already end with whitespace or punctuation
                if not transcription.rstrip().endswith(('.', '!', '?', ',', ';', ':', ' ')):
                    transcription = transcription.rstrip() + ' '
                    logger.debug("Added trailing space to transcription to help with concatenation")
            
            # Log the exact response being sent (for debugging OpenWebUI truncation issues)
            logger.info(f"Sending transcription response: {len(transcription)} chars, last 50 chars: '...{transcription[-50:] if len(transcription) > 50 else transcription}'")
            
            if response_format == "text":
                return transcription
            else:
                # Create response and log it to ensure it's complete
                response = TranscriptionResponse(text=transcription)
                logger.debug(f"Response object created with text length: {len(response.text)}")
                return response
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {temp_file_path}: {e}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/v1/audio/translations", response_model=TranslationResponse)
async def create_translation(
    file: UploadFile = File(...),
    model_name: str = Form("parakeet-tdt-0.6b-v3", alias="model"),
    prompt: Optional[str] = Form(None),
    response_format: Optional[str] = Form("json"),
    temperature: Optional[float] = Form(None)
):
    """
    Create translation from audio file (OpenAI-compatible endpoint).
    
    Note: Parakeet-mlx is primarily for transcription. This endpoint behaves the same as /transcriptions.
    
    Args:
        file: Audio file to transcribe
        model_name: Model to use
        prompt: Optional prompt for context
        response_format: Response format (json, text, etc.)
        temperature: Temperature for generation
    
    Returns:
        TranslationResponse with transcribed text
    """
    # For parakeet-mlx, translation is the same as transcription
    # Check if we should force German for German models
    model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
    if is_german_model(model_id):
        language = "de"
        logger.info(f"German model detected ({model_id}), forcing language to 'de' for translation")
    
    # Just call the transcription endpoint logic
    return await create_transcription(
        file=file,
        model_name=model_name,
        language=language,
        prompt=prompt,
        response_format=response_format,
        temperature=temperature
    )

if __name__ == "__main__":
    import uvicorn
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Parakeet MLX OpenAI-Compatible API Server")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Model to use (default: {DEFAULT_MODEL} or PARAKEET_MODEL env var)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to run the server on (default: 8002 or PORT env var)"
    )
    args = parser.parse_args()
    
    # Set model from CLI argument if provided
    if args.model:
        os.environ["PARAKEET_MODEL"] = args.model
        logger.info(f"Using model from CLI argument: {args.model}")
    
    # Get port from CLI argument, environment variable, or default
    port = args.port if args.port is not None else int(os.getenv("PORT", 8002))
    
    # Get the model that will be used
    model_id = os.getenv("PARAKEET_MODEL", DEFAULT_MODEL)
    
    logger.info(f"Starting OpenAI-compatible Parakeet MLX API server on port {port}")
    logger.info(f"Model: {model_id}")
    uvicorn.run(app, host="0.0.0.0", port=port)

