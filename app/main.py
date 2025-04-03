import gradio as gr
import os
import base64
from pathlib import Path
import sys

# Add the app directory to the system path
current_dir = Path(__file__).parent.resolve()
sys.path.append(str(current_dir.parent))

# Local imports
from app.config import validate_config, DEEPSEEK_MODEL, CLAUDE_MODEL
from app.utils.elevenlabs_client import get_voices
from app.components.script_generator import create_script_generator_tab
from app.components.script_editor import create_script_editor_tab
from app.components.voiceover_generator import create_voiceover_tab, set_voice_data
from app.components.testing_dashboard import create_testing_dashboard
from app.components.token_dashboard import create_token_dashboard

# Constants for authentication
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # You should change this to a more secure password in production

def setup_directories():
    """Create necessary output directories"""
    os.makedirs("output/scripts", exist_ok=True)
    os.makedirs("output/audio", exist_ok=True)

def load_voices():
    """Load voices from ElevenLabs"""
    try:
        voices_response = get_voices()
        
        # Handle the response, which is now a list of dictionaries with 'name' and 'voice_id' keys
        if not voices_response or not isinstance(voices_response, list):
            print("Warning: Invalid or empty voice response received from ElevenLabs API.")
            return [], [], [], []
            
        all_voices = voices_response
        
        preset_voice_map = {
            "Dan Teacher - Natural": "jn5Dym9tbXQdxJRlyYzZ", 
            "Dan Teacher - Neutral": "CMtJJeUfoLE6mZYBmsFl", 
            "Dan Teacher - Upbeat": "W14NZHmEOKlltX7Dhrac", 
            "Mark - Natural": "UgBBYS2sOqTuMpoF3BR0",
            "Cassidy": "56AoDkrOh6qfVPDXZ7Pt", 
            "Jessica Anne - Conversational": "g6xIsTj2HwM6VR4iXFCw", 
            "Lori - Happy": "TbMNBJ27fH2U0VgpSNko", 
            "Rachel": "21m00Tcm4TlvDq8ikWAM"
        }
        
        preset_voice_names = []
        preset_voice_ids = []
        other_voice_names = []
        other_voice_ids = []
        
        # Ensure preset voices exist in the response and add them first
        for name, expected_id in preset_voice_map.items():
            found = False
            for voice in all_voices:
                if voice.get('name') == name and voice.get('voice_id') == expected_id:
                    preset_voice_names.append(voice.get('name'))
                    preset_voice_ids.append(voice.get('voice_id'))
                    found = True
                    break
            if not found:
                # Add as a fallback preset with the map values (allow voiceover generation without API)
                preset_voice_names.append(name)
                preset_voice_ids.append(expected_id)
                print(f"Warning: Preset voice '{name}' (ID: {expected_id}) not found in ElevenLabs account. Added as fallback.")
        
        # Add other voices, excluding presets
        for voice in all_voices:
            if voice.get('name') not in preset_voice_map:
                other_voice_names.append(voice.get('name'))
                other_voice_ids.append(voice.get('voice_id'))
        
        print(f"Successfully processed {len(all_voices)} voices. Found {len(preset_voice_names)} preset voices.")
        # Print a few found voices for confirmation
        for i, name in enumerate(other_voice_names):
            if i < 10:
                print(f"Found other voice: {name} (ID: {other_voice_ids[i]})")
            else:
                break
                
        # Ensure we have at least default voices if none found
        if not preset_voice_names:
            print("No preset voices found in API response, using default voice list")
            for name, voice_id in preset_voice_map.items():
                preset_voice_names.append(name)
                preset_voice_ids.append(voice_id)
                
        return preset_voice_names, preset_voice_ids, other_voice_names, other_voice_ids
        
    except Exception as e:
        print(f"Error loading voices: {e}")
        print("Proceeding with default preset voices for fallback")
        # Return default preset voice list for fallback
        preset_voice_names = []
        preset_voice_ids = []
        
        # Add default voices from the preset map
        preset_voice_map = {
            "Dan Teacher - Natural": "jn5Dym9tbXQdxJRlyYzZ", 
            "Dan Teacher - Neutral": "CMtJJeUfoLE6mZYBmsFl", 
            "Dan Teacher - Upbeat": "W14NZHmEOKlltX7Dhrac", 
            "Mark - Natural": "UgBBYS2sOqTuMpoF3BR0",
            "Cassidy": "56AoDkrOh6qfVPDXZ7Pt", 
            "Jessica Anne - Conversational": "g6xIsTj2HwM6VR4iXFCw", 
            "Lori - Happy": "TbMNBJ27fH2U0VgpSNko", 
            "Rachel": "21m00Tcm4TlvDq8ikWAM"
        }
        
        for name, voice_id in preset_voice_map.items():
            preset_voice_names.append(name)
            preset_voice_ids.append(voice_id)
        
        return preset_voice_names, preset_voice_ids, [], []

