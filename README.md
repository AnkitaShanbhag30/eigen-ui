# Brand Content Generator

A powerful Flask application that generates brand-styled content and renders it to high-quality PNG/PDF assets using Playwright. The system automatically extracts brand identity from websites and creates pixel-perfect, customizable templates.

## ✨ Key Features

- **🎨 Brand Identity Extraction**: Automatically scrape and analyze websites for colors, fonts, and design patterns
- **📱 Responsive Templates**: Modern, mobile-friendly templates that adapt to brand data
- **🖼️ High-Quality Rendering**: Pixel-perfect PNG and PDF output using Playwright (Chromium)
- **🔧 Modular Design**: Highly configurable templates with dynamic content sections
- **📊 Rich Data Support**: KPIs, metrics, custom sections, and dynamic content
- **🚀 CLI & API**: Both command-line interface and REST API for automation

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <your-repo>
cd eigen-ui

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
python -m playwright install chromium
```

### 2. Ingest Your First Brand

```bash
# Extract brand identity from a website
python cli.py ingest https://example.com my-brand

# View brand details
python cli.py show-brand my-brand

# See design tokens
python cli.py design-tokens my-brand
```

### 3. Generate Content

```bash
# Generate content with AI
python cli.py generate my-brand onepager \
  --x "building amazing products" \
  --y "to solve real problems" \
  --z "busy professionals" \
  --cta "Get Started Today"
```

### 4. Render High-Quality Assets

```bash
# Render to PNG with custom content
python cli.py render my-brand onepager \
  --format png \
  --title "Our Amazing Product" \
  --subtitle "Solving real problems for busy professionals" \
  --cta "Get Started Today" \
  --kpis "Users:10K,Revenue:$50K,Growth:+25%" \
  --bullets "Easy to use;Fast setup;24/7 support" \
  --width 1200 \
  --height 1600 \
  --scale 2

# Render to PDF
python cli.py render my-brand onepager \
  --format pdf \
  --title "Product Overview" \
  --subtitle "Everything you need to know" \
  --output "product-overview.pdf"
```

## 🎨 Enhanced Template System

### Dynamic Brand Integration

Templates automatically adapt to your brand data:

- **Colors**: Primary, secondary, accent, muted, text, and background colors
- **Typography**: Heading and body fonts with fallbacks
- **Spacing**: Dynamic spacing scale based on brand preferences
- **Layout**: Responsive grid systems and component layouts

### Modular Content Sections

Templates support various content types:

```bash
# Custom sections with JSON
python cli.py render my-brand onepager \
  --sections '[
    {
      "title": "Features",
      "type": "bullets",
      "bullets": ["Feature 1", "Feature 2", "Feature 3"]
    },
    {
      "title": "Metrics",
      "type": "grid",
      "columns": 3,
      "items": [
        {"title": "Users", "value": "10K", "icon": "👥"},
        {"title": "Revenue", "value": "$50K", "icon": "💰"},
        {"title": "Growth", "value": "+25%", "icon": "📈"}
      ]
    },
    {
      "title": "Testimonial",
      "type": "quote",
      "quote": "This product changed everything for us!",
      "author": "Jane Doe, CEO"
    }
  ]'
```

### KPI and Metrics Display

```bash
# Key Performance Indicators
python cli.py render my-brand onepager \
  --kpis "Monthly Users:15K,Revenue:$75K,Churn Rate:2%,NPS Score:85"
```

### Bullet Points

```bash
# Custom bullet points
python cli.py render my-brand onepager \
  --bullets "Easy to use;Fast setup;24/7 support;Mobile friendly;API access"
```

## 🔧 API Usage

### Render Endpoint

```bash
# POST /render
curl -X POST http://localhost:5000/render \
  -H 'Content-Type: application/json' \
  -d '{
    "template": "onepager",
    "format": "png",
    "data": {
      "title": "Product Launch",
      "subtitle": "Revolutionary new features",
      "cta": "Learn More",
      "kpis": [
        {"label": "Users", "value": "10K"},
        {"label": "Revenue", "value": "$50K"}
      ],
      "bullets": ["Feature 1", "Feature 2", "Feature 3"]
    },
    "width": 1200,
    "height": 1600,
    "scale": 2
  }'
```

### Available Endpoints

- `POST /render` - Render templates to PNG/PDF
- `GET /templates` - List available templates
- `GET /healthz` - Health check
- `GET /brands/{slug}` - Get brand data

## 📁 Template Structure

### Base Template (`base.html.j2`)

- Dynamic brand color integration
- Responsive typography scale
- Utility classes for spacing and layout
- Mobile-first responsive design

### Onepager Template (`onepager.html.j2`)

- Hero section with image/text options
- Brand overview with keywords
- Dynamic content sections
- KPI/metrics display
- Custom bullet points
- Call-to-action sections
- Contact information

### Customization Options

Templates support:

- **Content Types**: Text, bullets, grids, quotes, KPIs
- **Layout Variants**: 1-4 column grids, centered, left-aligned
- **Visual Elements**: Icons, images, color schemes
- **Responsive Behavior**: Mobile, tablet, desktop layouts

## 🎯 Advanced Usage

### Custom Section Types

```json
{
  "type": "grid",
  "columns": 2,
  "items": [
    {
      "icon": "🚀",
      "title": "Fast",
      "value": "10x faster",
      "description": "Lightning quick performance"
    }
  ]
}
```

### Brand Data Integration

Templates automatically use:

- Brand colors and typography
- Logo and imagery
- Tone and keywords
- Website and contact info
- Design preferences

### Responsive Design

- Mobile-first approach
- Dynamic spacing based on brand preferences
- Adaptive typography scales
- Flexible grid systems

## 🐳 Docker Deployment

```dockerfile
# Build and run
docker build -t brand-generator .
docker run -p 5000:5000 brand-generator
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/unit/test_renderer.py -v

# Test rendering
python test_renderer.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Template not found**: Ensure template exists in `templates/` directory
2. **Brand not found**: Check brand slug and data directory
3. **Rendering fails**: Verify Playwright installation and browser binaries
4. **Custom data not showing**: Check JSON format and template variables

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
python -m app.main
```

## 📚 Template Development

### Creating New Templates

1. Extend `base.html.j2`
2. Use brand variables: `{{ brand.name }}`, `{{ brand.colors.primary }}`
3. Access custom data: `{{ custom_data.title }}`, `{{ custom_data.kpis }}`
4. Use utility classes: `text-brand-primary`, `bg-brand-accent`

### Template Variables

- `brand`: Complete brand identity data
- `tokens`: Generated design tokens
- `custom_data`: User-provided content
- `outline`: Generated content structure
- `title`, `subtitle`, `cta`: Basic content fields

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details. 