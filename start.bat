@echo off
cd /d "%~dp0"

echo Starting SVG Generator...

:: Check if virtual environment exists and use it
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe main.py
) else (
    python main.py
)

if %errorlevel% neq 0 (
    echo.
    echo Application crashed or could not start.
    pause
)
