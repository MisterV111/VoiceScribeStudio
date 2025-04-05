# (Version 0.1.0)

<div align="center">
  <img src="app/assets/VoiceScribe Studio Banner.png" alt="VoiceScribe Studio Banner" width="800">
</div>

## About

VoiceScribe Studio leverages advanced AI workflow backend integrations to enhance content creation. This version (v0.1.0) focuses on providing a high-quality script generation core and a polished voiceover production experience.

Our vision is to build VoiceScribe into an **Intelligent Agent-driven Content Production Studio**, integrating AI agents directly into the workflow to streamline both the creative and production processes, from initial concept to final multimedia output.

### Current Capabilities (v0.1.0 - Phase 1 Complete)

- 📝 **Smarter Script Generation**: Significantly upgraded AI engine using:
  - **DeepSeek R1** as the primary model for high-quality, creative scripts across various templates.
  - **Claude 3.7 Sonnet** as a robust fallback for reliability.
- 🗣️ **Enhanced Voice Synthesis & Output**: A more polished experience for generating voiceovers:
  - Support for multiple audio formats: **MP3 (High Quality 192kbps)**, **OGG (Game Audio Quality)**, and **High Quality WAV (48kHz/24-bit)**.
  - **Batch Generation**: Create all formats with a single click.
  - **Format Preview**: See which formats will be generated when selecting "Generate All Formats".
  - **Professional Download Interface**: Clean, responsive cards with format-specific icons and file details.
  - **Styled Status Messages**: Clear visual feedback (e.g., colored success messages) for generation status.
- 📄 **Reference Input Options** (In Development - Phase 2): Multiple ways to provide context:
  - **Document Upload**: Support for various file formats (.txt, .md, .pdf, .docx)
  - **Web URL Reference**: Extract context directly from web pages
  - **YouTube Reference**: Use YouTube videos as style or content references
- 🔧 **Voice Customization**: Fine-tune voice parameters (stability, similarity, style, speed).
- ✏️ **Script Editing**: Built-in editor to refine generated scripts.
- 🔀 **Multiple Templates**: Specialized templates (General Education, Technical Tutorial, Marketing, Business Training, Music Lesson).
- 📊 **Audience & Content Adaptation**: Customize scripts for different audience levels, tones, and lengths.
- 💾 **Local Storage**: Save generated scripts and audio files to your machine.
- 🧪 **Admin & Testing Tools**:
  - **Secure Admin Dashboard**: Separate interface for testing and analytics (Login: `admin`/`admin123`).
  - **Cross-Template Testing Suite**: Ensures reliability and quality across templates.

### Future Vision (Planned Enhancements)

The roadmap includes transforming VoiceScribe into a full AI content **production** partner through phased development:

- **Phase 2: Smarter Context & Content Processing**: AI learns to analyze documents, understand YouTube video styles, and remember user preferences (Memory MCP).
- **Phase 3: Multilingual Translation**: AI-powered translation to multiple languages using Claude 3.7 Sonnet and custom glossaries.
- **Phase 4: AI Research Assistant**: Web browsing (FireCrawl) and fact-verification (Perplexity MCP) capabilities for accurate, informed scripts.
- **Phase 5: Multimedia Production**: AI-generated background music (Suno AI), visual content (EverArt MCP), and professional document exports.
- **Phase 6: Polishing & Professional Tools**: User dashboards for cost tracking, enhanced input methods (URLs, docs), media previews, and final deployment.

## Development & Versioning

- **main**: Represents the latest stable, released version (currently v0.1.0).
- **phase-2-features**: Active development branch for features planned in Phase 2.
- **Tags**: Specific versions (like `v0.1.0`) are marked using Git tags on the `main` branch.

Development for upcoming features occurs on dedicated branches (like `phase-2-features`) and is merged into `main` upon completion, accompanied by a new version tag.

## Installation

### Prerequisites

- Python 3.9+
- DeepSeek API key (primary model)
- Anthropic API key (for Claude 3.7 Sonnet fallback)
- ElevenLabs API key (for voice synthesis)

### Additional Prerequisites (Future Features)

- YouTube Data API Key
- Perplexity API Key
- Suno AI API Key
- EverArt API Key
- Configuration for self-hosted MCP servers (e.g., FireCrawl)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/MisterV111/VoiceScribeStudio.git
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
   # --- Required Keys (v0.1.0) ---
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

   # --- Optional Keys (Future Features) ---
   # YOUTUBE_DATA_API_KEY=your_youtube_data_api_key_here
   # PERPLEXITY_API_KEY=your_perplexity_api_key_here
   # SUNO_API_KEY=your_suno_api_key_here
   # EVERART_API_KEY=your_everart_api_key_here
   ```

5. Run the application:
   ```
   python run.py
   ```
   The application will be available at http://localhost:7860/.

## Application Structure

VoiceScribe Studio runs as a single Gradio application, with a separate admin section accessible via login.

- **Main Interface (Port 7860)**: User-facing tools for script generation, editing, and voiceover production.
- **Admin Dashboard (Accessible via Login)**: Contains the Testing Suite and future analytics dashboards. Use the "Admin Login" link and credentials (`admin`/`admin123`).

## Usage (v0.1.0)

1.  **Script Generation**: Select a template, provide a subject/prompt, define audience, tone, and length. Click "Generate Script".
2.  **Script Editing**: Modify the generated script in the "Edit Script" tab.
3.  **Voiceover Creation**:
    *   Go to the "Generate Voiceover" tab (script is pre-filled).
    *   Select a preset voice or enter a custom ElevenLabs Voice ID.
    *   Choose an audio format (MP3, OGG, WAV) or select "Generate All Formats".
    *   Adjust voice settings (Stability, Similarity, etc.).
    *   Click "Generate Voiceover".
4.  **Download**: Use the download links provided in the output area.

## Templates

VoiceScribe Studio offers several specialized templates:

- General Education
- Technical Tutorial
- Marketing
- Business Training
- Music Lesson

## Contributing

Contributions are welcome! Please follow standard GitHub fork & pull request procedures, targeting the relevant development branch (e.g., `phase-2-features`).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [DeepSeek AI](https://www.deepseek.com/) for the DeepSeek R1 model
- [Anthropic](https://www.anthropic.com/) for the Claude 3.7 Sonnet model
- [ElevenLabs](https://elevenlabs.io/) for the text-to-speech technology
- [Gradio](https://gradio.app/) for the web interface
- Future Acknowledgments: Suno AI, Perplexity AI, YouTube Data API, FireCrawl, EverArt, etc. 