def get_css():
    """Get shared CSS for the application"""
    return """
    .gradio-container {
        background-color: #f8faff !important;
        font-family: 'Inter', 'Segoe UI', Roboto, -apple-system, system-ui, BlinkMacSystemFont, sans-serif !important;
    }
    .header-row {
        padding: 0 !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: white !important;
    }
    /* Remove margin/padding from banner container */
    .header-banner {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 0 !important;
    }
    /* Remove margin from Markdown component */
    .header-banner .prose {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Make sure the image spans full width */
    .header-banner img {
        display: block !important;
        width: 100% !important;
        border-radius: 12px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Navigation container styling */
    .nav-container {
        margin-bottom: 1.5rem !important;
        align-items: flex-end !important;
    }
    /* Style buttons that should look like links */
    button.link-button {
        background: none !important;
        color: #0066cc !important;
        border: none !important;
        padding: 0 !important;
        font: inherit !important;
        text-decoration: none !important;
        cursor: pointer !important;
        text-align: right !important;
        box-shadow: none !important;
        margin-top: 0 !important;
        margin-bottom: 10px !important;
    }
    button.link-button:hover {
        text-decoration: underline !important;
        background: none !important;
    }
    #admin-link-btn {
        margin-left: auto !important;
        display: block !important;
    }
    /* Remove test suite button styling as it's defined inline now */
    button.primary {
        background: #5e166a !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 12px rgba(94, 22, 106, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    button[id*='generate'], button[id$='Generate'] {
        background: #5e166a !important;
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
        background: #5e166a !important;
        box-shadow: 0 4px 8px rgba(94, 22, 106, 0.3) !important;
    }
    .gradio-box, .gradio-group, .gradio-accordion {
        border-radius: 12px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12) !important;
        border: none !important;
        overflow: hidden;
        transition: all 0.3s ease;
        background-color: white !important;
    }
    /* Script output container styling */
    .script-output-container textarea {
        min-height: 620px !important;
        height: 100% !important;
    }
    .script-output-container > label {
        margin-bottom: 10px !important;
    }
    /* Edited script output container styling */
    .edited-script-output-container textarea {
        min-height: 620px !important;
        height: 100% !important;
    }
    .edited-script-output-container > label {
        margin-bottom: 10px !important;
    }
    /* Button alignment fix */
    .gradio-column {
        display: flex !important;
        flex-direction: column !important;
    }
    .gradio-column > .gradio-button {
        margin-top: auto !important;
    }
    .gradio-column > .gradio-row:last-child {
        margin-top: auto !important;
        margin-bottom: 0 !important;
    }
    /* Reduce space at bottom of tabs */
    .tabitem {
        padding-bottom: 1rem !important;
    }
    /* Login container styling */
    .login-container {
        max-width: 500px !important;
        margin: 80px auto 0 auto !important;
        padding: 30px !important;
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
    }
    .login-title {
        color: #4a2a5a !important;
        font-size: 1.5rem !important;
        margin-bottom: 20px !important;
        text-align: center !important;
    }
    .login-button {
        background: #5e166a !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .error-message {
        color: #d32f2f !important;
        font-weight: 500 !important;
        text-align: center !important;
        margin-top: 10px !important;
    }
    /* Admin bar styling */
    .admin-bar {
        background-color: #3a0647 !important;
        color: white !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        border-radius: 8px !important;
    }
    """

def create_banner(base64_banner):
    """Create the banner component with the given base64 encoded image"""
    with gr.Row(elem_classes=["header-row"]):
        banner_html = f'<img src="data:image/png;base64,{base64_banner}" alt="VoiceScribe Studio Banner">'
        gr.Markdown(banner_html, elem_classes=["header-banner"])

