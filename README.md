# Brand Content Generator

A minimal Python + Flask backend for generating branded content from URLs and predefined templates.

## Features

- **Brand Ingestion**: Scrape websites to extract brand identity (colors, fonts, tone, keywords)
- **Content Generation**: Create one-pagers, newsletters, and blog posts using brand voice
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

#### REST API (Optional)

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

### 3. Example Workflow

```bash
# 1. Ingest a brand
python cli.py ingest https://acme.com acme

# 2. Generate a one-pager
python cli.py generate acme onepager \
  --x "revolutionary AI platform" \
  --y "transforms business operations" \
  --z "enterprise decision makers" \
  --cta "Schedule a demo"

# 3. Check the output
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
  scrape.py            # Web scraping utilities
  palette.py           # Color extraction
  fonts.py             # Font parsing
  llm.py               # LLM provider interface
  generate.py          # Content generation
  templates_loader.py  # Jinja2 template management
/templates
  onepager.md.j2      # One-pager template
  newsletter.md.j2    # Newsletter template
  blogpost.md.j2      # Blog post template
/data
  brands/              # Brand JSON files
  assets/              # Downloaded assets
  drafts/              # Generated content
/cli.py                # Typer CLI interface
```

## Templates

Three content templates are available:

1. **One-pager** (400-700 words): Concise overview with sections
2. **Newsletter** (450-900 words): Email format with subject/preheader
3. **Blog post** (800-1200 words): Longer-form content

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_key_here          # Required for OpenAI
LLM_PROVIDER=openai                   # or: gemini
GOOGLE_API_KEY=                       # Required for Gemini
```

### LLM Providers

- **OpenAI** (default): Uses GPT-3.5-turbo for content generation
- **Gemini**: Alternative provider using Google's Gemini Pro

## Data Storage

All data is stored locally in the `/data` directory:

- **Brands**: `/data/brands/<slug>.json` - Brand identity data
- **Assets**: `/data/assets/<slug>/raw/` - Downloaded images
- **Uploads**: `/data/assets/<slug>/uploads/` - User-uploaded files
- **Drafts**: `/data/drafts/` - Generated markdown and HTML

## API Examples

### Ingest Brand

```bash
curl -X POST http://localhost:5050/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "slug": "demo",
    "max_images": 3,
    "timeout_ms": 7000
  }'
```

### Generate Content

```bash
curl -X POST http://localhost:5050/generate \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "demo",
    "template": "onepager",
    "x": "building X",
    "y": "reason Y",
    "z": "audience Z",
    "w": "Additional context notes",
    "cta": "Get started",
    "to_html": true
  }'
```

## Error Handling

The system includes fallbacks for common failures:

- **Palette extraction fails**: Uses default color palette
- **Font detection fails**: Falls back to "Inter" font
- **LLM analysis fails**: Uses default tone and keywords
- **Image download fails**: Continues with available assets

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest

# Run tests (when implemented)
pytest
```

### Adding New Templates

1. Create new `.md.j2` file in `/templates/`
2. Add template to `TemplatesLoader.templates` in `app/templates_loader.py`
3. Update word count bands in `ContentGenerator._get_word_count_band()`

### Adding New LLM Providers

1. Implement `LLMProvider` interface in `app/llm.py`
2. Add provider logic to `get_llm_provider()`
3. Update environment variable handling

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `OPENAI_API_KEY` is set in `.env`
2. **Import Errors**: Make sure virtual environment is activated
3. **Permission Errors**: Check write permissions for `/data` directory
4. **Network Timeouts**: Increase `timeout_ms` for slow websites

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