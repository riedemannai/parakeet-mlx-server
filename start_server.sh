#!/bin/bash
# Start Neuro-Parakeet MLX Server

PORT=${PORT:-8002}
MODEL=${PARAKEET_MODEL:-NeurologyAI/neuro-parakeet-mlx}
API_KEY=${API_KEY:-""}
CONDA_ENV_NAME="neuro-parakeet-mlx-server"

echo "Starting Neuro-Parakeet MLX Server..."
echo "  Port: $PORT"
echo "  Model: $MODEL"
if [ -n "$API_KEY" ]; then
    echo "  API Key: ENABLED"
else
    echo "  API Key: DISABLED (set API_KEY environment variable to enable)"
fi
echo ""

# Activate conda environment if available
if command -v conda &> /dev/null; then
    # Initialize conda for bash
    eval "$(conda shell.bash hook)"
    
    # Check if the environment exists
    if conda env list | grep -q "^${CONDA_ENV_NAME}\s"; then
        conda activate "$CONDA_ENV_NAME"
        echo "  Using conda environment: $CONDA_ENV_NAME"
        echo "  Python: $(which python)"
        
        # Check if parakeet-mlx is installed
        if ! python -c "import parakeet_mlx" 2>/dev/null; then
            echo ""
            echo "  ⚠️  Warning: parakeet-mlx is not installed in this environment!"
            echo "  Please install dependencies:"
            echo "    pip install -r requirements.txt"
            echo ""
        fi
    else
        echo "  Warning: Conda environment '$CONDA_ENV_NAME' not found."
        echo "  Please create it with: conda create -n $CONDA_ENV_NAME python=3.10 -y"
        echo "  Then install dependencies: pip install -r requirements.txt"
        echo ""
    fi
else
    echo "  Warning: conda not found. Using system Python."
    echo ""
fi

export PARAKEET_MODEL="$MODEL"
if [ -n "$API_KEY" ]; then
    export API_KEY="$API_KEY"
fi
python parakeet_server.py --port "$PORT" --model "$MODEL"

