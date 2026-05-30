#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 to run this application."
    exit 1
fi

# Try to run using virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 main.py
