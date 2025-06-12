import os
import sys
import json
import base64
import traceback
import logging
import gradio as gr
from dotenv import load_dotenv

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', mode='a') if os.path.exists('logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import constants from config (should happen after load_dotenv)
from app.config import (
    ELEVENLABS_API_KEY, DEEPSEEK_API_KEY, ANTHROPIC_API_KEY,
    DEEPSEEK_MODEL, CLAUDE_MODEL, VOICE_ID, PRESET_VOICES,
    validate_config
)

# Admin credentials - should be in environment variables
# For security, these should be moved to the config file later
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Tester credentials for shared testing access
TESTER_USERNAME = os.getenv("TESTER_USERNAME", "voicescribe_tester") 
TESTER_PASSWORD = os.getenv("TESTER_PASSWORD", "demo2024_vs")

# Import utility functions
from app.utils.token_counter import token_tracker

# Import elevenlabs client functions
from app.utils.elevenlabs_client import load_all_voices
from app.components.voiceover_generator import set_voice_data as voiceover_set_voice_data

# Import script generation functions
from app.utils.llm_clients import generate_script

# Import components
from app.components.script_generator import create_script_generator_tab
from app.components.script_editor import create_script_editor_tab
from app.components.voiceover_generator import create_voiceover_tab
from app.components.token_dashboard import create_token_dashboard
from app.components.testing_dashboard import create_testing_dashboard

# Global variables for voice data
preset_voice_names = []
preset_voice_ids = []
voice_names = []
voice_ids = []

# Initialize token tracker
# token_tracker = TokenTracker()  # Already initialized in token_counter.py

def set_voice_data(p_names, p_ids, v_names, v_ids):
    """Set global voice data variables"""
    global preset_voice_names, preset_voice_ids, voice_names, voice_ids
    preset_voice_names = p_names
    preset_voice_ids = p_ids
    voice_names = v_names
    voice_ids = v_ids
    print(f"set_voice_data set {len(preset_voice_names)} preset voices")

def setup_directories():
    """Make sure required directories exist"""
    # Core directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Output directories with improved organization
    os.makedirs("output/scripts", exist_ok=True)
    os.makedirs("output/audio", exist_ok=True)
    os.makedirs("output/audio/ogg", exist_ok=True)
    os.makedirs("output/audio/mp3", exist_ok=True)
    os.makedirs("output/audio/wav", exist_ok=True)
    os.makedirs("output/batch", exist_ok=True)
    
    # Create token log if it doesn't exist
    token_log_path = os.path.join("data", "token_log.json")
    if not os.path.exists(token_log_path):
        with open(token_log_path, "w") as f:
            json.dump([], f)

def get_css():
    """Get custom CSS for the Gradio app"""
    return """
    .login-container {
            width: 100%;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            background-color: white;
    }
    .login-title {
            text-align: center;
            margin-bottom: 20px;
    }
    .error-message {
            color: red;
            text-align: center;
            margin-top: 10px;
        }
    .admin-bar-container {
            background-color: #6F42C1;
            color: white;
            padding: 10px 20px;
            margin-bottom: 20px;
            border-radius: 5px;
    }
    .admin-bar {
            margin: 0;
            color: white;
        }
        .analytics-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
        }
        #admin-link-btn {
            position: absolute;
            top: 10px;
            right: 20px;
            color: #6F42C1;
            border: none;
            background: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.875rem;
        }
        .admin-button {
            color: #6F42C1 !important;
            border: 1px solid #6F42C1 !important;
        background-color: white !important;
            border-radius: 4px !important;
            padding: 5px 10px !important;
        font-weight: 600 !important;
            margin-left: auto !important;
            margin-right: 10px !important;
            margin-bottom: 10px !important;
        display: inline-block !important;
        }
        .admin-button:hover {
            background-color: #f8f4ff !important;
        }
        .link-button {
            border: none !important;
            background: none !important;
            color: #6F42C1 !important;
            cursor: pointer !important;
            padding: 0 !important;
        font-weight: 600 !important;
            font-size: 0.875rem !important;
            text-align: right !important;
        }
        .link-button:hover {
            text-decoration: underline !important;
        }
    """

