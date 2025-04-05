# VoiceScribe Studio

AI-powered script generation and voiceover production studio for educational and marketing content.

<div align="center">
  <img src="app/assets/VoiceScribe Studio Banner.png" alt="VoiceScribe Studio Banner" width="800">
</div>

## About

VoiceScribe Studio is a comprehensive application that combines advanced AI technologies to streamline content creation from script to voiceover. Designed for educators, marketers, and content creators, this application simplifies the process of creating professional, engaging content with minimal effort.

### Features

**Current MVP Features:**

- 📝 **Script Generation**: Create customized scripts using our multi-model architecture:
  - **DeepSeek R1 as primary model** for superior creative script generation 
  - **Claude 3.7 Sonnet as fallback** for reliable content processing
- 🗣️ **Voice Synthesis**: Transform scripts into natural-sounding voiceovers using ElevenLabs' advanced TTS technology.
  - Support for multiple audio formats (MP3, OGG, High-Quality WAV)
  - Batch generation of all formats with a single click
  - Professionally styled download interface with format-specific icons
  - Format preview capabilities for multi-format generation
  - Visual status indicators with custom styling for better user feedback
- 🔧 **Voice Customization**: Adjust voice parameters including stability, clarity, style, and speed to achieve the perfect sound.
- ✏️ **Script Editing**: Integrated editor for refining AI-generated scripts before voiceover creation.
- 🔀 **Multiple Templates**: Specialized script templates for different content types and audiences.
- 📊 **Audience Targeting**: Customize content for different audience levels from beginner to expert.
- 🔍 **Content Adaptation**: Adjust tone, length, and style based on your specific needs.
- 💾 **Local Storage**: Save generated scripts and audio files locally.
- 🧪 **Testing Dashboard**: Comprehensive cross-template testing suite with user-friendly result visualization for quality assurance.
  - Password-protected interface accessible via a dedicated button
  - Formatted test configuration visualization with clear parameters
  - Enhanced validation results with color-coded pass/fail indicators
  - Interactive data visualization and filtering capabilities

### Planned Enhancements (v2 - Under Development)

VoiceScribe Studio is undergoing a major enhancement. Future versions (developed on the `voicescribe-v2` branch) will include:

- **🌐 Multi-Source Content Integration**: Ability to process content from various sources:
    - **Web Content Retrieval** (via FireCrawl)
    - **Direct URL Processing** (via Browser Tools MCP)
    - **Document Uploads & Analysis**
- **✅ Enhanced Accuracy & Verification**: Fact-checking and knowledge enhancement using **Perplexity MCP**.
- **<0xF0><0x9F><0xAA><0x9E> YouTube Integration**: Direct API integration to reference YouTube video style and content.
- **<0xF0><0x9F><0xA7><0xA0> Memory & Context**: Persistent user preferences and context using **Memory MCP**.
- **<0xF0><0x9F><0xAA><0xA8> Multilingual Translation**: In-app script translation to multiple languages (French, Spanish, German, etc.) powered by Claude 3.7 Sonnet with glossary support.
- **<0xF0><0x9F><0x8E><0xB5> Background Music Generation**: AI-powered background music creation tailored to script tone using **Suno AI**.
- **<0xF0><0x9F><0x96><0xBC>️ Visual Content Generation**: AI-generated images relevant to the script content using **EverArt MCP**.
- **<0xF0><0x9F><0x93><0x84> Professional Exports**: Advanced document export formats using **Document Conversion MCP**.
- **📂 Enhanced File Management**: Improved content organization via **File System MCP**.
- **📊 Advanced Analytics**: Detailed token usage dashboard and API cost monitoring.
- 📊 **Analytics Dashboard**: Track project metrics, token usage, and generation trends

## Development Branches

The repository is organized with the following branch structure:

- **main**: Stable, production-ready version of VoiceScribe Studio
- **voicescribe-v2**: Development branch for the next major version (currently in active development)

All new feature development happens on the **voicescribe-v2** branch and is merged to main when ready for release.

## Installation

### Prerequisites

- Python 3.9+
- DeepSeek API key (primary model)
- Anthropic API key (for Claude 3.7 Sonnet fallback)
- ElevenLabs API key (for voice synthesis)

### Additional Prerequisites (Optional Features)

- YouTube Data API Key (for YouTube features)
- Perplexity API Key (for verification features)
- Suno AI API Key (for music generation)
- EverArt API Key (for image generation)
- Configuration for self-hosted MCP servers (e.g., FireCrawl) where applicable.

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/VoiceScribeStudio.git
   cd VoiceScribeStudio
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```dotenv
   # --- Required Keys ---
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

   # --- Optional Feature Keys ---
   # OPENAI_API_KEY=your_openai_api_key_here  # For legacy support if needed
   # YOUTUBE_DATA_API_KEY=your_youtube_data_api_key_here
   # PERPLEXITY_API_KEY=your_perplexity_api_key_here
   # SUNO_API_KEY=your_suno_api_key_here
   # EVERART_API_KEY=your_everart_api_key_here
   ```

5. Run the application:
   ```
   python run.py
   ```
   
   This will start two server applications:
   - Main application: http://localhost:7860/
   - Testing dashboard: http://localhost:7861/ (protected with authentication)

## Application Structure

VoiceScribe Studio now runs as two separate Gradio applications:

1. **Main Application (Port 7860)**: The primary user interface for script generation, editing, and voiceover production.
2. **Testing Dashboard (Port 7861)**: A dedicated interface for cross-template testing and quality assurance, accessible via:
   - A "Test Suite" button in the main application
   - Direct access at http://localhost:7861/
   - Authentication required (username: `admin`, password: `testingsuite`)

This separation ensures a clean user experience while maintaining robust testing capabilities for development and quality control.

## Usage

*(Note: Usage will expand significantly with v2 features)*

1. **Script Generation**: Select a template, provide a subject/prompt, **or input content via document upload, URL, or YouTube link (v2)**.
2. **Script Editing & Translation (v2)**: Review, refine, and translate the generated script.
3. **Voiceover Creation**: Select a voice and adjust parameters.
4. **Media Enhancement (v2)**: Generate background music and visual content.
5. **Export**: Save script, audio, **music (v2)**, **images (v2)**, and **professional document formats (v2)**.

## Templates

VoiceScribe Studio offers several specialized templates:

- **General Education**: For traditional educational content
- **Technical Tutorial**: For software, coding, and technical instruction
- **Marketing**: For promotional and advertising content
- **Business Training**: For corporate training and professional development
- **Music Lesson**: For music instruction and demonstration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for the language model API
- [ElevenLabs](https://elevenlabs.io/) for the text-to-speech technology
- [Gradio](https://gradio.app/) for the web interface
- **[Anthropic](https://www.anthropic.com/) (Planned v2)** for the Claude 3.7 Sonnet model
- **[DeepSeek AI](https://www.deepseek.com/) (Planned v2)** for the DeepSeek R1 model
- **[Suno AI](https://suno.ai/) (Planned v2)** for AI music generation
- **[Perplexity AI](https://perplexity.ai/) (Planned v2)** for verification features
- **[YouTube Data API](https://developers.google.com/youtube/v3) (Planned v2)**
- **Various MCP Server technologies (Planned v2)** (FireCrawl, EverArt, etc.) 