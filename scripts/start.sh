#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run the application
python run.py

# Keep terminal open on error
if [ $? -ne 0 ]; then
    echo -e "\nApplication exited with an error. Press any key to close this window..."
    read -n 1
fi 