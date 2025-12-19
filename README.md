# Parakeet MLX Server

<div align="center">

**OpenAI-Compatible FastAPI Server for Audio Transcription with Parakeet-MLX**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API](#api)

</div>

---

## About Parakeet MLX Server

Parakeet MLX Server is an OpenAI-compatible FastAPI server for audio transcription using [Parakeet-MLX](https://github.com/mlx-community/parakeet) models. The server is specifically optimized for Apple Silicon (MLX) and provides a fully compatible API to OpenAI's Whisper API.

## Features

- 🚀 **OpenAI-Compatible API** - Direct drop-in replacement for OpenAI Whisper API
- 🍎 **Apple Silicon Optimized** - Uses MLX for optimal performance on Mac
- 📝 **Automatic Transcription** - Supports various audio formats
- 🌍 **Multilingual** - Supports multiple languages (including German)
- ⚡ **Fast** - Optimized for local inference
- 🔧 **Easy to Use** - Simple installation and configuration

## Installation

### Prerequisites

- Python 3.10 or higher
- Apple Silicon Mac (M1/M2/M3) or system with MLX support
- pip or uv

### Quick Start

```bash
# 1. Clone repository
git clone git@github.com:riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
./start_server.sh
```

### With UV

```bash
# 1. Clone repository
git clone git@github.com:riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 2. Install with UV
uv pip install -r requirements.txt

# 3. Start server
python parakeet_server.py
```

## Usage

### Start Server

```bash
# Default (Port 8002, default model)
./start_server.sh

# With custom port
PORT=8080 ./start_server.sh

# With custom model
PARAKEET_MODEL=mlx-community/parakeet-tdt-0.6b-v3 ./start_server.sh

# Or directly with Python
python parakeet_server.py --port 8002 --model mlx-community/parakeet-tdt-0.6b-v3
```

### Available Models

- `mlx-community/parakeet-tdt-0.6b-v3` (default)
- More models from [MLX Community](https://huggingface.co/mlx-community)

## API

### OpenAI-Compatible Endpoints

#### POST `/v1/audio/transcriptions`

Transcribes audio to text.

**Request:**
```bash
curl -X POST "http://localhost:8002/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de" \
  -F "response_format=json"
```

**Response:**
```json
{
  "text": "Transcribed text here..."
}
```

#### GET `/v1/models`

Lists available models.

**Request:**
```bash
curl http://localhost:8002/v1/models
```

**Response:**
```json
{
  "data": [
    {
      "id": "parakeet-tdt-0.6b-v3",
      "object": "model",
      "created": 1700000000,
      "owned_by": "custom"
    }
  ],
  "object": "list"
}
```

#### GET `/health`

Health check endpoint.

**Request:**
```bash
curl http://localhost:8002/health
```

**Response:**
```json
{
  "status": "ok",
  "model": "mlx-community/parakeet-tdt-0.6b-v3",
  "parakeet_mlx_available": true
}
```

### Supported Audio Formats

- WAV
- MP3
- FLAC
- OGG/Vorbis
- M4A/AAC
- AIFF
- AU

## Configuration

### Environment Variables

- `PORT` - Port for the server (default: 8002)
- `PARAKEET_MODEL` - Model ID or path (default: mlx-community/parakeet-tdt-0.6b-v3)

### Command Line Arguments

```bash
python parakeet_server.py --help

Options:
  --port PORT     Port for the server (default: 8002)
  --model MODEL   Model ID or path
```

## Integration

### With RemedyScribe

The server can be used directly with [RemedyScribe](https://github.com/riedemannai/remedy-scribe):

```bash
# Terminal 1: Start Parakeet Server
./start_server.sh

# Terminal 2: Start RemedyScribe Web App
cd ../remedy-scribe
./start_remedy_scribe_simple.sh
```

### With OpenAI-Compatible Clients

The server is fully compatible with OpenAI-compatible clients:

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8002/v1",
    api_key="not-needed"
)

with open("audio.wav", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="parakeet-tdt-0.6b-v3",
        file=audio_file,
        language="de"
    )

print(transcript.text)
```

## Development

### Local Development

```bash
# With hot-reload
uvicorn parakeet_server:app --reload --port 8002
```

### Testing

```bash
# Health check
curl http://localhost:8002/health

# List models
curl http://localhost:8002/v1/models

# Test transcription
curl -X POST "http://localhost:8002/v1/audio/transcriptions" \
  -F "file=@test_audio.wav" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de"
```

## Troubleshooting

### Model Not Found

Make sure the model has been downloaded:
```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/parakeet-tdt-0.6b-v3')"
```

### Port Already in Use

Use a different port:
```bash
PORT=8080 ./start_server.sh
```

### Parakeet-MLX Not Installed

```bash
pip install -U parakeet-mlx
```

## Technical Details

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Model Backend**: Parakeet-MLX
- **Audio Processing**: librosa, soundfile
- **API Compatibility**: OpenAI Whisper API v1

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- [NVIDIA Parakeet TDT 0.6B V3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) - Base transcription model by NVIDIA
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [MLX](https://github.com/ml-explore/mlx) - Machine learning framework for Apple Silicon

---

<div align="center">

**Made with ❤️ for the MLX community**

[⭐ Star on GitHub](https://github.com/riedemannai/parakeet-mlx-server) • [🐛 Issues](https://github.com/riedemannai/parakeet-mlx-server/issues)

</div>
