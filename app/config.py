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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Model Configuration
OPENAI_MODEL = clean_id(os.getenv("OPENAI_MODEL", "gpt-4o"))
DEEPSEEK_MODEL = clean_id(os.getenv("DEEPSEEK_MODEL", "deepseek-chat")) # Default DeepSeek model

# ElevenLabs Voice Configuration
VOICE_ID = clean_id(os.getenv("VOICE_ID", "default"))

# Preset Voice Options (with comment cleanup)
PRESET_VOICES = {
    # Male Voices
    "Dan Teacher - Natural": clean_id(os.getenv("MALE_VOICE_1", "jn5Dym9tbXQdxJRlyYzZ")),  # Yousician music instructor in a natural tone of voice
    "Dan Teacher - Neutral": clean_id(os.getenv("MALE_VOICE_2", "CMtJJeUfoLE6mZYBmsFl")),  # Yousician music instructor in a neutral tone of voice
    "Dan Teacher - Upbeat": clean_id(os.getenv("MALE_VOICE_3", "W14NZHmEOKlltX7Dhrac")),  # Yousician music instructor in an energetic tone of voice
    "Mark - Natural": clean_id(os.getenv("MALE_VOICE_4", "UgBBYS2sOqTuMpoF3BR0")),  # English (American), Casual, Young, Male, Conversational
    
    # Female Voices
    "Cassidy": clean_id(os.getenv("FEMALE_VOICE_1", "56AoDkrOh6qfVPDXZ7Pt")),  # A confident female podcaster with plethora of experience in the music industry
    "Jessica Anne - Conversational": clean_id(os.getenv("FEMALE_VOICE_2", "g6xIsTj2HwM6VR4iXFCw")),  # Friendly and Conversational Female voice. Articulate, Confident and Helpful
    "Lori - Happy": clean_id(os.getenv("FEMALE_VOICE_3", "TbMNBJ27fH2U0VgpSNko")),  # Optimistic, smiling, and carefree young woman with slight vocal fry
    "Rachel": clean_id(os.getenv("FEMALE_VOICE_4", "21m00Tcm4TlvDq8ikWAM")),  # Original Rachel voice kept as the fourth female option
}

# Print cleaned values for debugging
print(f"Cleaned voice IDs:")
for name, voice_id in PRESET_VOICES.items():
    print(f"  {name}: '{voice_id}'")
print(f"Cleaned OpenAI model: '{OPENAI_MODEL}'")
print(f"Cleaned DeepSeek model: '{DEEPSEEK_MODEL}'")

# Check if required API keys are present
def validate_config():
    """Validate that required configuration parameters are set."""
    missing_keys = []
    
    if not OPENAI_API_KEY:
        missing_keys.append("OPENAI_API_KEY")
    
    if not ELEVENLABS_API_KEY:
        missing_keys.append("ELEVENLABS_API_KEY")
        
    if not DEEPSEEK_API_KEY:
        missing_keys.append("DEEPSEEK_API_KEY")
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True
