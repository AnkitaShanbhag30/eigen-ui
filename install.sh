#!/bin/bash

echo "🚀 Setting up Brand Content Generator..."

# Check if Python 3.11+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
fi

# Ensure data directories exist
echo "📁 Creating data directories..."
mkdir -p data/brands data/assets data/drafts

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Test the setup: python test_setup.py"
echo "4. Try the CLI: python cli.py --help"
echo "5. Run the demo: python demo.py"
echo ""
echo "To activate the environment in the future:"
echo "  source .venv/bin/activate" 