def main():
    """Main function to run the application with multiple interfaces"""
    try:
        # Print diagnostic information
        print(f"Starting application...")
        print(f"Using DeepSeek model: {DEEPSEEK_MODEL}")
        print(f"Using Claude model: {CLAUDE_MODEL}")
        
        # Validate configuration
        validate_config()
        
        # Setup necessary directories
        setup_directories()
        
        # Load voices
        preset_voice_names, preset_voice_ids, voice_names, voice_ids = load_voices()
        set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
        
        # Load the banner image as base64 to avoid any file path issues
        banner_path = os.path.join(os.path.dirname(__file__), "assets", "VoiceScribe Studio Banner.png")
        with open(banner_path, "rb") as img_file:
            banner_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Create a single Gradio app with interface switching
        with gr.Blocks(title="VoiceScribe Studio", css=get_css()) as app:
            # Create a state variable to track the current interface
            current_interface = gr.State("public")
            is_authenticated = gr.State(False)
            
            # Public interface components
            with gr.Column(visible=True) as public_interface:
                # Create the banner
                create_banner(banner_base64)
                
                # Add admin login link
                with gr.Row():
                    admin_link = gr.Button(
                        "Admin Login", 
                        elem_id="admin-link-btn",
                        elem_classes=["link-button"],
                        scale=0,
                        size="sm"
                    )
                
                # Create the main tabs
                with gr.Tabs():
                    # Create tabs using the component functions
                    script_output, script_file_output = create_script_generator_tab()
                    edit_script_input, edited_script_output = create_script_editor_tab()
                    voiceover_script, voiceover_status, ogg_output, mp3_output = create_voiceover_tab()
                    
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
            
            # Admin login form
            with gr.Column(visible=False) as login_form:
                # Create the banner
                create_banner(banner_base64)
                
                with gr.Column(elem_classes=["login-container"]):
                    gr.Markdown("# 🔒 Admin Authentication", elem_classes=["login-title"])
                    gr.Markdown("Please enter your credentials to access the admin dashboard.")
                    username = gr.Textbox(label="Username", placeholder="Enter your username")
                    password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                    error_message = gr.Markdown(visible=False, value="⚠️ Incorrect username or password", elem_classes=["error-message"])
                    
                    with gr.Row():
                        login_button = gr.Button("Login", variant="primary", elem_classes=["login-button"])
                        back_button = gr.Button("Back to Main App")
            
            # Admin dashboard
            with gr.Column(visible=False) as admin_dashboard:
                # Create the banner
                create_banner(banner_base64)
                
                gr.Markdown("# VoiceScribe Studio - Admin Dashboard", elem_classes=["admin-bar"])
                
                with gr.Row():
                    with gr.Column(scale=10):
                        gr.Markdown("")  # Spacer
                    with gr.Column(scale=1):
                        return_btn = gr.Button("Return to Public Interface", size="sm", elem_classes=["link-button"])
                    with gr.Column(scale=1):
                        logout_btn = gr.Button("Logout", size="sm", elem_classes=["link-button"])
                
                # Create the admin tabs
                with gr.Tabs():
                    # Add analytics tab for token usage tracking
                    with gr.TabItem("Token Analytics"):
                        gr.Markdown("## Token Usage Analytics")
                        gr.Markdown("Track API usage and costs for DeepSeek and Claude models.")
                        create_token_dashboard()
                    
                    # Add testing dashboard
                    with gr.TabItem("Testing Suite"):
                        create_testing_dashboard()
            
            # Function to switch to login form
            def switch_to_login():
                return {
                    public_interface: gr.update(visible=False),
                    login_form: gr.update(visible=True),
                    admin_dashboard: gr.update(visible=False),
                    current_interface: "login"
                }
            
            # Function to switch to public interface
            def switch_to_public():
                return {
                    public_interface: gr.update(visible=True),
                    login_form: gr.update(visible=False),
                    admin_dashboard: gr.update(visible=False),
                    current_interface: "public",
                    is_authenticated: False
                }
            
            # Function to check login credentials
            def check_login(username_value, password_value):
                print(f"Checking login for username: {username_value}")
                if username_value == ADMIN_USERNAME and password_value == ADMIN_PASSWORD:
                    print("Authentication successful")
                    return {
                        public_interface: gr.update(visible=False),
                        login_form: gr.update(visible=False),
                        admin_dashboard: gr.update(visible=True),
                        error_message: gr.update(visible=False),
                        current_interface: "admin",
                        is_authenticated: True
                    }
                else:
                    print("Authentication failed")
                    return {
                        error_message: gr.update(visible=True),
                        is_authenticated: False
                    }
            
            # Connect admin link directly
            admin_link.click(
                fn=switch_to_login,
                inputs=[],
                outputs=[public_interface, login_form, admin_dashboard, current_interface]
            )
            
            # Connect the login form buttons
            login_button.click(
                fn=check_login,
                inputs=[username, password],
                outputs=[public_interface, login_form, admin_dashboard, error_message, current_interface, is_authenticated]
            )
            
            back_button.click(
                fn=switch_to_public,
                inputs=[],
                outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated]
            )
            
            # Connect return and logout buttons
            return_btn.click(
                fn=switch_to_public,
                inputs=[],
                outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated]
            )
            
            logout_btn.click(
                fn=switch_to_login,
                inputs=[],
                outputs=[public_interface, login_form, admin_dashboard, current_interface]
            )
        
        # Launch the app
        print("Starting VoiceScribe Studio on http://0.0.0.0:7860")
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
        
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        print("Please update your .env file with the required API keys.")
    except Exception as e:
        print(f"Application error: {str(e)}")
        import traceback
        traceback.print_exc()

# Main application entry point
if __name__ == "__main__":
    main()
