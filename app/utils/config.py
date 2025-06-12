"""
Configuration re-export module

This re-exports the configuration from the app/config.py file to maintain
proper import structure while allowing the configuration to be defined at the app level.
"""

# Re-export from the main app config
from ..config import (
    CLAUDE_MODEL,
    DEEPSEEK_MODEL,
    ELEVENLABS_API_KEY,
    DEEPSEEK_API_KEY,
    ANTHROPIC_API_KEY,
    DEEPSEEK_BASE_URL,
    VOICE_ID,
    PRESET_VOICES,
    validate_config
)

# Add admin configuration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # In production, this should be more secure

# Add helper function to save config to env
def save_config_to_env(config_updates):
    """
    Save configuration updates to the .env file
    
    Args:
        config_updates (dict): Dictionary of configuration keys and values to update
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the current .env file
        env_file_path = ".env"
        
        try:
            with open(env_file_path, "r") as env_file:
                env_lines = env_file.readlines()
        except FileNotFoundError:
            # Create a new .env file if it doesn't exist
            env_lines = []
        
        # Process each line, updating values that match config_updates keys
        updated_lines = []
        updated_keys = set()
        
        for line in env_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                updated_lines.append(line)
                continue
                
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                
                if key in config_updates:
                    updated_lines.append(f"{key}={config_updates[key]}")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Add any keys that weren't in the file
        for key, value in config_updates.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")
        
        # Write the updated file
        with open(env_file_path, "w") as env_file:
            env_file.write("\n".join(updated_lines) + "\n")
            
        return True
    except Exception as e:
        print(f"Error saving config to .env: {e}")
        return False 