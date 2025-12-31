#!/usr/bin/env python3
"""Example Python client for parakeet-mlx-server."""

import openai
from pathlib import Path


def transcribe_audio(audio_path: str, server_url: str = "http://localhost:8002") -> str:
    """
    Transcribe an audio file using the parakeet-mlx-server.
    
    Args:
        audio_path: Path to the audio file
        server_url: Base URL of the server
        
    Returns:
        Transcribed text
    """
    client = openai.OpenAI(
        base_url=f"{server_url}/v1",
        api_key="not-needed"  # API key not required for local server
    )
    
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="parakeet-tdt-0.6b-v3",
            file=audio_file,
            language="de"
        )
    
    return transcript.text


def transcribe_with_segments(audio_path: str, server_url: str = "http://localhost:8002"):
    """
    Transcribe an audio file and get segments with timestamps.
    
    Args:
        audio_path: Path to the audio file
        server_url: Base URL of the server
        
    Returns:
        Dictionary with text and segments
    """
    import requests
    
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f, "audio/wav")}
        data = {
            "model": "parakeet-tdt-0.6b-v3",
            "language": "de",
            "response_format": "json"
        }
        
        response = requests.post(
            f"{server_url}/v1/audio/transcriptions",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python python_client.py <audio_file> [server_url]")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8002"
    
    print(f"Transcribing {audio_file}...")
    result = transcribe_with_segments(audio_file, server_url)
    
    print(f"\nTranscription: {result['text']}")
    if result.get('segments'):
        print("\nSegments:")
        for seg in result['segments']:
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            print(f"  [{start:.2f}s - {end:.2f}s]: {seg['text']}")

