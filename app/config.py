import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Helper function to clean ID values by removing comments
def clean_id(value):
    if not value:
        return value
    # Strip and remove anything after the first #
    return value.split('#')[0].strip()

# API Keys
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Removed
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 

# API Base URLs
# OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") # Removed
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1") 

# Model Configuration
# OPENAI_MODEL = clean_id(os.getenv("OPENAI_MODEL", "gpt-4o")) # Removed
DEEPSEEK_MODEL = clean_id(os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
CLAUDE_MODEL = clean_id(os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")) 

# ElevenLabs Voice Configuration
VOICE_ID = clean_id(os.getenv("VOICE_ID", "default"))

# Preset Voice Options (with comment cleanup)
PRESET_VOICES = {
    # Male Voices
    "Dan Teacher - Natural": clean_id(os.getenv("MALE_VOICE_1", "jn5Dym9tbXQdxJRlyYzZ")), 
    "Dan Teacher - Neutral": clean_id(os.getenv("MALE_VOICE_2", "CMtJJeUfoLE6mZYBmsFl")), 
    "Dan Teacher - Upbeat": clean_id(os.getenv("MALE_VOICE_3", "W14NZHmEOKlltX7Dhrac")), 
    "Mark - Natural": clean_id(os.getenv("MALE_VOICE_4", "UgBBYS2sOqTuMpoF3BR0")), 
    
    # Female Voices
    "Cassidy": clean_id(os.getenv("FEMALE_VOICE_1", "56AoDkrOh6qfVPDXZ7Pt")), 
    "Jessica Anne - Conversational": clean_id(os.getenv("FEMALE_VOICE_2", "g6xIsTj2HwM6VR4iXFCw")), 
    "Lori - Happy": clean_id(os.getenv("FEMALE_VOICE_3", "TbMNBJ27fH2U0VgpSNko")), 
    "Rachel": clean_id(os.getenv("FEMALE_VOICE_4", "21m00Tcm4TlvDq8ikWAM")), 
}

# Print cleaned values for debugging
print(f"Cleaned voice IDs:")
for name, voice_id in PRESET_VOICES.items():
    print(f"  {name}: '{voice_id}'")
# print(f"Cleaned OpenAI model: '{OPENAI_MODEL}'") # Removed
print(f"Cleaned DeepSeek model: '{DEEPSEEK_MODEL}'")
print(f"Cleaned Claude model: '{CLAUDE_MODEL}'") 
# print(f"Using OpenAI Base URL: '{OPENAI_BASE_URL or 'Default OpenAI API'}'") # Removed
print(f"Using DeepSeek Base URL: '{DEEPSEEK_BASE_URL}'")

# Check if required API keys are present
def validate_config():
    """Validate that required configuration parameters are set."""
    missing_keys = []
    
    # Core functionality keys
    if not ELEVENLABS_API_KEY:
        missing_keys.append("ELEVENLABS_API_KEY")
        
    # LLM Keys (Now require DeepSeek and Anthropic)
    if not DEEPSEEK_API_KEY:
        missing_keys.append("DEEPSEEK_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing_keys.append("ANTHROPIC_API_KEY")
        
    # # Previous check for at least one key - removed
    # llm_keys_present = False
    # if OPENAI_API_KEY:
    #     llm_keys_present = True
    # if DEEPSEEK_API_KEY:
    #     llm_keys_present = True
    # if ANTHROPIC_API_KEY:
    #     llm_keys_present = True
    # if not llm_keys_present:
    #     missing_keys.append("At least one LLM API Key (OpenAI, DeepSeek, or Anthropic)")
        
    # Base URLs are optional, models have defaults
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True
