#!/bin/bash
# Start Neuro-Parakeet MLX Server

PORT=${PORT:-8002}
MODEL=${PARAKEET_MODEL:-mlx-community/parakeet-tdt-0.6b-v3}

echo "Starting Neuro-Parakeet MLX Server..."
echo "  Port: $PORT"
echo "  Model: $MODEL"
echo ""

export PARAKEET_MODEL="$MODEL"
python3 parakeet_server.py --port "$PORT" --model "$MODEL"

