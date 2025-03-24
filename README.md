# VoiceScribe Studio

AI-powered script generation and voiceover production studio for educational and marketing content.

<div align="center">
  <img src="app/assets/VoiceScribe Studio Banner.png" alt="VoiceScribe Studio Banner" width="800">
</div>

## About

VoiceScribe Studio is a comprehensive application that combines advanced AI technologies to streamline content creation from script to voiceover. Designed for educators, marketers, and content creators, this application simplifies the process of creating professional, engaging content with minimal effort.

### Features

- 📝 **Script Generation**: Create customized scripts for various content types including educational materials, marketing campaigns, business training, and more
- 🗣️ **Voice Synthesis**: Transform scripts into natural-sounding voiceovers using ElevenLabs' advanced TTS technology
- 🔧 **Voice Customization**: Adjust voice parameters including stability, clarity, style, and speed to achieve the perfect sound
- ✏️ **Script Editing**: Integrated editor for refining AI-generated scripts before voiceover creation
- 🔀 **Multiple Templates**: Specialized script templates for different content types and audiences
- 📊 **Audience Targeting**: Customize content for different audience levels from beginner to expert
- 🔍 **Content Adaptation**: Adjust tone, length, and style based on your specific needs
- 💾 **Local Storage**: Save generated scripts and audio files locally

## Development Branches

The repository is organized with the following branch structure:

- **main**: Stable, production-ready version of VoiceScribe Studio
- **voicescribe-v2**: Development branch for the next major version (currently in active development)

All new feature development happens on the **voicescribe-v2** branch and is merged to main when ready for release.

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key
- ElevenLabs API key

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
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

5. Run the application:
   ```
   python run.py
   ```

## Usage

1. **Script Generation**: Select a template type, adjust parameters, and provide a subject or prompt
2. **Script Editing**: Review and refine the generated script
3. **Voiceover Creation**: Select a voice and adjust parameters to generate the perfect voiceover
4. **Export**: Save both script and audio files for use in your projects

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