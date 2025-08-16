# 🚀 Quick Start Guide

## One-Command Setup

### macOS/Linux
```bash
./install.sh
```

### Windows
```cmd
install.bat
```

## Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Test Your Setup

```bash
# Test basic functionality
python test_setup.py

# Run demo (creates sample brand and content)
python demo.py

# Try CLI commands
python cli.py --help
python cli.py list-brands
```

## First Run

```bash
# 1. Ingest a brand from a website
python cli.py ingest https://example.com mybrand

# 2. Generate content
python cli.py generate mybrand onepager \
  --x "building amazing product" \
  --y "to solve real problems" \
  --z "busy professionals" \
  --cta "Get started today"

# 3. Check output
ls data/drafts/
cat data/drafts/mybrand-onepager-*.md
```

## Start Flask Server (Optional)

```bash
export FLASK_APP=app.main:app
flask run -p 5050
```

**For Canva Integration**: Use a tunnel service (ngrok, localtunnel) and set `PUBLIC_BASE_URL=https://your-tunnel-url` in `.env` to make assets publicly fetchable.

## What You Get

- ✅ **Brand Ingestion**: Scrape websites for brand identity
- ✅ **Content Generation**: Create one-pagers, newsletters, blog posts
- ✅ **Local Storage**: All data stored in `/data` directory
- ✅ **CLI Interface**: Easy command-line usage
- ✅ **REST API**: HTTP endpoints for integration
- ✅ **LLM Integration**: OpenAI and Gemini support
- ✅ **Template System**: Jinja2 templates for consistent output

## File Structure

```
/app                 # Flask application
/templates           # Content templates
/data               # Generated content and assets
/cli.py             # Command-line interface
/demo.py             # Demo script
/test_setup.py      # Setup verification
```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Run `python cli.py --help` for CLI options
- Use `python test_setup.py` to diagnose issues 