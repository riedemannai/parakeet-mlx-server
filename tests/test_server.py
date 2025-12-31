"""Unit tests for parakeet_server.py"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
import tempfile
import os
import io

# Mock the parakeet_mlx import before importing the server
import sys
sys.modules['parakeet_mlx'] = MagicMock()
sys.modules['huggingface_hub'] = MagicMock()

from parakeet_server import (
    app, 
    clean_text, 
    extract_text, 
    extract_segments,
    TranscriptionResponse,
    load_model
)


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
    response = TranscriptionResponse(
        text="test",
        recording_timestamp="2024-01-01",
        segments=[{"text": "test", "start": 0.0, "end": 1.0}]
    )
    assert response.text == "test"
    assert response.recording_timestamp == "2024-01-01"
    assert len(response.segments) == 1


def test_transcription_response_minimal():
    """Test TranscriptionResponse with minimal fields."""
    response = TranscriptionResponse(text="minimal")
    assert response.text == "minimal"
    assert response.recording_timestamp is None
    assert response.segments is None


def test_clean_text_various_cases():
    """Test clean_text with various edge cases."""
    # Multiple spaces
    assert clean_text("hello    world") == "hello world"
    
    # Tabs and newlines
    assert clean_text("hello\tworld\n") == "hello world"
    
    # Multiple <unk> tokens
    assert clean_text("hello <unk> world <unk> test") == "hello world test"
    
    # Case insensitive <unk>
    assert clean_text("hello <UNK> world") == "hello world"
    
    # Leading/trailing whitespace
    assert clean_text("  hello world  ") == "hello world"
    
    # Only whitespace
    assert clean_text("   ") == ""
    
    # Mixed whitespace and <unk>
    assert clean_text("  hello <unk>  world  ") == "hello world"


def test_extract_text_with_segments():
    """Test extract_text when result has segments."""
    # Object with segments
    seg1 = MagicMock(text="hello")
    seg2 = MagicMock(text="world")
    obj = MagicMock(segments=[seg1, seg2])
    assert extract_text(obj) == "hello world"
    
    # Dict with segments
    obj_dict = {
        "segments": [
            {"text": "hello"},
            {"text": "world"}
        ]
    }
    assert extract_text(obj_dict) == "hello world"


def test_extract_text_edge_cases():
    """Test extract_text with edge cases."""
    # Empty segments
    obj = MagicMock(segments=[])
    assert extract_text(obj) == ""
    
    # Dict with empty segments
    obj_dict = {"segments": []}
    assert extract_text(obj_dict) == ""
    
    # Dict with text but no segments
    obj_dict = {"text": "test"}
    assert extract_text(obj_dict) == "test"
    
    # Dict without text or segments
    obj_dict = {"other": "value"}
    assert extract_text(obj_dict) == "{'other': 'value'}"
    
    # Non-dict, non-object
    assert extract_text(123) == "123"
    assert extract_text(None) == "None"


def test_extract_segments_edge_cases():
    """Test extract_segments with edge cases."""
    # Empty segments
    obj = MagicMock(segments=[])
    assert extract_segments(obj) is None
    
    # Dict with empty segments
    obj_dict = {"segments": []}
    assert extract_segments(obj_dict) is None
    
    # No segments attribute
    obj = MagicMock(spec=[])
    assert extract_segments(obj) is None
    
    # Segments without timing
    seg = MagicMock(text="test")
    del seg.start
    del seg.end
    obj = MagicMock(segments=[seg])
    segments = extract_segments(obj)
    assert len(segments) == 1
    assert segments[0]["text"] == "test"
    assert "start" not in segments[0]
    assert "end" not in segments[0]


def test_extract_segments_mixed_timing():
    """Test extract_segments with mixed timing information."""
    # Some segments with timing, some without
    seg1 = MagicMock(text="hello", start=0.0, end=1.0)
    seg2 = MagicMock(text="world")
    del seg2.start
    del seg2.end
    obj = MagicMock(segments=[seg1, seg2])
    
    segments = extract_segments(obj)
    assert len(segments) == 2
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 1.0
    assert "start" not in segments[1]
    assert "end" not in segments[1]


@patch('parakeet_server.model')
def test_transcription_endpoint_with_model(mock_model_global, client):
    """Test transcription endpoint with a loaded model."""
    # Create a mock model
    mock_model = MagicMock()
    mock_segment1 = MagicMock(text="Hello", start=0.0, end=1.0)
    mock_segment2 = MagicMock(text="world", start=1.0, end=2.0)
    mock_result = MagicMock(
        text="Hello world",
        segments=[mock_segment1, mock_segment2]
    )
    mock_model.transcribe.return_value = mock_result
    
    # Patch the global model
    with patch('parakeet_server.model', mock_model):
        # Create a dummy audio file
        audio_data = b"fake audio data"
        files = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
        data = {
            "model": "parakeet-tdt-0.6b-v3",
            "response_format": "json"
        }
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        assert result["text"] == "Hello world"
        assert "segments" in result
        assert len(result["segments"]) == 2


@patch('parakeet_server.model')
def test_transcription_endpoint_text_format(mock_model_global, client):
    """Test transcription endpoint with text response format."""
    mock_model = MagicMock()
    mock_result = MagicMock(text="Simple text", segments=[])
    mock_model.transcribe.return_value = mock_result
    
    with patch('parakeet_server.model', mock_model):
        audio_data = b"fake audio data"
        files = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
        data = {
            "model": "parakeet-tdt-0.6b-v3",
            "response_format": "text"
        }
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        assert response.status_code == 200
        assert response.text == "Simple text"
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


@patch('parakeet_server.model')
def test_transcription_endpoint_with_recording_timestamp(mock_model_global, client):
    """Test transcription endpoint with recording timestamp."""
    mock_model = MagicMock()
    mock_result = MagicMock(text="Test", segments=[])
    mock_model.transcribe.return_value = mock_result
    
    with patch('parakeet_server.model', mock_model):
        audio_data = b"fake audio data"
        files = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
        data = {
            "model": "parakeet-tdt-0.6b-v3",
            "recording_timestamp": "2024-01-01T12:00:00"
        }
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["recording_timestamp"] == "2024-01-01T12:00:00"


@patch('parakeet_server.model')
def test_transcription_endpoint_model_without_language(mock_model_global, client):
    """Test transcription when model doesn't support language parameter."""
    mock_model = MagicMock()
    # First call with language raises TypeError, second without language succeeds
    call_count = [0]
    
    def transcribe_side_effect(*args, **kwargs):
        call_count[0] += 1
        if 'language' in kwargs and call_count[0] == 1:
            raise TypeError("transcribe() got an unexpected keyword argument 'language'")
        return MagicMock(text="Test without language", segments=[])
    
    mock_model.transcribe.side_effect = transcribe_side_effect
    
    with patch('parakeet_server.model', mock_model):
        audio_data = b"fake audio data"
        files = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
        data = {"model": "parakeet-tdt-0.6b-v3", "language": "de"}
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        # Should succeed after falling back to call without language
        assert response.status_code == 200
        assert mock_model.transcribe.call_count == 2  # Called twice: with language, then without


def test_root_endpoint_without_index_html(client):
    """Test root endpoint when index.html doesn't exist."""
    # The endpoint should return JSON status
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "error"]


def test_transcription_response_validation():
    """Test TranscriptionResponse Pydantic validation."""
    # Valid response
    response = TranscriptionResponse(text="test")
    assert response.text == "test"
    
    # Empty text should still be valid (empty string)
    response = TranscriptionResponse(text="")
    assert response.text == ""
    
    # Segments can be None
    response = TranscriptionResponse(text="test", segments=None)
    assert response.segments is None


def test_extract_text_from_segments_with_dict_segments():
    """Test extract_text when segments are dictionaries."""
    obj = MagicMock()
    obj.segments = [
        {"text": "hello"},
        {"text": "world"}
    ]
    assert extract_text(obj) == "hello world"


def test_extract_segments_with_dict_segments():
    """Test extract_segments when segments are dictionaries."""
    obj = {
        "segments": [
            {"text": "hello", "start": 0.0, "end": 1.0},
            {"text": "world", "start": 1.0}
        ]
    }
    
    segments = extract_segments(obj)
    assert len(segments) == 2
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 1.0
    assert segments[1]["start"] == 1.0
    assert "end" not in segments[1]  # Missing end should not be included

