@echo off
echo 🚀 Setting up Brand Content Generator...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env and add your OPENAI_API_KEY
)

REM Ensure data directories exist
echo 📁 Creating data directories...
if not exist data\brands mkdir data\brands
if not exist data\assets mkdir data\assets
if not exist data\drafts mkdir data\drafts

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your OPENAI_API_KEY
echo 2. Activate the virtual environment: .venv\Scripts\activate.bat
echo 3. Test the setup: python test_setup.py
echo 4. Try the CLI: python cli.py --help
echo 5. Run the demo: python demo.py
echo.
echo To activate the environment in the future:
echo   .venv\Scripts\activate.bat
pause 