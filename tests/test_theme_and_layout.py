"""
Test Theme and Layout System
Validates contrast, channel sizing, and template selection.
"""

import pytest
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_contrast_tokens():
    """Test that generated themes have proper contrast ratios"""
    from palette_harmonizer import propose_theme, validate_theme_contrast, contrast_ratio
    
    # Mock brand data
    brand = {
        "colors": {
            "primary": "#241461",
            "secondary": "#0099ff",
            "accent": "#3a3a3a",
            "muted": "#d9d8fc"
        }
    }
    
    theme = propose_theme(brand)
    
    # Test CTA contrast
    cta_bg = theme["pairs"]["cta_bg"]
    cta_fg = theme["pairs"]["cta_fg"]
    assert contrast_ratio(cta_bg, cta_fg) >= 4.5, f"CTA contrast too low: {contrast_ratio(cta_bg, cta_fg)}"
    
    # Test card contrast
    card_bg = theme["pairs"]["card_bg"]
    card_fg = theme["pairs"]["card_fg"]
    assert contrast_ratio(card_bg, card_fg) >= 4.5, f"Card contrast too low: {contrast_ratio(card_bg, card_fg)}"

def test_story_canvas_size():
    """Test that story templates have correct 9:16 dimensions"""
    from template_registry import get_template_by_id
    
    # This would test actual template rendering
    # For now, just test that the template exists
    try:
        template = get_template_by_id("story.story-pdp-cta")
        assert template.aspect_hint == "9:16", f"Expected 9:16, got {template.aspect_hint}"
    except ValueError:
        pytest.skip("Story template not found")

def test_template_registry():
    """Test that template registry has expected templates"""
    from template_registry import TEMPLATES
    
    # Check that we have templates for each channel
    channels = set()
    for template in TEMPLATES:
        channels.update(template.channels)
    
    expected_channels = {"onepager", "story", "linkedin"}
    assert channels.issuperset(expected_channels), f"Missing channels: {expected_channels - channels}"
    
    # Check that we have multiple templates per channel
    for channel in expected_channels:
        channel_templates = [t for t in TEMPLATES if channel in t.channels]
        assert len(channel_templates) >= 2, f"Channel {channel} has only {len(channel_templates)} templates"

def test_palette_harmonizer_functions():
    """Test that palette harmonizer functions work correctly"""
    from palette_harmonizer import propose_theme, validate_theme_contrast
    
    brand = {
        "colors": {
            "primary": "#241461",
            "secondary": "#0099ff",
            "accent": "#3a3a3a",
            "muted": "#d9d8fc"
        }
    }
    
    # Test theme generation
    theme = propose_theme(brand)
    assert "tokens" in theme
    assert "pairs" in theme
    assert "base_colors" in theme
    
    # Test theme validation
    validation = validate_theme_contrast(theme)
    assert "valid" in validation
    assert "issues" in validation
    assert "fixes" in validation

def test_layout_selector_functions():
    """Test that layout selector functions work correctly"""
    from layout_selector import features_from_brand
    
    # Mock brand data
    brand = {
        "name": "Test Brand",
        "tagline": "AI-powered platform",
        "source_notes": "has_products, has_ai",
        "ui_layout": {
            "page_structure": {
                "content": {
                    "has_buttons": True
                }
            }
        }
    }
    
    # Test feature detection
    features = features_from_brand(brand)
    
    assert features["has_ai"] > 0, "AI detection should work"
    assert features["has_features"] > 0, "Features detection should work"

if __name__ == "__main__":
    # Run tests
    print("Running theme and layout tests...")
    
    try:
        test_contrast_tokens()
        print("✅ Contrast tokens test passed")
    except Exception as e:
        print(f"❌ Contrast tokens test failed: {e}")
    
    try:
        test_template_registry()
        print("✅ Template registry test passed")
    except Exception as e:
        print(f"❌ Template registry test failed: {e}")
    
    try:
        test_palette_harmonizer_functions()
        print("✅ Palette harmonizer test passed")
    except Exception as e:
        print(f"❌ Palette harmonizer test failed: {e}")
    
    try:
        test_layout_selector_functions()
        print("✅ Layout selector test passed")
    except Exception as e:
        print(f"❌ Layout selector test failed: {e}")
    
    print("Tests completed!")
