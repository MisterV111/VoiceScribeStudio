#!/usr/bin/env python3
"""
List all voices in the app after the update
"""

import sys
sys.path.append('.')
from app.main import load_voices

def main():
    # Load voices from the app
    names, ids, _, _ = load_voices()
    
    print("UPDATED VOICES IN APP:")
    print("=" * 80)
    print(f"{'#':<3} {'VOICE NAME':<40} {'VOICE ID':<40}")
    print("=" * 80)
    
    # Print all voice names and IDs
    for i, (name, voice_id) in enumerate(zip(names, ids), 1):
        print(f"{i:<3} {name:<40} {voice_id:<40}")
    
    print(f"\nTotal: {len(names)} voices")

if __name__ == "__main__":
    main() 