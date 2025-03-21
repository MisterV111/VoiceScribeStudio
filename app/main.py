import gradio as gr
import os
import sys
from pathlib import Path
import base64

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
    
    # Define custom CSS path
    css_path = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")
    
    # Read logo as data URI
    try:
        with open(logo_path, "rb") as f:
            logo_svg = f.read()
            logo_base64 = base64.b64encode(logo_svg).decode("utf-8")
            logo_data_uri = f"data:image/svg+xml;base64,{logo_base64}"
    except Exception as e:
        print(f"Error loading logo: {str(e)}")
        # Fallback simple logo
        logo_data_uri = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4Ij48Y2lyY2xlIGN4PSIyNCIgY3k9IjI0IiByPSIyMCIgZmlsbD0iIzRhNmJhZiIvPjxwYXRoIGQ9Ik0xOCAxNnYxNmwxNi04eiIgZmlsbD0id2hpdGUiLz48L3N2Zz4="
    
    # Simple CSS test string
    css_test = """
    .gradio-container {
        background-color: #f8faff !important;
        font-family: 'Inter', 'Segoe UI', Roboto, -apple-system, system-ui, BlinkMacSystemFont, sans-serif !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        padding: 2rem !important;
    }
    
    /* Header styling */
    .header-row {
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        padding: 1.5rem 2rem !important;
        border-radius: 12px !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
    }
    .header-row h1, .header-row p {
        color: white !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Improved spacing and layout */
    .gradio-box, .gradio-group, .gradio-accordion {
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        background-color: white !important;
        border: 1px solid rgba(74, 107, 175, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    .gradio-box:hover, .gradio-group:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    }
    
    /* Section headings */
    .gradio-container h2, .gradio-container h3, .gr-form > div:first-child {
        color: #4a6baf !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid rgba(74, 107, 175, 0.2) !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Additional Context and similar section headers */
    .gradio-box > .gradio-markdown:first-child h3,
    .gradio-accordion > .gradio-markdown:first-child h3 {
        margin-top: 0 !important;
        color: #4a6baf !important;
        font-weight: 600 !important;
        border-left: 4px solid #4a6baf !important;
        padding-left: 10px !important;
        border-bottom: none !important;
    }
    
    /* Form fields alignment and spacing */
    .form, label, input, textarea, select {
        margin-bottom: 1rem !important;
    }
    
    label {
        font-weight: 600 !important;
        color: #4a6baf !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    
    input, textarea, select {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: #4a6baf !important;
        box-shadow: 0 0 0 3px rgba(74, 107, 175, 0.2) !important;
        outline: none !important;
    }
    
    /* Tab styling with brand colors */
    .tabs {
        display: flex !important;
        background-color: white !important;
        border-radius: 8px !important;
        padding: 0.25rem !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    .tabitem {
        flex: 1 !important;
        text-align: center !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .tabitem.selected {
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Override default Gradio tab selected color from orange to brand colors */
    .tab-nav button.selected {
        border-color: #4a6baf !important;
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        color: white !important;
    }
    
    /* Sliders and interactive elements */
    input[type="range"] {
        accent-color: #4a6baf !important;
    }
    
    /* Override Gradio slider track colors */
    input[type="range"]::-webkit-slider-runnable-track, 
    input[type="range"]::-moz-range-track {
        background: linear-gradient(90deg, #4a6baf, #7e57c2) !important;
    }
    
    /* Target Gradio progress bars/sliders specifically */
    .progress-bar-filled {
        background: linear-gradient(90deg, #4a6baf, #7e57c2) !important;
    }
    
    /* Checkboxes and Radio buttons */
    input[type="checkbox"], input[type="radio"] {
        accent-color: #4a6baf !important;
        width: auto !important;
    }
    
    /* Style Gradio's specific checkbox components */
    .gr-check-radio {
        border-color: #4a6baf !important;
    }
    
    .gr-check-radio:checked {
        background-color: #4a6baf !important;
        border-color: #4a6baf !important;
    }
    
    /* Button styling */
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
    
    button.primary:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25) !important;
        transform: translateY(-2px) !important;
    }
    
    button[id*='generate'], button[id$='Generate'] {
        background: linear-gradient(135deg, #4a6baf, #7e57c2) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-top: 1.5rem !important;
        width: 100% !important;
    }
    
    button[id*='generate']:hover, button[id$='Generate']:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Override dropdown styling */
    select, .gr-dropdown {
        appearance: none !important;
        background-color: white !important;
        background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234a6baf' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e") !important;
        background-repeat: no-repeat !important;
        background-position: right 1rem center !important;
        background-size: 1em !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        padding-right: 2.5rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        height: auto !important;
        min-height: 48px !important;
    }
    
    select:hover, .gr-dropdown:hover {
        border-color: #4a6baf !important;
    }
    
    select:focus, .gr-dropdown:focus {
        border-color: #4a6baf !important;
        box-shadow: 0 0 0 3px rgba(74, 107, 175, 0.2) !important;
        outline: none !important;
    }
    
    /* Improved two-column layout for wider screens */
    @media (min-width: 768px) {
        .two-columns {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 1.5rem !important;
        }
        
        .form-row {
            display: flex !important;
            gap: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        .form-row > * {
            flex: 1 !important;
        }
    }
    """
    
    with gr.Blocks(title="VoiceScribe Studio", css=css_test) as app:
        with gr.Row(equal_height=True, elem_classes=["header-row"]):
            with gr.Column(scale=1, min_width=40):
                gr.HTML(f'<img src="{logo_data_uri}" alt="Logo" style="width:60px; height:60px; margin-top:0px;">')
            with gr.Column(scale=20):
                gr.Markdown("# VoiceScribe Studio")
                gr.Markdown("Transform your ideas into professional educational content with AI-powered scripts and lifelike voiceovers")
        
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
