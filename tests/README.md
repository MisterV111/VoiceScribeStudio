# Tests Directory

This directory contains test scripts and files for VoiceScribe Studio.

## Available Tests

- `test_openai.py` - Tests for OpenAI API connectivity and functionality
- `test_elevenlabs.py` - Tests for ElevenLabs API connectivity and functionality
- `debug_elevenlabs.py` - Debugging script for ElevenLabs API issues

## Cross-Template Testing Suite

VoiceScribe Studio includes a comprehensive cross-template testing suite for validating script generation across all templates. This testing system is accessible through:

1. Command-line: Run tests via the `app.tests.run_tests` module
2. Web interface: Access via the "Test Suite" button in the main application

### Web Interface Access
- Username: `admin`
- Password: `testingsuite`

### Features
- Automated testing of all templates with various parameter combinations
- Formatted test results with clear pass/fail indicators
- Detailed validation results for troubleshooting
- Script output inspection and comparison tools

## Running Tests

To run a test:

```bash
# Basic API tests
python -m tests.test_openai
python -m tests.test_elevenlabs

# Cross-Template Testing Suite
python -m app.tests.run_tests                                # Run all tests
python -m app.tests.run_tests --templates "Technical Tutorial"  # Test specific template
python -m app.tests.run_tests --force-fallback                # Test with fallback model
```

## Test Assets

This directory also contains test assets like sample audio files used for testing.

