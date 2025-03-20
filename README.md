# VoiceScribe Studio

VoiceScribe Studio is a powerful AI-driven educational content creation platform that transforms how instructors, trainers, and content creators develop professional-quality educational materials. By leveraging OpenAI's advanced language models and ElevenLabs' state-of-the-art voice synthesis technology, VoiceScribe Studio streamlines the entire content production workflow—from script generation to final voiceover production—all within an intuitive, user-friendly interface.

With specialized templates for various educational domains including music instruction, corporate training, and technical tutorials, VoiceScribe Studio helps users craft perfectly tailored content for their specific audience. The application enables fine-grained control over script length, audience targeting, and tone, while providing powerful editing capabilities with AI assistance. Once your script is perfected, transform it into lifelike voiceovers using premium male and female voices, with precise control over delivery speed, style, and even custom pauses using SSML tags.

VoiceScribe Studio eliminates the technical barriers to creating professional educational content, making it accessible to educators, trainers, and content creators of all technical skill levels.

## Features

- Generate educational scripts using OpenAI's API
- Edit and refine scripts with AI assistance
- Generate high-quality voiceovers with ElevenLabs' API
- Convert audio between MP3 and OGG formats
- User-friendly Gradio web interface

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/MisterV111/VoiceScribeStudio.git
   cd VoiceScribeStudio
   ```
   
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   
4. Configure your API keys:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your OpenAI and ElevenLabs API keys.

### Running the Application

To run the application, you can use either:

```
python3 run.py
```

Or use the start script:

```
bash start.sh
```

This will start the Gradio web interface. You can access it at http://127.0.0.1:7860 in your web browser.

## Usage

### Generating a Script

1. Navigate to the "Generate Script" tab
2. Enter your script topic and details
3. Click "Generate Script"
4. Your script will be saved in the `output/scripts` directory

### Editing a Script

1. Navigate to the "Edit Script" tab
2. Paste your script or use one generated in the previous step
3. Enter your editing instructions
4. Click "Edit Script"
5. Your edited script will be saved in the `output/scripts` directory

### Creating a Voiceover

1. Navigate to the "Generate Voiceover" tab
2. Paste your script
3. Select a voice and output format
4. Adjust voice settings as needed
5. Click "Generate Voiceover"
6. Play the audio or download it
7. Your audio will be saved in the `output/audio` directory

## Advanced Script Formatting

When creating voiceovers, you can control pauses and timing using SSML tags:

```
<break time="0.5s" />   - Add a half-second pause
<break time="1s" />     - Add a 1-second pause
<break time="1.5s" />   - Add a 1.5-second pause
<break time="2s" />     - Add a 2-second pause
<break time="3s" />     - Add a 3-second pause
```

See the Script Formatting Guide in the app for more details.

## Project Structure

- `app/` - Main application code
  - `config.py` - Configuration handling
  - `main.py` - Gradio interface setup
  - `components/` - UI components for each tab
  - `utils/` - Utility functions for API interactions
  - `templates/` - Template prompts and documents
- `output/` - Generated scripts and audio files
  - `scripts/` - Generated and edited scripts
  - `audio/` - Generated voiceovers
- `run.py` - Application entry point
- `start.sh` - Shell script to start the application
- `.env.example` - Example environment file for API keys
- `requirements.txt` - Python dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for providing the language model API
- [ElevenLabs](https://elevenlabs.io/) for the voice synthesis API
- [Gradio](https://gradio.app/) for the web interface framework 