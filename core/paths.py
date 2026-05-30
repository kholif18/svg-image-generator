# core/paths.py
import os
import sys
import shutil
from pathlib import Path

# Get the base directory of the application
# 1. Check if running as an AppImage
if os.environ.get('APPIMAGE'):
    BASE_DIR = Path(os.environ.get('APPIMAGE')).resolve().parent
# 2. Check if running as a frozen executable (PyInstaller)
elif getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
# 3. Running from source
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

def app_path(*parts) -> str:
    """Return an absolute path relative to the application root"""
    return str(BASE_DIR.joinpath(*parts))

def relative_to_app(path: str) -> str:
    """Convert an absolute path to a relative path if it's inside BASE_DIR"""
    if not path:
        return ""
    try:
        abs_path = Path(path).resolve()
        if abs_path.is_relative_to(BASE_DIR):
            return str(abs_path.relative_to(BASE_DIR))
    except:
        pass
    return path

def resolve_path(path: str) -> str:
    """Convert a potentially relative path to an absolute path"""
    if not path:
        return ""
    p = Path(path)
    if p.is_absolute():
        return str(p)
    
    # If it's a simple command name (no slashes), don't resolve it as a path
    if os.sep not in path and (os.altsep is None or os.altsep not in path):
        return path
        
    return app_path(path)

def ensure_portable_env():
    """Create necessary folders for a portable environment"""
    folders = [
        'config',
        'templates',
        'photos',
        'themes',
        'output/svg',
        'output/images',
        'logs'
    ]
    for folder in folders:
        os.makedirs(app_path(folder), exist_ok=True)

def find_inkscape() -> str:
    """Try to find Inkscape executable automatically"""
    # 1. Check PATH
    inkscape = shutil.which("inkscape")
    if inkscape:
        return inkscape
        
    # 2. Check common locations on Windows
    if os.name == 'nt':
        common_paths = [
            r"C:\Program Files\Inkscape\bin\inkscape.exe",
            r"C:\Program Files\Inkscape\inkscape.exe",
            r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
            r"C:\Program Files (x86)\Inkscape\inkscape.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
                
    # 3. Check common locations on Linux
    else:
        linux_paths = [
            "/usr/bin/inkscape",
            "/usr/local/bin/inkscape",
            "/snap/bin/inkscape"
        ]
        for path in linux_paths:
            if os.path.exists(path):
                return path
                
    return "inkscape" # Fallback to command name