def load_banner():
    """Load the banner image as base64"""
    banner_path = os.path.join(os.path.dirname(__file__), "assets", "VoiceScribe Studio Banner.png")
    with open(banner_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def create_banner(base64_banner):
    """Create the banner component"""
    return gr.HTML(f'<img src="data:image/png;base64,{base64_banner}" style="width:100%; margin-bottom:20px; border-radius:10px;">')

def setup_app_environment():
    """Set up all prerequisites for the app"""
    try:
        logger.info("Setting up directories...")
        setup_directories()
        
        # Load voices using the consolidated function from elevenlabs_client.py
        logger.info("Loading voice configurations...")
        preset_voice_names, preset_voice_ids, voice_names, voice_ids = load_all_voices()
        logger.info(f"Loaded {len(preset_voice_names)} preset voices and {len(voice_names)} total voices")
        print(f"Loaded {len(preset_voice_names)} preset voices")
        print(f"First few voice names: {preset_voice_names[:3] if preset_voice_names else []}")
        
        # Set voice data in both the main app and the voiceover component
        set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
        voiceover_set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
        logger.info("Voice data configured successfully")
        print(f"Voice data passed to voiceover component")
        
        return load_banner()
        
    except Exception as e:
        logger.error(f"Error setting up app environment: {str(e)}", exc_info=True)
        # Continue with minimal setup if voice loading fails
        print(f"Warning: Some features may not work properly due to setup error: {str(e)}")
        return load_banner()

def verify_credentials(username, password, user_type="tester"):
    """Verify user credentials based on user type"""
    if user_type == "admin":
        return (username == ADMIN_USERNAME and password == ADMIN_PASSWORD)
    elif user_type == "tester":
        return (username == TESTER_USERNAME and password == TESTER_PASSWORD)
    return False

def create_gradio_app():
    """Create the Gradio app with all components"""
    banner_base64 = load_banner()
    
    with gr.Blocks(title="VoiceScribe Studio", css=get_css()) as app:
        # Create a state variable to track the current interface
        current_interface = gr.State("public")
        is_authenticated = gr.State(False)
        
        # Public interface components (shown when authenticated as tester or when not authenticated)
        with gr.Column(visible=True) as public_interface:
            # Create the banner
            create_banner(banner_base64)
            
            # Authentication status and login link
            with gr.Row():
                with gr.Column(scale=10):
                    auth_status = gr.Markdown("Please login to access VoiceScribe Studio features.", visible=True)
                with gr.Column(scale=1):
                    login_link = gr.Button(
                        "🔒 Login", 
                        elem_classes=["admin-button"],
                        scale=0,
                        size="sm"
                    )
            
            # Main application content (hidden until authenticated)
            main_content = gr.Column(visible=False)
            with main_content:
                # Create the main tabs
                with gr.Tabs():
                    # Create tabs using the component functions
                    script_output, script_file_output = create_script_generator_tab()
                    edit_script_input, edited_script_output = create_script_editor_tab()
                    voiceover_script, voiceover_status, ogg_output, mp3_output, wav_output, batch_output = create_voiceover_tab()
                    
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
        
        # Login form (for both testers and admins)
        with gr.Column(visible=False) as login_form:
            # Create the banner
            create_banner(banner_base64)
            
            with gr.Column(elem_classes=["login-container"]):
                gr.Markdown("# 🔒 VoiceScribe Studio Login", elem_classes=["login-title"])
                gr.Markdown("Please enter your credentials to access VoiceScribe Studio.")
                gr.Markdown("*Testers will have full access to all features. Admins will have access to analytics and testing tools.*")
                username = gr.Textbox(label="Username", placeholder="Enter your username")
                password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                error_message = gr.Markdown(visible=False, value="⚠️ Incorrect username or password", elem_classes=["error-message"])
                
                with gr.Row(equal_height=True):
                    login_button = gr.Button("Login", variant="primary", size="lg")
                    back_button = gr.Button("Back to Public View", size="lg")
        
        # Admin dashboard
        with gr.Column(visible=False) as admin_dashboard:
            # Create the banner
            create_banner(banner_base64)
            
            # Admin title bar
            with gr.Column(elem_classes=["admin-bar-container"]):
                gr.Markdown("# Admin Dashboard", elem_classes=["admin-bar"])
            
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
                    token_dashboard = create_token_dashboard()
                
                # Add testing dashboard
                with gr.TabItem("Testing Suite"):
                    create_testing_dashboard()
        
        # Create UI handlers
        def switch_to_login():
            return {
                public_interface: gr.update(visible=False),  
                login_form: gr.update(visible=True),   
                admin_dashboard: gr.update(visible=False),
                auth_status: gr.update(visible=True),
                main_content: gr.update(visible=False),
                current_interface: "login",                   
                is_authenticated: False                      
            }

        def switch_to_public():
            return {
                public_interface: gr.update(visible=True),   
                login_form: gr.update(visible=False),  
                admin_dashboard: gr.update(visible=False),
                auth_status: gr.update(visible=True),
                main_content: gr.update(visible=False),
                current_interface: "public",                   
                is_authenticated: False                      
            }
        
        def check_login(username_value, password_value):
            print(f"Checking login for username: {username_value}")
            
            # Check admin credentials first
            if verify_credentials(username_value, password_value, "admin"):
                print("Admin authentication successful")
                return {
                    public_interface: gr.update(visible=False),  
                    login_form: gr.update(visible=False),  
                    admin_dashboard: gr.update(visible=True),   
                    error_message: gr.update(visible=False),
                    auth_status: gr.update(visible=False),
                    main_content: gr.update(visible=False),
                    current_interface: "admin",                   
                    is_authenticated: True                      
                }
            # Check tester credentials
            elif verify_credentials(username_value, password_value, "tester"):
                print("Tester authentication successful")
                return {
                    public_interface: gr.update(visible=True),   
                    login_form: gr.update(visible=False),  
                    admin_dashboard: gr.update(visible=False),   
                    error_message: gr.update(visible=False),
                    auth_status: gr.update(visible=False),
                    main_content: gr.update(visible=True),
                    current_interface: "public",                   
                    is_authenticated: True                      
                }
            else:
                print("Authentication failed")
                return {
                    public_interface: gr.update(visible=False),  
                    login_form: gr.update(visible=True),  
                    admin_dashboard: gr.update(visible=False),  
                    error_message: gr.update(visible=True),
                    auth_status: gr.update(visible=True),
                    main_content: gr.update(visible=False),
                    current_interface: "login",                   
                    is_authenticated: False                      
                }
        
        # Connect all the event handlers
        login_link.click(
            fn=lambda: None,
            inputs=[],
            outputs=[],
            js="() => { window.location.href = window.location.origin + '?view=login'; }"
        )
        
        # We need to wrap the dictionary-returning functions to convert to list format
        def wrap_check_login(username_value, password_value):
            result = check_login(username_value, password_value)
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[error_message],
                result[auth_status],
                result[main_content],
                result[current_interface],
                result[is_authenticated]
            ]
            
        def wrap_switch_to_public():
            result = switch_to_public()
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[auth_status],
                result[main_content],
                result[current_interface],
                result[is_authenticated]
            ]
            
        def wrap_switch_to_login():
            result = switch_to_login()
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[auth_status],
                result[main_content],
                result[current_interface],
                result[is_authenticated]
            ]
        
        login_button.click(
            fn=wrap_check_login,
            inputs=[username, password],
            outputs=[public_interface, login_form, admin_dashboard, error_message, auth_status, main_content, current_interface, is_authenticated]
        )
        
        back_button.click(
            fn=wrap_switch_to_public,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, auth_status, main_content, current_interface, is_authenticated]
        )
        
        return_btn.click(
            fn=wrap_switch_to_public,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, auth_status, main_content, current_interface, is_authenticated]
        )
        
        logout_btn.click(
            fn=wrap_switch_to_login,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, auth_status, main_content, current_interface, is_authenticated]
        )
        
        # Add load handler
        @app.load(outputs=[public_interface, login_form, admin_dashboard, auth_status, main_content, current_interface, is_authenticated], api_name=False)
        def on_load(request: gr.Request):
            if request and hasattr(request, "query_params") and (request.query_params.get("view") == "login" or request.query_params.get("view") == "admin"):
                return [
                    gr.update(visible=False),  # public_interface
                    gr.update(visible=True),   # login_form
                    gr.update(visible=False),  # admin_dashboard
                    gr.update(visible=True),   # auth_status (not used in login form)
                    gr.update(visible=False),  # main_content
                    "login",                   # current_interface
                    False                      # is_authenticated
                ]
            return [
                gr.update(visible=True),    # public_interface
                gr.update(visible=False),   # login_form
                gr.update(visible=False),   # admin_dashboard
                gr.update(visible=True),    # auth_status (show login message)
                gr.update(visible=False),   # main_content (hidden until login)
                "public",                   # current_interface
                False                       # is_authenticated
            ]
            
    return app

