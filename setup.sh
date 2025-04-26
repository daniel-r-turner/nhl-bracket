#!/bin/bash
echo "Setting up NHL Bracket project..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Run the app
echo "Running the app..."
python main.py
