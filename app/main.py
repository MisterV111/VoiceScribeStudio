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
    
    # Define custom CSS path and asset paths
    css_path = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
    banner_path = os.path.join(os.path.dirname(__file__), "assets", "banner.png")
    
    # Simple CSS test string
    css_test = """
    .gradio-container {
        background-color: #f8faff !important;
        font-family: 'Inter', 'Segoe UI', Roboto, -apple-system, system-ui, BlinkMacSystemFont, sans-serif !important;
    }
    .header-row {
        margin-bottom: 1.5rem !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
        position: relative !important;
    }
    .banner-image {
        width: 100% !important;
        display: block !important;
    }
    .header-text {
        position: absolute !important;
        top: 50% !important;
        left: 20% !important;
        transform: translateY(-50%) !important;
        width: 80% !important;
    }
    .header-text h1, .header-text p {
        color: white !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        margin: 0 !important;
    }
    button.primary {
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    button[id*='generate'], button[id$='Generate'] {
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-top: 1rem !important;
        width: 100% !important;
    }
    .tabs {
        background-color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    .tabs > .tabitem {
        border-bottom: none !important;
        font-weight: 600 !important;
        color: #57606f !important;
        margin: 0 8px !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease !important;
        border-radius: 8px !important;
    }
    .tabs > .tabitem.selected {
        color: white !important;
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    .gradio-box, .gradio-group, .gradio-accordion {
        border-radius: 12px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12) !important;
        border: none !important;
        overflow: hidden;
        transition: all 0.3s ease;
        background-color: white !important;
    }
    """
    
    with gr.Blocks(title="VoiceScribe Studio", css=css_test) as app:
        with gr.Row(equal_height=True, elem_classes=["header-row"]):
            # Banner image
            gr.HTML(f'<img src="/gradio_api/file={banner_path}" alt="VoiceScribe Studio Banner" class="banner-image">')
            
            # Text overlay on banner
            with gr.Column(elem_classes=["header-text"]):
                gr.Markdown("# VoiceScribe Studio")
                gr.Markdown("VoiceScribe: Your Complete Script and Voiceover Solution for Education, Business, and Content Creation")
        
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
