# Tests

This directory contains unit tests for the parakeet-mlx-server.

## Running Tests

### Install test dependencies

```bash
pip install -r requirements-dev.txt
```

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_server.py
```

### Run specific test

```bash
pytest tests/test_server.py::test_clean_text
```

### Run with coverage report

```bash
pytest --cov=parakeet_server --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

## Test Structure

- `test_server.py` - Unit tests for the main server functionality
  - Tests for utility functions (`clean_text`, `extract_text`, `extract_segments`)
  - Tests for API endpoints
  - Tests for response models
  - Tests for error handling

## Writing New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<functionality>`
2. Add docstrings explaining what the test does
3. Use fixtures for common setup (see `@pytest.fixture`)
4. Mock external dependencies (like `parakeet_mlx`)

Example:

```python
def test_new_functionality():
    """Test description of what this test verifies."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == "expected"
```

