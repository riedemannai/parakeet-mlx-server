"""Unit tests for parakeet_server.py"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import tempfile
import os

# Mock the parakeet_mlx import before importing the server
import sys
sys.modules['parakeet_mlx'] = MagicMock()
sys.modules['huggingface_hub'] = MagicMock()

from parakeet_server import app, clean_text, extract_text, extract_segments


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    mock = MagicMock()
    mock.transcribe.return_value = MagicMock(
        text="Test transcription",
        segments=[
            MagicMock(text="Test", start=0.0, end=1.0),
            MagicMock(text="transcription", start=1.0, end=2.0)
        ]
    )
    return mock


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()


def test_clean_text():
    """Test text cleaning function."""
    assert clean_text("hello  world") == "hello world"
    assert clean_text("  test  ") == "test"
    assert clean_text("hello <unk> world") == "hello world"
    assert clean_text("") == ""


def test_extract_text_from_object():
    """Test extracting text from object with text attribute."""
    obj = MagicMock(text="test text")
    assert extract_text(obj) == "test text"


def test_extract_text_from_dict():
    """Test extracting text from dictionary."""
    obj = {"text": "test text"}
    assert extract_text(obj) == "test text"


def test_extract_segments_from_object():
    """Test extracting segments from object."""
    seg1 = MagicMock(text="hello", start=0.0, end=1.0)
    seg2 = MagicMock(text="world", start=1.0, end=2.0)
    obj = MagicMock(segments=[seg1, seg2])
    
    segments = extract_segments(obj)
    assert len(segments) == 2
    assert segments[0]["text"] == "hello"
    assert segments[0]["start"] == 0.0
    assert segments[1]["text"] == "world"


def test_extract_segments_from_dict():
    """Test extracting segments from dictionary."""
    obj = {
        "segments": [
            {"text": "hello", "start": 0.0, "end": 1.0},
            {"text": "world", "start": 1.0, "end": 2.0}
        ]
    }
    
    segments = extract_segments(obj)
    assert len(segments) == 2
    assert segments[0]["text"] == "hello"


@patch('parakeet_server.model')
def test_transcription_endpoint_no_model(mock_model_global, client):
    """Test transcription endpoint when model is not loaded."""
    mock_model_global = None
    with patch('parakeet_server.model', None):
        # Create a dummy audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"dummy audio data")
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/v1/audio/transcriptions",
                    files={"file": ("test.wav", f, "audio/wav")},
                    data={"model": "parakeet-tdt-0.6b-v3"}
                )
            # Should fail with 500 if model not loaded
            assert response.status_code == 500
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def test_transcription_response_model():
    """Test TranscriptionResponse model."""
    from parakeet_server import TranscriptionResponse
    
    response = TranscriptionResponse(
        text="test",
        recording_timestamp="2024-01-01",
        segments=[{"text": "test", "start": 0.0, "end": 1.0}]
    )
    assert response.text == "test"
    assert response.recording_timestamp == "2024-01-01"
    assert len(response.segments) == 1

