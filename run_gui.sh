#!/bin/bash

# Sherlock GUI Launcher for Linux and macOS

echo "Starting Sherlock Web UI..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install it to continue."
    exit 1
fi

# Create a virtual environment if it doesn't exist (recommended for Unix)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Checking dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the application
echo "Launching Native Desktop App..."
python3 native_app.py
