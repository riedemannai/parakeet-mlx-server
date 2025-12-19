#!/bin/bash
# Start-Skript für Parakeet MLX Server

set -e

PORT=${PORT:-8002}
MODEL=${PARAKEET_MODEL:-mlx-community/parakeet-tdt-0.6b-v3}

echo "🚀 Starte Parakeet MLX Server..."
echo "📡 Port: $PORT"
echo "🤖 Model: $MODEL"
echo ""

# Prüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 ist nicht installiert."
    exit 1
fi

# Installiere Abhängigkeiten falls nötig
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installiere Abhängigkeiten..."
    pip install -q -r requirements.txt
fi

# Starte Server
export PARAKEET_MODEL="$MODEL"
python3 parakeet_server.py --port "$PORT"
