#!/usr/bin/env python3
"""
Test script to verify the setup works correctly
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic modules
        from app.brand import BrandIdentity, Colors
        print("✅ BrandIdentity imported successfully")
        
        from app.scrape import fetch_html, extract_meta
        print("✅ Scraping modules imported successfully")
        
        from app.palette import extract_palette, get_default_palette
        print("✅ Palette modules imported successfully")
        
        from app.fonts import get_fonts_from_css_urls, get_default_fonts
        print("✅ Font modules imported successfully")
        
        from app.templates_loader import TemplatesLoader
        print("✅ Templates loader imported successfully")
        
        # Test optional modules with fallbacks
        try:
            from app.generate import generate_assets
            print("✅ Content generation modules imported successfully")
        except ImportError as e:
            if "weasyprint" in str(e):
                print("⚠️  Content generation imported (WeasyPrint optional)")
            else:
                raise e
        
        print("\n🎉 All imports successful! Basic setup is working.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_brand_creation():
    """Test creating a basic brand identity"""
    try:
        from app.brand import BrandIdentity, Colors
        
        colors = Colors(
            primary="#FF0000",
            secondary="#00FF00",
            palette=["#FF0000", "#00FF00", "#0000FF"]
        )
        
        brand = BrandIdentity(
            slug="test-brand",  # Add the required slug field
            name="Test Brand",
            website="https://test.com",
            tagline="Test tagline",
            colors=colors,
            fonts_detected=["Arial", "Helvetica"],
            tone="professional",
            keywords=["test", "demo", "example"]
        )
        
        print("✅ Brand creation test successful")
        print(f"   Brand: {brand.name}")
        print(f"   Colors: {len(brand.colors.palette)} in palette")
        print(f"   Fonts: {len(brand.fonts_detected)} fonts")
        
        return True
        
    except Exception as e:
        print(f"❌ Brand creation test failed: {e}")
        return False

def test_templates():
    """Test template loading"""
    try:
        from app.templates_loader import TemplatesLoader
        
        loader = TemplatesLoader()
        templates = loader.list_templates()
        
        print(f"✅ Templates loaded: {templates}")
        
        # Test rendering a simple template with new system
        from app.html_tokens import default_tokens
        
        tokens = default_tokens({"primary": "#FF0000", "secondary": "#00FF00"})
        context = {
            "brand": {
                "name": "Test Brand", 
                "website": "https://test.com",
                "typography": {"heading": "Inter", "body": "Inter"}
            },
            "tokens": tokens,
            "outline": {
                "headline": "Test Headline",
                "subhead": "Test Subhead",
                "sections": [{"title": "Section 1", "bullets": ["Point 1", "Point 2"]}],
                "cta": "Test CTA"
            }
        }
        
        result = loader.render_template("onepager", context)
        if result:
            print("✅ Template rendering test successful")
            print(f"   Generated {len(result)} characters")
        else:
            print("❌ Template rendering failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Brand Content Generator Setup\n")
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Brand Creation Test", test_brand_creation),
        ("Template Test", test_templates)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and add your OPENAI_API_KEY")
        print("2. Try: python cli.py --help")
        print("3. Or start the server: python -m app.main")
    else:
        print("❌ Some tests failed. Check the errors above.")
        if passed >= 2:  # If most tests passed
            print("\n💡 Most functionality is working! You can proceed with:")
            print("   python cli.py --help")
        sys.exit(1) 