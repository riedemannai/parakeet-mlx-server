# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive system validation on startup
- Health check endpoint (`/health`) for monitoring
- File upload validation (size limits, empty file detection)
- Port availability check before starting server
- Disk space validation warnings
- Improved error messages for MLX library requirements
- Automatic conda environment activation in start script
- Dependency check warnings in start script

### Changed
- Default model changed to `NeurologyAI/neuro-parakeet-mlx` (recommended for German medical speech)
- Updated all dependencies to latest versions
- Improved error handling and logging throughout
- Enhanced troubleshooting documentation

### Fixed
- Fixed "Model not loaded" error by ensuring correct Python environment
- Improved conda environment detection in start script
- Better error messages for unsupported platforms (Linux/Windows)

## [0.1.0] - 2024-12-XX

### Added
- Initial release
- OpenAI-compatible FastAPI server for audio transcription
- Support for Parakeet-MLX models
- Web UI for audio transcription
- Automatic model downloading from HuggingFace
- CORS middleware support
- Comprehensive test suite
- Pre-commit hooks for code quality
- CI/CD pipeline with GitHub Actions

### Features
- POST `/v1/audio/transcriptions` - Audio transcription endpoint
- GET `/` - Root endpoint with status
- GET `/transcription` - Transcription UI
- GET `/health` - Health check endpoint
- GET `/docs` - Swagger UI documentation
- GET `/redoc` - ReDoc documentation
- GET `/openapi.json` - OpenAPI schema

[Unreleased]: https://github.com/riedemannai/parakeet-mlx-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/riedemannai/parakeet-mlx-server/releases/tag/v0.1.0

