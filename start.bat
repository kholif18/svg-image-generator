@echo off
cd /d "%~dp0"

echo Starting SVG Generator...
echo.

if exist venv\Scripts\python.exe (
    set PYTHON=venv\Scripts\python.exe
) else (
    set PYTHON=python
)

%PYTHON% -c "import pandas, PyQt6, openpyxl, lxml" >nul 2>&1

if errorlevel 1 (
    echo Dependencies belum terinstall.
    echo.
    echo Jalankan:
    echo.
    echo     pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

%PYTHON% main.py

if errorlevel 1 (
    echo.
    echo Application crashed.
    pause
)