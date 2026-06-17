@echo off
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Opening download page...
    echo Install Python, tick "Add Python to PATH", then run this again.
    start https://www.python.org/downloads/
    pause
    exit /b
)
echo Setting up dependencies...
python -m pip install yt-dlp imageio-ffmpeg --user --quiet --disable-pip-version-check
start "" pythonw "%~dp0ytgrab.py"
