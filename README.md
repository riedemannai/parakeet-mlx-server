# Neuro-Parakeet MLX Server

**OpenAI-Compatible FastAPI Server for Audio Transcription with Parakeet-MLX**

[![Model](https://img.shields.io/badge/Model-NeurologyAI%2Fneuro--parakeet--mlx-blue)](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx)
[![Dataset](https://img.shields.io/badge/Dataset-NeurologyAI%2Fneuro--whisper--v1-green)](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## About Neuro-Parakeet MLX Server

Neuro-Parakeet MLX Server is an OpenAI-compatible FastAPI server for audio transcription using Parakeet-MLX models. The server is specifically optimized for Apple Silicon (MLX) and provides a fully compatible API to OpenAI's Whisper API.

This server is designed to work with the [NeurologyAI/neuro-parakeet-mlx](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) model, a fine-tuned Parakeet TDT 0.6B model optimized for German medical/neurological speech recognition.

## Features

* 🚀 **OpenAI-Compatible API** - Direct drop-in replacement for OpenAI Whisper API
* 🍎 **Apple Silicon Optimized** - Uses MLX for optimal performance on Mac (M1/M2/M3/M4)
* 📝 **Automatic Transcription** - Supports various audio formats
* 🏥 **Medical Domain Specialized** - Optimized for German medical terminology
* 🌍 **Multilingual** - Supports multiple languages (optimized for German)
* ⚡ **Fast** - Optimized for local inference
* 🔧 **Easy to Use** - Simple installation and configuration

## Installation

### Prerequisites

* Python 3.10 or higher
* Apple Silicon Mac (M1/M2/M3/M4) or system with MLX support
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

* `NeurologyAI/neuro-parakeet-mlx` (recommended) - Fine-tuned for German medical speech (1.04% WER)
* `mlx-community/parakeet-tdt-0.6b-v3` (default) - Base multilingual model

**Model Performance:**
- **NeurologyAI/neuro-parakeet-mlx**: 1.04% WER on German medical speech (validation set)
- Trained on [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1) dataset
- See [model README](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) for details

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

## Troubleshooting

### Model Not Found

Make sure the model has been downloaded:

```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('NeurologyAI/neuro-parakeet-mlx')"
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

## Model Information

### Recommended Model: NeurologyAI/neuro-parakeet-mlx

- **WER**: 1.04% on German medical speech validation set
- **Training Dataset**: [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1)
- **Base Model**: [nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Domain**: German medical/neurological speech recognition
- **License**: CC-BY-4.0

For detailed model information, see the [model README on Hugging Face](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx).

## Technical Details

* **Framework**: FastAPI
* **Server**: Uvicorn
* **Model Backend**: Parakeet-MLX
* **Audio Processing**: librosa, soundfile
* **API Compatibility**: OpenAI Whisper API v1

## Reverse Proxy Configuration (Nginx)

The server is configured to work behind an nginx reverse proxy. See `nginx_example.conf` for a complete example configuration.

### Quick Nginx Setup

1. **Install nginx** (if not already installed):
   ```bash
   # macOS
   brew install nginx
   
   # Ubuntu/Debian
   sudo apt-get install nginx
   ```

2. **Create nginx configuration**:
   ```bash
   sudo nano /etc/nginx/sites-available/parakeet-server
   ```
   
   Copy the configuration from `nginx_example.conf` and adjust:
   - Server name/IP
   - Port (if different from 8002)
   - SSL certificates (if using HTTPS)

3. **Enable the site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/parakeet-server /etc/nginx/sites-enabled/
   sudo nginx -t  # Test configuration
   sudo systemctl reload nginx  # Reload nginx
   ```

4. **Start the server**:
   ```bash
   ./start_server.sh
   ```

### Important Nginx Settings

- **`proxy_method POST`** - Ensures POST requests are forwarded correctly
- **`client_max_body_size 100M`** - Allows large audio file uploads
- **`proxy_buffering off`** - Prevents buffering issues with file uploads
- **X-Forwarded-* headers** - Properly forwarded for correct URL generation

## License

MIT License - see LICENSE file

## Acknowledgments

* [NeurologyAI/neuro-parakeet-mlx](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx) - Fine-tuned model for German medical speech
* [NeurologyAI/neuro-whisper-v1](https://huggingface.co/datasets/NeurologyAI/neuro-whisper-v1) - Training dataset
* [NVIDIA Parakeet TDT 0.6B V3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) - Base transcription model by NVIDIA
* [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
* [MLX](https://github.com/ml-explore/mlx) - Machine learning framework for Apple Silicon

---

**Made with ❤️ for the MLX community**

⭐ [Star on GitHub](https://github.com/riedemannai/parakeet-mlx-server) • 🐛 [Issues](https://github.com/riedemannai/parakeet-mlx-server/issues) • 📦 [Model on Hugging Face](https://huggingface.co/NeurologyAI/neuro-parakeet-mlx)

