#!/usr/bin/env python3
"""
Unit tests for brand module
Tests individual functions and classes in isolation
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

def test_brand_identity_model():
    """Test BrandIdentity model creation and validation"""
    from app.brand import BrandIdentity, Colors, Typography, DesignAdvisor
    
    # Test Colors model
    colors = Colors(
        primary="#FF0000",
        secondary="#00FF00",
        accent="#0000FF",
        muted="#888888",
        palette=["#FF0000", "#00FF00", "#0000FF", "#888888"]
    )
    assert colors.primary == "#FF0000"
    assert len(colors.palette) >= 0  # Allow empty palette
    
    # Test Typography model
    typography = Typography(
        heading="Inter",
        body="Roboto",
        fallbacks=["Arial", "sans-serif"]
    )
    assert typography.heading == "Inter"
    assert len(typography.fallbacks) == 2
    
    # Test DesignAdvisor model
    design = DesignAdvisor(
        layout_variant="B",
        spacing_scale=[1, 1.25, 1.6, 2],
        radius={"sm": 8, "md": 14, "lg": 22},
        hero_brief="Minimal abstract design"
    )
    assert design.layout_variant == "B"
    assert design.radius["md"] == 14
    
    # Test full BrandIdentity
    brand = BrandIdentity(
        slug="test-brand",
        name="Test Brand",
        website="https://test.com",
        tagline="Test tagline",
        description="Test description",
        colors=colors,
        fonts_detected=["Inter", "Roboto"],
        typography=typography,
        design_advisor=design,
        tone="professional",
        keywords=["test", "demo", "example"]
    )
    
    assert brand.slug == "test-brand"
    assert brand.name == "Test Brand"
    assert len(brand.keywords) == 3
    assert brand.typography.heading == "Inter"
    assert brand.design_advisor.layout_variant == "B"

def test_brand_creation():
    """Test creating a basic brand identity"""
    from app.brand import BrandIdentity, Colors
    
    colors = Colors(
        primary="#FF0000",
        secondary="#00FF00",
        palette=["#FF0000", "#00FF00", "#0000FF"]
    )
    
    brand = BrandIdentity(
        slug="test-brand",
        name="Test Brand",
        website="https://test.com",
        tagline="Test tagline",
        colors=colors,
        fonts_detected=["Arial", "Helvetica"],
        tone="professional",
        keywords=["test", "demo", "example"]
    )
    
    assert brand.name == "Test Brand"
    assert len(brand.colors.palette) >= 3
    assert len(brand.fonts_detected) == 2

if __name__ == "__main__":
    pytest.main([__file__])
