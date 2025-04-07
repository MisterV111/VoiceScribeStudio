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
    /* Info text styling */
    .info-text {
        font-size: 0.85rem !important;
        color: #6c757d !important; /* Use Gradio's secondary text color */
        margin-top: -10px !important; /* Adjust spacing relative to the File component */
        margin-bottom: 10px !important;
        padding-left: 1px !important; /* Align with other component labels */
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
    .admin-bar-container {
        margin-bottom: 20px !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    .admin-bar {
        background: #3b355d !important;
        color: white !important;
        padding: 15px 20px !important;
        font-weight: bold !important;
        text-align: center !important;
        margin: 0 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
    }
    .admin-bar h1 {
        font-size: 1.8rem !important;
        margin: 0 !important;
        color: white !important;
    }
    
    /* Humanize feature styling */
    .humanize-container {
        background-color: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    .humanize-explainer {
        background-color: #f8f9ff !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-bottom: 20px !important;
        border-left: 4px solid #5e166a !important;
    }
    
    .humanize-explainer h4 {
        color: #5e166a !important;
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        font-weight: 600 !important;
    }
    
    .humanize-explainer p {
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        font-size: 0.9rem !important;
    }
    
    .humanize-explainer ul {
        margin-bottom: 0 !important;
        padding-left: 20px !important;
    }
    
    .humanize-explainer li {
        margin-bottom: 5px !important;
        font-size: 0.9rem !important;
    }
    
    .humanize-preview {
        display: flex !important;
        flex-direction: row !important;
        gap: 20px !important;
        margin-bottom: 0 !important;
    }
    
    .humanize-original, .humanize-transformed {
        flex: 1 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        background-color: #f8f9fb !important;
    }
    
    .humanize-original h4, .humanize-transformed h4 {
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        color: #3b355d !important;
        font-weight: 600 !important;
    }
    
    .script-content {
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        white-space: pre-wrap !important;
        max-height: 500px !important;
        overflow-y: auto !important;
        padding: 10px !important;
        background-color: white !important;
        border-radius: 6px !important;
        border: 1px solid #e0e4e9 !important;
    }
    
    .humanize-transformed {
        background-color: #f8f9ff !important;
        border-left: 4px solid #5e166a !important;
    }
    
    .humanize-pause {
        background-color: #e5e7ff !important;
        border-radius: 4px !important;
        padding: 2px 4px !important;
        color: #4338ca !important;
        font-family: monospace !important;
        font-size: 0.9em !important;
    }
    
    .humanize-emphasis {
        color: #5e166a !important;
        font-weight: bold !important;
    }
    
    .humanize-strong-emphasis {
        color: #5e166a !important;
        font-weight: bold !important;
        background-color: rgba(94, 22, 106, 0.1) !important;
        border-radius: 4px !important;
        padding: 1px 3px !important;
    }
    
    .humanize-warning {
        background-color: #fee2e2 !important;
        color: #b91c1c !important;
        border-radius: 4px !important;
        padding: 2px 4px !important;
        font-family: monospace !important;
        font-size: 0.9em !important;
    }
    
    .humanize-narration {
        background-color: #ecfdf5 !important;
        color: #047857 !important;
        border-radius: 4px !important;
        padding: 2px 4px !important;
        font-style: italic !important;
    }
    
    .humanize-emotion {
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border-radius: 4px !important;
        padding: 2px 4px !important;
        font-family: monospace !important;
        font-size: 0.9em !important;
    }
    
    /* Generated audio files styling */
    .generated-formats-container {
        background-color: white !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* File types info styling */
    .file-types-info {
        background-color: #f8f9fb !important;
        border: 1px solid #e0e4e9 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        font-size: 0.9rem !important;
    }
    
    /* File info box styling for side-by-side layout */
    .file-info-box {
        background-color: #f8f9fb !important;
        border: 1px solid #e0e4e9 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 10px 5px 15px 5px !important;
        height: 100% !important;
        font-size: 0.9rem !important;
    }
    
    .file-info-box h3 {
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        color: #3b355d !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    /* Compact file info styling */
    .compact-info-row {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    
    .compact-file-info {
        background-color: #f8f9fb !important;
        border: 1px solid #e0e4e9 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin: 2px !important;
        font-size: 0.85rem !important;
    }
    
    .compact-file-info h3 {
        margin-top: 0 !important;
        margin-bottom: 5px !important;
        color: #3b355d !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    /* Ultra-compact file info styling to match example */
    .file-info-container {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    .ultra-compact-info {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .file-info-wrapper {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        background-color: #f8f9fb !important;
        border: 1px solid #e0e4e9 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    
    .file-type-section, .file-limit-section {
        padding: 0 10px !important;
    }
    
    .file-type-section {
        flex: 3 !important;
        border-right: 1px solid #e0e4e9 !important;
    }
    
    .file-limit-section {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    
    .file-info-wrapper h4 {
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        color: #3b355d !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    .file-info-wrapper p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
    }
    
    .file-types-info h3 {
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        color: #3b355d !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    .file-types-info ul, .file-types-info li {
        margin-bottom: 5px !important;
    }
    
    .warning-text {
        background-color: #fff7ed !important;
        border-left: 4px solid #f59e0b !important;
        padding: 10px 15px !important;
        margin-bottom: 15px !important;
        color: #92400e !important;
        font-weight: 500 !important;
    }
    
    .success-text {
        background-color: #ecfdf5 !important;
        border-left: 4px solid #10b981 !important;
        padding: 10px 15px !important;
        margin-bottom: 15px !important;
        color: #065f46 !important;
        font-weight: 500 !important;
    }
    
    .info-text {
        background-color: #f0f9ff !important;
        border-left: 4px solid #3b82f6 !important;
        padding: 10px 15px !important;
        margin-bottom: 15px !important;
        color: #1e40af !important;
        font-weight: 500 !important;
    }
    
    .url-extraction-note {
        margin-top: 5px !important;
        margin-bottom: 15px !important;
    }
    
    .url-note {
        padding: 8px 12px !important;
        background-color: #f8fafc !important;
        border: 1px dashed #cbd5e1 !important;
        border-radius: 6px !important;
    }
    
    .url-note p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        color: #475569 !important;
        line-height: 1.4 !important;
    }
    
    .youtube-extraction-note {
        margin-top: 5px !important;
        margin-bottom: 15px !important;
    }
    
    .youtube-note {
        padding: 8px 12px !important;
        background-color: #fdf2f8 !important;
        border: 1px dashed #f472b6 !important;
        border-radius: 6px !important;
    }
    
    .youtube-note p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        color: #9d174d !important;
        line-height: 1.4 !important;
    }
    
    .generated-files-header {
        background: linear-gradient(135deg, #5e166a 0%, #3b355d 100%) !important;
        color: white !important;
        padding: 16px 24px !important;
        border-radius: 12px 12px 0 0 !important;
        margin: 0 !important;
    }
    
    .generated-files-header h3 {
        margin: 0 0 8px 0 !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        color: white !important;
    }
    
    .generated-files-header p {
        margin: 0 !important;
        opacity: 0.9 !important;
        font-size: 0.9rem !important;
        color: white !important;
    }
    
    .generated-files-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
        gap: 16px !important;
        padding: 20px !important;
        background-color: #f8faff !important;
    }
    
    .audio-file-card {
        display: flex !important;
        align-items: center !important;
        background-color: white !important;
        border-radius: 10px !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .audio-file-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12) !important;
    }
    
    .format-icon {
        font-size: 2rem !important;
        margin-right: 16px !important;
        width: 40px !important;
        text-align: center !important;
    }
    
    .format-details {
        flex: 1 !important;
    }
    
    .format-name {
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #3b355d !important;
        margin-bottom: 4px !important;
    }
    
    .file-info {
        font-size: 0.85rem !important;
        color: #666 !important;
        margin-bottom: 8px !important;
    }
    
    .download-link {
        display: inline-block !important;
        background-color: #5e166a !important;
        color: white !important;
        text-decoration: none !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }
    
    .download-link:hover {
        background-color: #4a1255 !important;
    }
    
    /* Pending format styles */
    .pending-format {
        background-color: #f8f9ff !important;
        border: 1px dashed #aab4cf !important;
    }
    
    .pending-label {
        display: inline-block !important;
        background-color: #e9edf7 !important;
        color: #4a5568 !important;
        padding: 4px 8px !important;
        font-size: 0.75rem !important;
        border-radius: 20px !important;
        margin-top: 4px !important;
        font-weight: 500 !important;
        border: 1px solid #d0d7e8 !important;
    }
    
    /* Audio preview player styles */
    .audio-preview-container {
        background-color: white !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        text-align: center !important;
    }
    
    .preview-title {
        color: #3b355d !important;
        margin-top: 0 !important;
        margin-bottom: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .audio-preview-player {
        width: 100% !important;
        max-width: 600px !important;
        height: 40px !important;
        outline: none !important;
    }
    
    /* Style the audio controls to match the theme */
    audio::-webkit-media-controls-panel {
        background-color: #f8f9ff !important;
    }
    
    audio::-webkit-media-controls-play-button {
        background-color: #5e166a !important;
        border-radius: 50% !important;
    }
    
    /* Compact File Upload Component */
    #document-upload-input,
    #document-upload-input .file-preview-holder {
        min-height: 80px !important; /* Reduce minimum height */
        height: auto !important;
    }
    #document-upload-input .upload-button,
    #document-upload-input .upload-button p {
        padding: 8px 12px !important; /* Reduce button padding */
        font-size: 0.9rem !important; /* Slightly smaller font */
    }
    #document-upload-input .upload-button svg {
        width: 20px !important; /* Smaller icon */
        height: 20px !important;
    }
    #document-upload-input .file-preview-holder .grid-wrap {
        gap: 5px !important;
    }
    #document-upload-input .file-preview-holder .file {
        padding: 5px !important;
    }
    /* Side-by-side upload and info styling */
    .upload-info-container {
        gap: 15px !important;
        margin-bottom: 15px !important;
    }
    
    .upload-area-column {
        min-width: 0 !important; /* Allow column to shrink */
    }
    
    .file-info-column {
        min-width: 0 !important; /* Allow column to shrink */
    }
    
    .side-by-side-info {
        height: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .file-info-panel {
        background-color: #f8f9fb !important;
        border: 1px solid #e0e4e9 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    .file-type-section h4, .file-size-section h4 {
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        color: #3b355d !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    .file-types {
        margin: 0 !important;
        padding-left: 0 !important;
    }
    
    .file-types p {
        margin: 0 0 3px 0 !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
    }
    
    /* Checkmark styling */
    .checkmark {
        display: inline-block !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        text-align: center !important;
        line-height: 18px !important;
        margin-right: 8px !important;
        font-weight: bold !important;
        background-color: #f0f0f0 !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
    }
    
    .checkmark.selected {
        background-color: #ff7b31 !important;
        color: white !important;
        border-color: #ff7b31 !important;
    }
    
    .file-size-section {
        margin-top: 15px !important;
    }
    
    .file-size-section p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #5e166a !important;
    }
    
    /* Make file upload component more compact */
    .upload-area-column [data-testid="file"] {
        min-height: 150px !important;
        height: auto !important;
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
                    
                    with gr.Row():
                        login_button = gr.Button("Login", variant="primary", elem_classes=["login-button"])
                        back_button = gr.Button("Back to Main App")
            
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
        print("Starting VoiceScribe Studio on http://0.0.0.0:7862")
        app.launch(
            server_name="0.0.0.0",
            server_port=7862,
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
