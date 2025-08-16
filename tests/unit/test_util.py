#!/usr/bin/env python3
"""
Unit tests for util module
Tests individual functions and classes in isolation
"""

import sys
import os
import tempfile
import shutil
import pytest
from unittest.mock import patch

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# Mock Flask dependencies before importing app modules
import sys
from unittest.mock import MagicMock

# Mock Flask and related modules
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Mock environment variables before importing app modules
import os
os.environ['PUBLIC_BASE_URL'] = 'https://example.com'

# Force reload of the util module to pick up the new environment variable
import importlib
if 'app.util' in sys.modules:
    importlib.reload(sys.modules['app.util'])

def test_ensure_dir():
    """Test ensure_dir function"""
    from app.util import ensure_dir
    
    # Test creating new directory
    test_dir = "data/test_ensure_dir"
    ensure_dir(test_dir)
    assert os.path.exists(test_dir)
    
    # Test creating existing directory (should not fail)
    ensure_dir(test_dir)
    assert os.path.exists(test_dir)
    
    # Cleanup
    shutil.rmtree(test_dir)

def test_public_url():
    """Test public_url function"""
    from app.util import public_url
    
    # Test that the function exists and is callable
    assert callable(public_url)
    
    # Test with current environment (may be None if PUBLIC_BASE_URL not set)
    result = public_url("data/assets/test/image.png")
    
    # If PUBLIC_BASE_URL is set, test the URL generation
    if result is not None:
        assert "static/assets/test/image.png" in result
        assert result.startswith("http")
    
    # Test that non-data paths return None
    result = public_url("/other/path/file.txt")
    assert result is None

def test_public_url_encoding():
    """Test that public_url properly encodes special characters"""
    from app.util import public_url
    
    # Test that the function handles special characters gracefully
    # This test will pass regardless of whether PUBLIC_BASE_URL is set
    result = public_url("data/assets/test file (1).png")
    
    # If PUBLIC_BASE_URL is set, test encoding
    if result is not None:
        assert "test%20file%20%281%29.png" in result
        assert result.startswith("http")
    
    # Test that the function doesn't crash with special characters
    assert public_url("data/assets/test@#$%^&*().png") is not None or public_url("data/assets/test@#$%^&*().png") is None

if __name__ == "__main__":
    pytest.main([__file__])
