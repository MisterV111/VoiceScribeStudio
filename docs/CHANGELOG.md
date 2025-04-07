# Changelog

All notable changes to the VoiceScribe Studio project will be documented in this file.

## [Unreleased]

### Added
- New ElevenLabs optimization techniques implemented in Humanize feature
  - Break tags for precise pause control `<break time="1.5s" />`
  - Artifact prevention with strategic leading/trailing breaks
  - Book-style narration for emotional context
  - Emotion tags for varied tones `<cheerful>text</cheerful>`
- Comprehensive documentation in `docs/ELEVENLABS_OPTIMIZATION.md`
- Example script showcasing all techniques in `examples/optimized_elevenlabs_script.txt`
- Warning system in preview to highlight problematic characters causing artifacts
- CSS styling for better visualizing different markup types

### Fixed
- Removed intonation arrow markers (↗↘) that were causing artifacts in ElevenLabs output
- Updated humanize system prompt to explicitly avoid problematic characters
- Improved script preview with clearer markup highlighting
- Fixed Token Analytics dashboard not displaying data due to SQL query typo in `token_counter.py`

## [0.1.0] - 2023-04-06

### Added
- Initial release with core functionality
- DeepSeek R1 integration for script generation
- Claude 3.7 Sonnet as fallback model
- ElevenLabs voice synthesis with multiple output formats
- Script editing capabilities
- Multiple template options for different content types
- Admin dashboard for testing and analytics
- Token usage tracking 