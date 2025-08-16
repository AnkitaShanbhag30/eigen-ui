#!/usr/bin/env python3
"""
Integration tests for template system
Tests template loading, rendering, and integration with design tokens
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# Mock Flask dependencies before importing app modules
import sys
from unittest.mock import MagicMock

# Mock Flask and related modules
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

def test_template_rendering():
    """Test that templates render correctly with design tokens"""
    from app.templates_loader import get_env
    from app.html_tokens import default_tokens
    
    # Create test data
    brand = {
        "name": "Test Brand",
        "website": "https://test.com",
        "tagline": "Test tagline",
        "typography": {"heading": "Inter", "body": "Inter"},
        "colors": {"primary": "#FF0000", "secondary": "#00FF00"}
    }
    
    # Build tokens the same way generate_assets does
    from app.html_tokens import default_tokens
    heading = brand.get("typography",{}).get("heading","Inter")
    body = brand.get("typography",{}).get("body","Inter")
    tokens = default_tokens(brand.get("colors",{}), heading, body)
    
    # Debug: print the tokens structure
    print(f"Tokens structure: {tokens}")
    print(f"Colors in tokens: {tokens.get('colors', {})}")
    print(f"Secondary color: {tokens.get('colors', {}).get('secondary', 'NOT FOUND')}")
    outline = {
        "headline": "Test Headline",
        "subhead": "Test Subhead",
        "sections": [{"title": "Section 1", "bullets": ["Point 1", "Point 2"]}],
        "cta": "Test CTA"
    }
    
    # Test HTML rendering
    from app.generate import render_html
    html = render_html("onepager", brand, tokens, outline, None)
    
    # Debug: print the generated HTML to see what's actually there
    print(f"Generated HTML length: {len(html)}")
    print(f"HTML contains 'var(--color-primary)': {'var(--color-primary)' in html}")
    print(f"HTML contains 'var(--color-secondary)': {'var(--color-secondary)' in html}")
    print(f"HTML contains 'Test Headline': {'Test Headline' in html}")
    print(f"HTML contains 'Test Brand': {'Test Brand' in html}")
    
    # Extract and print the CSS variables section
    if '<style>' in html and '</style>' in html:
        style_start = html.find('<style>') + 7
        style_end = html.find('</style>')
        css_content = html[style_start:style_end]
        print(f"CSS content: {css_content[:500]}...")
        print(f"CSS contains secondary: {'--color-secondary' in css_content}")
    
    # Verify content is rendered
    assert "Test Headline" in html
    assert "Test Brand" in html
    assert "var(--color-primary)" in html
    assert "Test CTA" in html
    
    # Verify CSS variables are defined (even if not used)
    assert "--color-secondary:" in css_content
    assert "#00FF00" in css_content  # The secondary color value

def test_template_with_hero():
    """Test template rendering with hero image"""
    from app.generate import render_html
    from app.html_tokens import default_tokens
    
    tokens = default_tokens({"primary": "#FF0000"})
    brand = {
        "name": "Test Brand",
        "typography": {"heading": "Inter", "body": "Inter"}
    }
    outline = {
        "headline": "Test Headline",
        "subhead": "Test Subhead",
        "sections": [{"title": "Section 1", "bullets": ["Point 1"]}],
        "cta": "Test CTA"
    }
    
    # Test with hero image
    html = render_html("onepager", brand, tokens, outline, "https://example.com/hero.jpg")
    
    assert "hero" in html
    assert "https://example.com/hero.jpg" in html
    assert "hero-overlay" in html

def test_template_structure():
    """Test that all templates have the correct structure"""
    from app.templates_loader import get_env
    
    env = get_env()
    templates = ["onepager", "newsletter", "blogpost"]
    
    for template_name in templates:
        template = env.get_template(f"{template_name}.html.j2")
        assert template is not None
        
        # Test basic rendering
        html = template.render(
            brand={"name": "Test", "typography": {"heading": "Inter", "body": "Inter"}},
            tokens={
                "font_heading": "Inter", 
                "font_body": "Inter",
                "colors": {"primary": "#FF0000", "secondary": "#00FF00", "accent": "#00FF00", "muted": "#EBEEF3", "text": "#0B0B0B", "bg": "#FFFFFF"},
                "spacing": {"4": 16, "6": 24, "8": 32},
                "radius": {"md": 16},
                "max_width": 880
            },
            outline={"headline": "Test", "sections": [], "cta": "Test"},
            hero_url=None,
            title="Test",
            font_links=""
        )
        
        assert "Test" in html
        assert "<!doctype html>" in html

if __name__ == "__main__":
    pytest.main([__file__])
