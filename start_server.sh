#!/bin/bash
# Start Neuro-Parakeet MLX Server

PORT=${PORT:-8002}
MODEL=${PARAKEET_MODEL:-NeurologyAI/neuro-parakeet-mlx}

echo "Starting Neuro-Parakeet MLX Server..."
echo "  Port: $PORT"
echo "  Model: $MODEL"
echo ""

# Activate conda environment if available
if command -v conda &> /dev/null; then
    # Initialize conda for bash
    eval "$(conda shell.bash hook)"
    # Activate the environment if it exists
    if conda env list | grep -q "neuro-parakeet-mlx-server"; then
        conda activate neuro-parakeet-mlx-server
        echo "  Using conda environment: neuro-parakeet-mlx-server"
    fi
fi

export PARAKEET_MODEL="$MODEL"
python parakeet_server.py --port "$PORT" --model "$MODEL"

