import os
import base64
import gradio as gr
import time
import json
import tempfile
import traceback
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional, Any

# Import utility functions
from app.utils.config import (
    CLAUDE_MODEL, 
    DEEPSEEK_MODEL, 
    ADMIN_USERNAME, 
    ADMIN_PASSWORD,
    validate_config,
    save_config_to_env
)
from app.utils.token_counter import token_tracker
from app.utils.llm_clients import generate_script, analyze_content
from app.utils.tts_clients import (
    generate_audio, 
    load_voices,
    humanize_audio
)

# Import components
from app.components.voiceover_generator import set_voice_data as voiceover_set_voice_data, create_voiceover_tab
from app.components.script_generator import create_script_generator_tab
from app.components.script_editor import create_script_editor_tab
from app.components.token_dashboard import create_token_dashboard
from app.components.testing_dashboard import create_testing_dashboard

# Global voice data
voice_data = {
    "preset_voice_names": [],
    "preset_voice_ids": [],
    "voice_names": [],
    "voice_ids": []
}

def set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids):
    """Set the global voice data"""
    voice_data["preset_voice_names"] = preset_voice_names
    voice_data["preset_voice_ids"] = preset_voice_ids
    voice_data["voice_names"] = voice_names
    voice_data["voice_ids"] = voice_ids

