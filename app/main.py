import gradio as gr
import os
import sys
from pathlib import Path

# Add the app directory to the system path
app_dir = Path(__file__).parent.parent.resolve()
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import components
from app.components.script_generator import create_script_generator_tab
from app.components.script_editor import create_script_editor_tab
from app.components.voiceover_generator import create_voiceover_tab, set_voice_data

# Import utilities
from app.utils.elevenlabs_client import get_voices
from app.config import validate_config, OPENAI_MODEL, OPENAI_API_KEY

def setup_directories():
    """Create necessary output directories"""
    os.makedirs("output/scripts", exist_ok=True)
    os.makedirs("output/audio", exist_ok=True)

def load_voices():
    """Load voice data from ElevenLabs"""
    # Define preset voices
    preset_voice_names = [
        # Male voices
        "Dan Teacher - Natural", 
        "Dan Teacher - Neutral", 
        "Dan Teacher - Upbeat", 
        "Mark - Natural Conversations",
        # Female voices
        "Cassidy", 
        "Jessica Anne - Conversational", 
        "Lori - Happy", 
        "Rachel"
    ]
    
    # Corresponding IDs (these should match the voice names above)
    preset_voice_ids = [
        # Male voices
        "jn5Dym9tbXQdxJRlyYzZ", # Dan Teacher - Natural
        "CMtJJeUfoLE6mZYBmsFl", # Dan Teacher - Neutral
        "W14NZHmEOKlltX7Dhrac", # Dan Teacher - Upbeat
        "UgBBYS2sOqTuMpoF3BR0", # Mark - Natural Conversations
        # Female voices
        "56AoDkrOh6qfVPDXZ7Pt", # Cassidy
        "g6xIsTj2HwM6VR4iXFCw", # Jessica Anne - Conversational
        "TbMNBJ27fH2U0VgpSNko", # Lori - Happy
        "21m00Tcm4TlvDq8ikWAM"  # Rachel
    ]
    
    # Get voices from ElevenLabs account
    voice_names, voice_ids = [], []
    try:
        voices = get_voices()
        if voices:
            # Populate voice data with actual voices from the API
            for voice in voices:
                voice_name = voice.get("name", "Unnamed")
                voice_id = voice.get("voice_id", "")
                
                if voice_name and voice_id:
                    # Clean and add to lists
                    voice_name = voice_name.strip()
                    voice_id = voice_id.strip()
                    voice_names.append(voice_name)
                    voice_ids.append(voice_id)
                    print(f"Found voice: {voice_name} (ID: {voice_id})")
    except Exception as e:
        print(f"Error loading voices from API: {str(e)}")
    
    # Set voice data for the voiceover component
    set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
    
    return preset_voice_names, preset_voice_ids, voice_names, voice_ids

def create_interface():
    """Create the Gradio interface"""
    # Setup necessary directories
    setup_directories()
    
    # Load voices
    preset_voice_names, preset_voice_ids, voice_names, voice_ids = load_voices()
    
    with gr.Blocks(title="VoiceScribe Studio") as app:
        gr.Markdown("# VoiceScribe Studio")
        gr.Markdown("Create educational scripts and generate voiceovers with AI")
        
        with gr.Tabs():
            # Create tabs using the component functions
            script_output, script_file_output = create_script_generator_tab()
            edit_script_input, edited_script_output = create_script_editor_tab()
            voiceover_script, voiceover_status, mp3_output, ogg_output = create_voiceover_tab()
            
            # Connect script generator to script editor
            script_output.change(
                fn=lambda x: x,
                inputs=[script_output],
                outputs=[edit_script_input]
            )
            
            # Connect script editor to voiceover generator
            edited_script_output.change(
                fn=lambda x: x,
                inputs=[edited_script_output],
                outputs=[voiceover_script]
            )
    
    return app

def main():
    """Main function to run the application"""
    try:
        # Print diagnostic information
        print(f"Starting application with OpenAI model: {OPENAI_MODEL}")
        print(f"OpenAI API key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'None'}")
        
        # Validate configuration
        validate_config()
        
        # Create and launch the interface
        app = create_interface()
        app.launch(
            server_name="0.0.0.0",
            share=False
        )
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        print("Please update your .env file with the required API keys.")
    except Exception as e:
        print(f"Application error: {str(e)}")

# Main application entry point
if __name__ == "__main__":
    main()
