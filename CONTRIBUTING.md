# Contributing to Neuro-Parakeet MLX Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/parakeet-mlx-server.git
   cd parakeet-mlx-server
   ```
3. **Set up development environment**:
   ```bash
   conda create -n neuro-parakeet-mlx-server-dev python=3.10 -y
   conda activate neuro-parakeet-mlx-server-dev
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them:
   ```bash
   # Run tests
   pytest
   
   # Run with coverage
   pytest --cov=parakeet_server --cov-report=html
   
   # Format code
   black parakeet_server.py
   isort parakeet_server.py
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
   
   Pre-commit hooks will run automatically to check code quality.

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

## Code Style

- **Formatting**: We use [Black](https://black.readthedocs.io/) for code formatting
- **Import sorting**: We use [isort](https://pycqa.github.io/isort/) for import organization
- **Linting**: We use [flake8](https://flake8.pycqa.org/) for linting
- **Type hints**: Please add type hints to function signatures
- **Docstrings**: Add docstrings to functions and classes (Google style)

### Example

```python
def transcribe_audio(
    audio_path: str,
    language: str = "de"
) -> str:
    """
    Transcribe an audio file.
    
    Args:
        audio_path: Path to the audio file
        language: Language code (default: "de")
        
    Returns:
        Transcribed text
    """
    # Implementation
    pass
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a PR
- Aim for good test coverage
- Tests should be in the `tests/` directory

Run tests:
```bash
pytest
pytest -v  # Verbose output
pytest tests/test_server.py::test_specific_test  # Run specific test
```

## Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what changes you made and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update README if needed
- **Small PRs**: Keep PRs focused and reasonably sized

## Reporting Issues

When reporting issues, please include:
- Description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)
- Error messages or logs

## Questions?

Feel free to open an issue for questions or discussions!

Thank you for contributing! 🎉