def launch_app(app):
    """Launch the application"""
    # Use Railway's PORT environment variable if available, otherwise fallback to local development ports
    railway_port = os.getenv("PORT")
    
    if railway_port:
        # Railway deployment - use the provided port
        port = int(railway_port)
        print(f"Starting VoiceScribe Studio on Railway port: {port}")
        app.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            show_error=True
        )
    else:
        # Local development - try a range of ports starting from 7862
        for port in range(7862, 7872):
            try:
                print(f"Starting VoiceScribe Studio on http://0.0.0.0:{port}")
                app.launch(
                    server_name="0.0.0.0",
                    server_port=port,
                    share=False,
                    show_error=True
                )
                # If launch is successful, break out of the loop
                break
            except OSError as e:
                if "address already in use" in str(e).lower() and port < 7871:
                    print(f"Port {port} is in use, trying {port+1}...")
                    continue
                else:
                    # If we've tried all ports in our range
                    if port >= 7871:
                        print("All ports in range 7862-7871 are in use. Please free up a port and try again.")
                    # Otherwise it's some other error
                    print(f"Error starting server: {str(e)}")
                    raise

def main():
    """Main function to run the application with multiple interfaces"""
    try:
        # Setup steps
        logger.info("Starting VoiceScribe Studio...")
        print("Starting VoiceScribe Studio...")
        
        # Validate configuration first
        logger.info("Validating configuration...")
        validate_config()
        
        # Setup app environment
        setup_app_environment()
        
        # Create and launch app
        logger.info("Creating Gradio application...")
        app = create_gradio_app()
        
        logger.info("Launching application...")
        launch_app(app)
        
    except ValueError as e:
        error_msg = f"Configuration error: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
        print("Please check your API keys in the environment variables.")
        print("For Railway deployment, set these in your Railway dashboard.")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)
        traceback.print_exc()
        sys.exit(1)

# Main application entry point
if __name__ == "__main__":
    main()
