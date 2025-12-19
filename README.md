# Parakeet MLX Server

<div align="center">

**OpenAI-kompatibler FastAPI Server für Audio-Transkription mit Parakeet-MLX**

[Features](#features) • [Installation](#installation) • [Verwendung](#verwendung) • [API](#api)

</div>

---

## Über Parakeet MLX Server

Parakeet MLX Server ist ein OpenAI-kompatibler FastAPI-Server für Audio-Transkription, der [Parakeet-MLX](https://github.com/mlx-community/parakeet) Modelle verwendet. Der Server ist speziell für Apple Silicon (MLX) optimiert und bietet eine vollständig kompatible API zu OpenAI's Whisper API.

## Features

- 🚀 **OpenAI-kompatible API** - Direkter Drop-in-Ersatz für OpenAI Whisper API
- 🍎 **Apple Silicon optimiert** - Nutzt MLX für optimale Performance auf Mac
- 📝 **Automatische Transkription** - Unterstützt verschiedene Audio-Formate
- 🌍 **Mehrsprachig** - Unterstützt verschiedene Sprachen (inkl. Deutsch)
- ⚡ **Schnell** - Optimiert für lokale Inferenz
- 🔧 **Einfach zu verwenden** - Einfache Installation und Konfiguration

## Installation

### Voraussetzungen

- Python 3.10 oder höher
- Apple Silicon Mac (M1/M2/M3) oder System mit MLX-Unterstützung
- pip oder uv

### Schnellstart

```bash
# 1. Repository klonen
git clone git@github.com:riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Server starten
./start_server.sh
```

### Mit UV

```bash
# 1. Repository klonen
git clone git@github.com:riedemannai/parakeet-mlx-server.git
cd parakeet-mlx-server

# 2. Mit UV installieren
uv pip install -r requirements.txt

# 3. Server starten
python parakeet_server.py
```

## Verwendung

### Server starten

```bash
# Standard (Port 8002, Standard-Model)
./start_server.sh

# Mit benutzerdefiniertem Port
PORT=8080 ./start_server.sh

# Mit benutzerdefiniertem Model
PARAKEET_MODEL=mlx-community/parakeet-tdt-0.6b-v3 ./start_server.sh

# Oder direkt mit Python
python parakeet_server.py --port 8002 --model mlx-community/parakeet-tdt-0.6b-v3
```

### Verfügbare Modelle

- `mlx-community/parakeet-tdt-0.6b-v3` (Standard)
- `mlx-community/parakeet-neuro-german-mlx` (Deutsch)
- Weitere Modelle von [MLX Community](https://huggingface.co/mlx-community)

## API

### OpenAI-kompatible Endpoints

#### POST `/v1/audio/transcriptions`

Transkribiert Audio zu Text.

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
  "text": "Transkribierter Text hier..."
}
```

#### GET `/v1/models`

Listet verfügbare Modelle.

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

Health Check Endpoint.

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

### Unterstützte Audio-Formate

- WAV
- MP3
- FLAC
- OGG/Vorbis
- M4A/AAC
- AIFF
- AU

## Konfiguration

### Umgebungsvariablen

- `PORT` - Port für den Server (Standard: 8002)
- `PARAKEET_MODEL` - Model-ID oder Pfad (Standard: mlx-community/parakeet-tdt-0.6b-v3)

### Kommandozeilen-Argumente

```bash
python parakeet_server.py --help

Options:
  --port PORT     Port für den Server (Standard: 8002)
  --model MODEL   Model-ID oder Pfad
```

## Integration

### Mit RemedyScribe

Der Server kann direkt mit [RemedyScribe](https://github.com/riedemannai/remedy-scribe) verwendet werden:

```bash
# Terminal 1: Starte Parakeet Server
./start_server.sh

# Terminal 2: Starte RemedyScribe Web-App
cd ../remedy-scribe
./start_remedy_scribe_simple.sh
```

### Mit OpenAI-kompatiblen Clients

Der Server ist vollständig kompatibel mit OpenAI-kompatiblen Clients:

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

## Entwicklung

### Lokale Entwicklung

```bash
# Mit Hot-Reload
uvicorn parakeet_server:app --reload --port 8002
```

### Tests

```bash
# Health Check
curl http://localhost:8002/health

# Modelle auflisten
curl http://localhost:8002/v1/models

# Transkription testen
curl -X POST "http://localhost:8002/v1/audio/transcriptions" \
  -F "file=@test_audio.wav" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de"
```

## Fehlerbehebung

### Model nicht gefunden

Stellen Sie sicher, dass das Model heruntergeladen wurde:
```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/parakeet-tdt-0.6b-v3')"
```

### Port bereits belegt

Verwenden Sie einen anderen Port:
```bash
PORT=8080 ./start_server.sh
```

### Parakeet-MLX nicht installiert

```bash
pip install -U parakeet-mlx
```

## Technische Details

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Model-Backend**: Parakeet-MLX
- **Audio-Verarbeitung**: librosa, soundfile
- **API-Kompatibilität**: OpenAI Whisper API v1

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei

## Danksagungen

- [Parakeet-MLX](https://github.com/mlx-community/parakeet) - MLX-optimierte Transkriptions-Modelle
- [FastAPI](https://fastapi.tiangolo.com/) - Modernes Web-Framework
- [MLX](https://github.com/ml-explore/mlx) - Machine Learning Framework für Apple Silicon

---

<div align="center">

**Made with ❤️ for the MLX community**

[⭐ Star auf GitHub](https://github.com/riedemannai/parakeet-mlx-server) • [🐛 Issues](https://github.com/riedemannai/parakeet-mlx-server/issues)

</div>

