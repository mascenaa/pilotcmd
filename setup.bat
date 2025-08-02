@echo off
echo 🚁 PilotCmd Windows Setup
echo =============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install
echo 📦 Installing PilotCmd...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .
pip install -e .[dev]

echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Set your OpenAI API key:
echo    set OPENAI_API_KEY=your-key-here
echo    or
echo    pilotcmd config --api-key your-key-here
echo.
echo 3. Test the installation:
echo    pilotcmd "list files in current directory" --dry-run
echo.
pause
