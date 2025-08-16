# Brand Content Generator

A minimal Python + Flask backend for generating branded content from URLs and predefined templates.

## Features

- **Brand Ingestion**: Scrape websites to extract brand identity (colors, fonts, tone, keywords)
- **Content Generation**: Create one-pagers, newsletters, and blog posts using brand voice
- **Asset Rendering**: Render HTML templates to PNG/PDF with pixel-perfect fidelity using Playwright
- **Local Storage**: No database required - everything stored in `/data` directory
- **CLI & API**: Both command-line interface and REST API available
- **LLM Integration**: OpenAI (default) and Gemini support for content generation

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Chromium for Playwright (one time)
python -m playwright install chromium

# Copy environment file and add your API keys
cp env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Basic Usage

#### CLI Commands

```bash
# Ingest a brand from a website
python cli.py ingest https://example.com demo

# Upload additional assets
python cli.py upload demo ./logo.png ./brochure.pdf

# Generate content
python cli.py generate demo onepager \
  --x "launching X" \
  --y "to educate leads" \
  --z "SMB marketers" \
  --w "./notes.txt" \
  --cta "Join the beta" \
  --to-html

# List all brands
python cli.py list-brands

# Show brand details
python cli.py show-brand demo
```

#### REST API

```bash
# Start Flask server
export FLASK_APP=app.main:app
flask run -p 5050

# Or run directly
python -m app.main
```

**API Endpoints:**
- `POST /ingest` - Ingest brand from URL
- `POST /upload` - Upload additional assets
- `POST /generate` - Generate content
- `GET /brands` - List all brands
- `GET /brands/<slug>` - Get brand details
- `POST /render` - Render HTML templates to PNG/PDF
- `GET /templates` - List available templates
- `GET /healthz` - Health check

### 3. Asset Rendering

The new renderer allows you to convert HTML templates to high-quality PNG images or PDF documents using Playwright.

#### Render API Usage

```bash
# Render to PNG
curl -X POST http://127.0.0.1:5000/render \
  -H 'Content-Type: application/json' \
  -d '{
    "template": "onepager",
    "format": "png",
    "data": {
      "title": "Q3 Retail",
      "subtitle": "Brand Content",
      "tag": "Preview",
      "kpis": [{"label":"CTR lift","value":"18%"},
               {"label":"CPA delta","value":"-12%"},
               {"label":"Saves","value":"+3.1k"}],
      "bullets": ["Lift CTR by 18%", "Channels: IG, X, Email", "Hero variants: 6"],
      "footer": "© 2025 YourCo"
    },
    "width": 1200,
    "height": 1600,
    "scale": 2
  }' --output onepager.png

# Render to PDF
curl -X POST http://127.0.0.1:5000/render \
  -H 'Content-Type: application/json' \
  -d '{
    "template": "onepager",
    "format": "pdf",
    "data": {"title":"Q3 Retail","subtitle":"Brand Content"},
    "width": 1200,
    "height": 1600
  }' --output onepager.pdf
```

#### Render Parameters

- `template`: Template name (without .html extension)
- `format`: Output format (`png` or `pdf`)
- `data`: Template variables for Jinja2 rendering
- `width`: Output width in pixels
- `height`: Output height in pixels
- `scale`: Device scale factor for PNG (1-3, default: 2 for retina)

### 4. Example Workflow

```bash
# 1. Ingest a brand
python cli.py ingest https://acme.com acme

# 2. Generate a one-pager
python cli.py generate acme onepager \
  --x "revolutionary AI platform" \
  --y "transforms business operations" \
  --z "enterprise decision makers" \
  --cta "Schedule a demo"

# 3. Render to high-quality assets
curl -X POST http://127.0.0.1:5000/render \
  -H 'Content-Type: application/json' \
  -d '{
    "template": "onepager",
    "format": "png",
    "data": {"title": "Acme AI Platform"},
    "width": 1200,
    "height": 1600,
    "scale": 2
  }' --output acme-onepager.png

# 4. Check the output
ls data/drafts/
cat data/drafts/acme-onepager-*.md
```

## Project Structure

```
/app
  __init__.py          # Flask app factory
  main.py              # App entry point
  routes.py            # API endpoints
  brand.py             # BrandIdentity model
  renderer.py          # Playwright-based renderer
  generate.py          # Content generation
  templates_loader.py  # Template management
  # ... other modules

/templates
  onepager.html        # One-pager template
  # ... other templates

/static
  /fonts              # Brand fonts (add BrandSans.woff2)
  # ... other static assets
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest

# Run tests
pytest

# Run specific test file
pytest tests/unit/test_renderer.py -v
```

### Adding New Templates

1. Create new `.html` file in `/templates/`
2. Use Jinja2 syntax for dynamic content
3. Include CSS styling for consistent branding
4. Test with the render API

### Adding New LLM Providers

1. Implement `LLMProvider` interface in `app/llm.py`
2. Add provider logic to `get_llm_provider()`
3. Update environment variable handling

## Production Deployment

### Docker

```bash
# Build and run with Docker
docker build -t brand-generator .
docker run -p 8080:8080 brand-generator
```

### Local Production

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 2 -k gthread --threads 4 -b 0.0.0.0:8080 app.main:app
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `OPENAI_API_KEY` is set in `.env`
2. **Import Errors**: Make sure virtual environment is activated
3. **Permission Errors**: Check write permissions for `/data` directory
4. **Network Timeouts**: Increase `timeout_ms` for slow websites
5. **Playwright Issues**: Ensure Chromium is installed with `python -m playwright install chromium`

### Debug Mode

```bash
# Enable Flask debug mode
export FLASK_DEBUG=1
flask run -p 5050
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request 