#!/usr/bin/env python3
"""
Comprehensive end-to-end tests
Tests complete workflows from content generation to export
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# Mock Flask dependencies before importing app modules
import sys
from unittest.mock import MagicMock

# Mock only the problematic modules
sys.modules['flask_cors'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Don't mock Flask itself for the API endpoint test

def test_content_generation_workflow():
    """Test the complete content generation workflow"""
    from app.generate import generate_assets
    from app.brand import load_brand
    
    # Mock the LLM calls to avoid external dependencies
    with patch('app.generate.generate_json') as mock_generate:
        mock_generate.return_value = {
            "headline": "Test AI Platform",
            "subhead": "Revolutionary technology for modern businesses",
            "sections": [
                {
                    "title": "Key Features",
                    "bullets": ["AI-powered insights", "Real-time analytics", "Easy integration"]
                }
            ],
            "cta": "Get Started"
        }
        
        # Test with mock brand data
        mock_brand = {
            "name": "Test Brand",
            "website": "https://test.com",
            "typography": {"heading": "Inter", "body": "Inter"},
            "colors": {"primary": "#FF0000", "secondary": "#00FF00"},
            "tone": "professional",
            "keywords": ["AI", "technology"]
        }
        
        result = generate_assets(
            "test-brand", mock_brand, "onepager",
            "AI platform", "solve problems", "developers",
            "Additional context", "Get Started", "skip"
        )
        
        # Verify the result structure
        assert "outline" in result
        assert "paths" in result
        assert "public" in result
        assert "tokens" in result
        
        # Verify content was generated
        assert result["outline"]["headline"] == "Test AI Platform"
        assert result["outline"]["cta"] == "Get Started"
        assert len(result["outline"]["sections"]) == 1

def test_export_formats():
    """Test that all export formats are generated correctly"""
    from app.generate import generate_assets, write_pdf, write_docx, zip_outputs
    
    # Mock brand data
    mock_brand = {
        "name": "Test Brand",
        "typography": {"heading": "Inter", "body": "Inter"},
        "colors": {"primary": "#FF0000"}
    }
    
    # Mock outline
    mock_outline = {
        "headline": "Test Headline",
        "subhead": "Test Subhead",
        "sections": [{"title": "Section 1", "bullets": ["Point 1"]}],
        "cta": "Test CTA"
    }
    
    # Test PDF generation (will fail gracefully if WeasyPrint not available)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        html = "<html><body><h1>Test</h1></body></html>"
        pdf_success = write_pdf(html, tmp_pdf.name)
        if pdf_success:
            assert os.path.exists(tmp_pdf.name)
        os.unlink(tmp_pdf.name)
    
    # Test DOCX generation
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
        write_docx(mock_outline, mock_brand, tmp_docx.name)
        assert os.path.exists(tmp_docx.name)
        os.unlink(tmp_docx.name)
    
    # Test ZIP creation
    test_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(suffix=f'.txt', delete=False) as tmp_file:
            tmp_file.write(f"Test content {i}".encode())
            test_files.append(tmp_file.name)
    
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
        zip_outputs(test_files, tmp_zip.name)
        assert os.path.exists(tmp_zip.name)
        os.unlink(tmp_zip.name)
    
    # Clean up test files
    for f in test_files:
        os.unlink(f)

def test_api_endpoint():
    """Test the API endpoint returns correct structure"""
    from app.routes import generate
    from flask import Flask
    from unittest.mock import Mock
    
    # Create a test Flask app
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    with app.test_request_context('/generate', json={
        "slug": "test-brand",
        "template": "onepager",
        "x": "AI platform",
        "y": "solve problems",
        "z": "developers",
        "w": "Additional context",
        "cta": "Get Started",
        "hero": "skip"
    }):
        # Mock the generate_assets function
        with patch('app.generate.generate_assets') as mock_generate:
            mock_generate.return_value = {
                "outline": {
                    "headline": "Test Headline",
                    "subhead": "Test Subhead",
                    "sections": [{"title": "Section 1", "bullets": ["Point 1"]}],
                    "cta": "Test CTA"
                },
                "paths": {
                    "html": "/path/to/html",
                    "pdf": "/path/to/pdf",
                    "docx": "/path/to/docx",
                    "zip": "/path/to/zip"
                },
                "public": {
                    "html": "https://example.com/static/html",
                    "pdf": "https://example.com/static/pdf",
                    "docx": "https://example.com/static/docx",
                    "zip": "https://example.com/static/zip",
                    "hero": None
                },
                "tokens": {
                    "colors": {"primary": "#FF0000", "secondary": "#00FF00", "accent": "#00FF00"}
                }
            }
            
            # Mock load_brand
            with patch('app.routes.load_brand') as mock_load_brand:
                mock_load_brand.return_value = {
                    "name": "Test Brand",
                    "website": "https://test.com"
                }
                
                response = generate()
                data = response.get_json()
                
                # Verify response structure
                assert "design" in data
                assert "paths" in data
                assert "public" in data
                
                # Verify design content
                assert data["design"]["headline"] == "Test Headline"
                assert data["design"]["cta"] == "Test CTA"
                assert len(data["design"]["sections"]) == 1
                
                # Verify brand info
                assert data["design"]["brand"]["name"] == "Test Brand"
                assert data["design"]["brand"]["primary"] == "#FF0000"

if __name__ == "__main__":
    pytest.main([__file__])
