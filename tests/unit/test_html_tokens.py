#!/usr/bin/env python3
"""
Unit tests for html_tokens module
Tests individual functions and classes in isolation
"""

import sys
import os
import pytest

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# Mock Flask dependencies before importing app modules
import sys
from unittest.mock import MagicMock

# Mock Flask and related modules
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

def test_default_tokens():
    """Test default_tokens function"""
    from app.html_tokens import default_tokens
    
    # Test with basic colors
    tokens = default_tokens({"primary": "#FF0000", "secondary": "#00FF00"})
    
    assert tokens["font_heading"] == "Inter"
    assert tokens["font_body"] == "Inter"
    assert tokens["colors"]["primary"] == "#FF0000"
    assert tokens["colors"]["secondary"] == "#00FF00"
    assert tokens["colors"]["accent"] == "#00FF00"  # Should default to secondary
    assert tokens["max_width"] == 880
    
    # Test with custom fonts
    tokens = default_tokens({"primary": "#0000FF"}, "Roboto", "Open Sans")
    assert tokens["font_heading"] == "Roboto"
    assert tokens["font_body"] == "Open Sans"

def test_tokens_structure():
    """Test that tokens have the correct structure"""
    from app.html_tokens import default_tokens
    
    tokens = default_tokens({})
    
    required_keys = ["font_heading", "font_body", "spacing", "radius", "colors", "max_width"]
    for key in required_keys:
        assert key in tokens
    
    # Test spacing structure
    assert "4" in tokens["spacing"]
    assert "6" in tokens["spacing"]
    assert "8" in tokens["spacing"]
    
    # Test radius structure
    assert "md" in tokens["radius"]
    
    # Test colors structure
    color_keys = ["primary", "secondary", "accent", "muted", "text", "bg"]
    for key in color_keys:
        assert key in tokens["colors"]

if __name__ == "__main__":
    pytest.main([__file__])
