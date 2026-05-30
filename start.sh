#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Starting SVG Generator..."

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo ""
    echo "❌ Python 3 tidak ditemukan."
    echo "Silakan install Python 3 terlebih dahulu."
    exit 1
fi

# Activate venv if available
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check required modules
python3 -c "import pandas, PyQt6, openpyxl, lxml" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Dependencies belum terinstall."
    echo ""
    echo "Jalankan:"
    echo ""
    echo "    pip install -r requirements.txt"
    echo ""
    exit 1
fi

python3 main.py