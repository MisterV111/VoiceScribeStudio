#!/bin/bash

# This is a compatibility script that calls the main script in the scripts directory
echo "Starting VoiceScribe Studio..."
bash ./scripts/start.sh

# Exit with the same code as the main script
exit $? 