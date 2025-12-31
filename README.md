# Neuro-Parakeet MLX Server

**OpenAI-Compatible FastAPI Server for Audio Transcription with Parakeet-MLX**

[![CI](https://github.com/riedemannai/parakeet-mlx-server/actions/workflows/ci.yml/badge.svg)](https://github.com/riedemannai/parakeet-mlx-server/actions/workflows/ci.yml)
[![Security Scan](https://github.com/riedemannai/parakeet-mlx-server/actions/workflows/security.yml/badge.svg)](https://github.com/riedemannai/parakeet-mlx-server/actions/workflows/security.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/riedemannai/parakeet-mlx-server)](https://github.com/riedemannai/parakeet-mlx-server/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Model](https://img.shields.io/badge/Model-NeurologyAI%2Fneuro--parakeet--mlx-blue)](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx)
[![Dataset](https://img.shields.io/badge/Dataset-NeurologyAI%2Fneuro--whisper--v1-green)](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1)

> 🍎 **Apple Silicon Only** | 🧠 **Neurology & Neuro-Oncology Speech Recognition** | 🚀 **OpenAI-Compatible API**

---

## About Neuro-Parakeet MLX Server

Neuro-Parakeet MLX Server is an OpenAI-compatible FastAPI server for audio transcription using Parakeet-MLX models. The server is specifically optimized for Apple Silicon (MLX) and provides a fully compatible API to OpenAI's Whisper API.

This server is designed to work with the [NeurologyAI/neuro-parakeet-mlx](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) model, a fine-tuned Parakeet TDT 0.6B model optimized for German neurology and neuro-oncology terminology.

## Features

* 🚀 **OpenAI-Compatible API** - Direct drop-in replacement for OpenAI Whisper API
* 🍎 **Apple Silicon Optimized** - Uses MLX for optimal performance on Mac (M1/M2/M3/M4)
* 📝 **Automatic Transcription** - Supports various audio formats (WAV, MP3, FLAC, M4A, etc.)
* 🧠 **Neurology & Neuro-Oncology Specialized** - Optimized for German neurology and neuro-oncology terminology
* 🌍 **Multilingual** - Supports multiple languages (optimized for German)
* ⚡ **Fast** - Optimized for local inference with MLX
* 🔧 **Easy to Use** - Simple installation and configuration
* 📚 **Interactive API Docs** - Built-in Swagger UI and ReDoc
* 🏥 **Health Monitoring** - Health check endpoint for production use

## Installation

### Prerequisites

* **Apple Silicon Mac (M1/M2/M3/M4) - REQUIRED**
  * This server uses MLX (Apple's machine learning framework) which only works on Apple Silicon
  * **Does NOT work on Linux, Windows, or Intel Macs**
* Python 3.10 or higher
* pip, uv, or conda

### Recommended: Conda Environment Setup

We recommend using a conda environment to manage dependencies and avoid conflicts with other Python packages.

```bash
# 1. Create a new conda environment with Python 3.10+
conda create -n neuro-parakeet-mlx-server python=3.10 -y

# 2. Activate the environment
conda activate neuro-parakeet-mlx-server

# 3. Clone repository
git clone https://github.com/riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 4. Install dependencies (IMPORTANT: Do this step!)
pip install -r requirements.txt

# 5. Start server
./start_server.sh
```

**Important:** Make sure to install dependencies with `pip install -r requirements.txt` after creating the conda environment. The server will not work without this step!

**Note:** The start script (`./start_server.sh`) will automatically activate the conda environment if it exists. You can also manually activate it:
```bash
conda activate neuro-parakeet-mlx-server
./start_server.sh
```

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
./start_server.sh
```

### With UV

```bash
# 1. Clone repository
git clone https://github.com/riedemannai/parakeet-mlx-server.git
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

# With custom model (recommended: NeurologyAI/neuro-parakeet-mlx)
PARAKEET_MODEL=NeurologyAI/neuro-parakeet-mlx ./start_server.sh

# Or directly with Python
python parakeet_server.py --port 8002 --model NeurologyAI/neuro-parakeet-mlx
```

### Available Models

* `NeurologyAI/neuro-parakeet-mlx` (recommended) - Fine-tuned for German neurology and neuro-oncology terminology
* `mlx-community/parakeet-tdt-0.6b-v3` (default) - Base multilingual model

**Model Performance:**
- **NeurologyAI/neuro-parakeet-mlx**: Optimized for German neurology and neuro-oncology terminology
- Trained on [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1) dataset
- See [model README](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) for details

## API

### 📚 Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI Schema**: http://localhost:8002/openapi.json

These endpoints are available when the server is running and provide interactive documentation where you can test the API directly in your browser.

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
  "text": "Transcribed text here...",
  "recording_timestamp": "optional timestamp",
  "segments": [
    {
      "text": "Segment text",
      "start": 0.0,
      "end": 5.2
    }
  ]
}
```

#### GET `/`

Root endpoint - returns server status.

**Request:**

```bash
curl http://localhost:8002/
```

**Response:**

```json
{
  "status": "ok"
}
```

### Supported Audio Formats

* WAV
* MP3
* FLAC
* OGG/Vorbis
* M4A/AAC
* AIFF
* AU

Audio is automatically converted to 16 kHz mono format.

## Configuration

### Environment Variables

* `PORT` - Port for the server (default: 8002)
* `PARAKEET_MODEL` - Model ID or path (default: `mlx-community/parakeet-tdt-0.6b-v3`)

### Command Line Arguments

```bash
python parakeet_server.py --help
```

Options:
  --port PORT     Port for the server (default: 8002)
  --model MODEL   Model ID or path

## Integration

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

### API Documentation

When the server is running, you can access:

- **Swagger UI** (Interactive): http://localhost:8002/docs
- **ReDoc** (Alternative docs): http://localhost:8002/redoc
- **OpenAPI Schema** (JSON): http://localhost:8002/openapi.json

The Swagger UI allows you to test the API directly from your browser.

### Testing

```bash
# Health check
curl http://localhost:8002/

# Test transcription
curl -X POST "http://localhost:8002/v1/audio/transcriptions" \
  -F "file=@test_audio.wav" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de"
```

## Model Information

### Recommended Model: NeurologyAI/neuro-parakeet-mlx

- **Training Dataset**: [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1)
- **Base Model**: [nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Domain**: German neurology and neuro-oncology speech recognition
- **License**: CC-BY-4.0

For detailed model information, see the [model README on Hugging Face](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx).

## Technical Details

* **Framework**: FastAPI
* **Server**: Uvicorn
* **Model Backend**: Parakeet-MLX
* **Audio Processing**: librosa, soundfile
* **API Compatibility**: OpenAI Whisper API v1

## License

MIT License - see LICENSE file

## Acknowledgments

* [NeurologyAI/neuro-parakeet-mlx](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) - Fine-tuned model for German neurology and neuro-oncology terminology
* [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1) - Training dataset
* [NVIDIA Parakeet TDT 0.6B V3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) - Base transcription model by NVIDIA
* [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
* [MLX](https://github.com/ml-explore/mlx) - Machine learning framework for Apple Silicon

---

**Made with ❤️ for the MLX community**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

⭐ [Star on GitHub](https://github.com/riedemannai/parakeet-mlx-server) • 🐛 [Issues](https://github.com/riedemannai/parakeet-mlx-server/issues) • 📖 [Documentation](https://github.com/riedemannai/parakeet-mlx-server#readme) • 📦 [Model on Hugging Face](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx)

