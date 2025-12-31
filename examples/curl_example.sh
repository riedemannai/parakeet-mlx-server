#!/bin/bash
# Example curl commands for parakeet-mlx-server

SERVER_URL="http://localhost:8002"
AUDIO_FILE="test_audio.wav"

echo "1. Health check:"
curl -X GET "${SERVER_URL}/"

echo -e "\n\n2. Transcribe audio (JSON response):"
curl -X POST "${SERVER_URL}/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@${AUDIO_FILE}" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de" \
  -F "response_format=json"

echo -e "\n\n3. Transcribe audio (text response):"
curl -X POST "${SERVER_URL}/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@${AUDIO_FILE}" \
  -F "model=parakeet-tdt-0.6b-v3" \
  -F "language=de" \
  -F "response_format=text"