def setup_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/scripts", exist_ok=True)
    os.makedirs("outputs/audio", exist_ok=True)
    os.makedirs("outputs/audio/ogg", exist_ok=True)
    os.makedirs("outputs/audio/mp3", exist_ok=True)
    os.makedirs("outputs/audio/wav", exist_ok=True)
    os.makedirs("outputs/batch", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Create token log if it doesn't exist
    token_log_path = os.path.join("data", "token_log.json")
    if not os.path.exists(token_log_path):
        with open(token_log_path, "w") as f:
            json.dump([], f)

def load_voices():
    """Load voice options for the dropdown menus"""
    try:
        # ElevenLabs Preset Voices (always available)
        preset_voice_names = [
            "Adam - Deep & Authoritative",
            "Antoni - Polish American Male",
            "Arnold - Crisp & Rough",
            "Bella - Soft & Breathy",
            "Callum - British Male",
            "Charlie - Casual American",
            "Clyde - Friendly & Engaging",
            "Dan Teacher - Hybrid",
            "Dan Teacher - Neutral",
            "Dan Teacher - Upbeat",
            "Daniel - British Male",
            "Dorothy - Mature & Warm",
            "Ella - Conversational American",
            "Emily - Professional & Helpful",
            "Ethan - Young American",
            "Fin - Irish Male",
            "Freya - Professional Female",
            "Giovanni - Italian Male",
            "Glinda - Southern US Accent",
            "Grace - Gentle & Soft",
            "Harry - British Teen",
            "James - Australian Male",
            "Jeremy - British Butler",
            "Joseph - Deep & Resonant",
            "Josh - Gentle & Calm",
            "Knightley - British Male",
            "Liam - North American Male",
            "Lily - British Received Pronunciation",
            "Lucy - American Teen",
            "Mark - Natural",
            "Matilda - British Teen",
            "Michael - British Male",
            "Nicole - Expressive & Emotional",
            "Oswald - Old American Male",
            "Patrick - Friendly American",
            "Rachel - Expressive American",
            "Rebecca - British Female",
            "Sam - Raspy & Gritty",
            "Sarah - NPR Presenter",
            "Serena - British Female",
            "Thomas - British Male",
            "Victoria - British Female",
            "Wright - Broadcast Male"
        ]
        
        preset_voice_ids = [
            "pFZP5JQG7iQjIQuC4Bku", # Adam
            "ErXwobaYiN019PkySvjV", # Antoni
            "VR6AewLTigWG4xSOukaG", # Arnold
            "EXAVITQu4vr4xnSDxMaL", # Bella
            "N2lVS1w4EtoT3dr4eOWO", # Callum
            "IKne3meq5aSn9XLyUdCD", # Charlie
            "2EiwWnXFnvU5JabPnv8n", # Clyde
            "jn5Dym9tbXQdxJRlyYzZ", # Dan Teacher - Hybrid
            "CMtJJeUfoLE6mZYBmsFl", # Dan Teacher - Neutral
            "W14NZHmEOKlltX7Dhrac", # Dan Teacher - Upbeat
            "GBv7mTt0atIp3Br8iCZE", # Daniel
            "ThT5KcBeYPX3keUQqHPh", # Dorothy
            "gFuV3ljmkQVQYLUJcCbO", # Ella
            "LcfcDJNUP1GQjkzn1xUU", # Emily
            "g5CIjZEefAph4nQFvHAz", # Ethan
            "D38z5RcWu1voky8WS1ja", # Fin
            "jsCqWAovK2LkecY7zXl4", # Freya
            "XB0fDUnXU5powFXDhCwa", # Giovanni
            "z2wEauNq9b0ctFbrcTFE", # Glinda
            "oWAxZDx7w5VEj9dCyTzz", # Grace
            "SOYHLrjzK2X1ezoPC6cr", # Harry
            "cRxenIsyVFC4PgXxZuqY", # James
            "tLot2LU7XsMWxMiaYlTj", # Jeremy
            "Zlb1dXrM653N07WRdFW3", # Joseph
            "TxGEqnHWrfWFTfGW9XjX", # Josh
            "mEZ8l3OV7WjuIQNpgAgh", # Knightley
            "TX3LPaxmHKxFdv7VOQHJ", # Liam
            "zrHiDhphv9ZnVXBqCLjz", # Lily
            "ZQe5CZNOzWyzPSCn5a3c", # Lucy
            "edV7AwEvM221Q5TSuK34", # Mark
            "MF3mGyEYCl7XYWbV9V6O", # Matilda
            "flq6f7yk4E4fJM5XTYuZ", # Michael
            "piTKgcLEGmPE4e6mEKli", # Nicole
            "zcAOhNBS3c14rBihAFp1", # Oswald
            "ODkYq3NQQYMi4q8qDG8T", # Patrick
            "Gr2MWxYOyJcofZYbZuxH", # Rachel
            "t0jbNlBVZ17f02VDIeMI", # Rebecca
            "yoZ06aMxZJJ28mfd3POQ", # Sam
            "pMsXgVXv3BLzUgSXRplE", # Sarah
            "onwK4e9ZLuTAKqWW03F9", # Serena
            "UYNp4YBX644gGKaV0dkt", # Thomas
            "C83I4qVd8osJAgbtpYv", # Victoria
            "dE5zNjJBUgVOCxHuKFSJ", # Wright
        ]
                
        return preset_voice_names, preset_voice_ids, preset_voice_names, preset_voice_ids
    except Exception as e:
        print(f"Error loading voices: {e}")
        return [], [], [], []

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
    setup_directories()
    
    # Load voices
    preset_voice_names, preset_voice_ids, voice_names, voice_ids = load_voices()
    print(f"Loaded {len(preset_voice_names)} preset voices")
    print(f"First few voice names: {preset_voice_names[:3]}")
    
    # Set voice data in both the main app and the voiceover component
    set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
    voiceover_set_voice_data(preset_voice_names, preset_voice_ids, voice_names, voice_ids)
    print(f"Voice data passed to voiceover component")
    
    return load_banner()

def create_gradio_app():
    """Create the Gradio app with all components"""
    banner_base64 = load_banner()
    
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
                    "🔒 Admin Login", 
                    elem_id="admin-link-btn",
                    elem_classes=["admin-button"],
                    scale=0,
                    size="sm"
                )
            
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
                
                with gr.Row(equal_height=True):
                    login_button = gr.Button("Login", variant="primary", size="lg")
                    back_button = gr.Button("Back to Main App", size="lg")
        
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
                current_interface: "login",                   
                is_authenticated: False                      
            }

        def switch_to_public():
            return {
                public_interface: gr.update(visible=True),   
                login_form: gr.update(visible=False),  
                admin_dashboard: gr.update(visible=False),  
                current_interface: "public",                   
                is_authenticated: False                      
            }
        
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
                    public_interface: gr.update(visible=False),  
                    login_form: gr.update(visible=True),  
                    admin_dashboard: gr.update(visible=False),  
                    error_message: gr.update(visible=True),  
                    current_interface: "login",                   
                    is_authenticated: False                      
                }
        
        # Connect all the event handlers
        admin_link.click(
            fn=lambda: None,
            inputs=[],
            outputs=[],
            js="() => { window.open(window.location.href + '?view=admin', '_blank'); return []; }"
        )
        
        # We need to wrap the dictionary-returning functions to convert to list format
        def wrap_check_login(username_value, password_value):
            result = check_login(username_value, password_value)
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[error_message],
                result[current_interface],
                result[is_authenticated]
            ]
            
        def wrap_switch_to_public():
            result = switch_to_public()
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[current_interface],
                result[is_authenticated]
            ]
            
        def wrap_switch_to_login():
            result = switch_to_login()
            return [
                result[public_interface],
                result[login_form],
                result[admin_dashboard],
                result[current_interface],
                result[is_authenticated]
            ]
        
        login_button.click(
            fn=wrap_check_login,
            inputs=[username, password],
            outputs=[public_interface, login_form, admin_dashboard, error_message, current_interface, is_authenticated]
        )
        
        back_button.click(
            fn=wrap_switch_to_public,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated]
        )
        
        return_btn.click(
            fn=wrap_switch_to_public,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated]
        )
        
        logout_btn.click(
            fn=wrap_switch_to_login,
            inputs=[],
            outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated]
        )
        
        # Add load handler
        @app.load(outputs=[public_interface, login_form, admin_dashboard, current_interface, is_authenticated], api_name=False)
        def on_load(request: gr.Request):
            if request and hasattr(request, "query_params") and request.query_params.get("view") == "admin":
                return [
                    gr.update(visible=False),  # public_interface
                    gr.update(visible=True),   # login_form
                    gr.update(visible=False),  # admin_dashboard
                    "login",                   # current_interface
                    False                      # is_authenticated
                ]
            return [
                gr.update(visible=True),    # public_interface
                gr.update(visible=False),   # login_form
                gr.update(visible=False),   # admin_dashboard
                "public",                   # current_interface
                False                       # is_authenticated
            ]
            
    return app

def launch_app(app):
    """Launch the application"""
    # Try a range of ports starting from 7862
    for port in range(7862, 7872):
        try:
            print(f"Starting VoiceScribe Studio on http://0.0.0.0:{port}")
            app.launch(
                server_name="0.0.0.0",
                server_port=port,
                share=False
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
        print("Starting VoiceScribe Studio...")
        setup_app_environment()
        
        # Create and launch app
        app = create_gradio_app()
        launch_app(app)
        
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        print("Please update your .env file with the required API keys.")
    except Exception as e:
        print(f"Application error: {str(e)}")
        traceback.print_exc()

# Main application entry point
if __name__ == "__main__":
    main()
