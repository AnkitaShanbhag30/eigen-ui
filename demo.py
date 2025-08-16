#!/usr/bin/env python3
"""
Demo script for Brand Content Generator
Shows how to use the system programmatically
"""

import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def demo_brand_creation():
    """Demo creating a brand identity manually"""
    print("🎨 Demo: Creating Brand Identity\n")
    
    try:
        from app.brand import BrandIdentity, Colors, save_brand
        
        # Create a sample brand
        colors = Colors(
            primary="#2563EB",
            secondary="#F59E0B",
            palette=["#2563EB", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]
        )
        
        brand = BrandIdentity(
            name="TechCorp",
            website="https://techcorp.example.com",
            tagline="Innovation at the speed of thought",
            description="Leading technology solutions for modern businesses",
            colors=colors,
            fonts=["Inter", "Roboto", "Open Sans"],
            tone="innovative and trustworthy",
            keywords=["AI", "cloud", "automation", "scalability", "enterprise"]
        )
        
        # Save the brand
        save_path = save_brand(brand, "demo-techcorp")
        print(f"✅ Created brand: {brand.name}")
        print(f"   Website: {brand.website}")
        print(f"   Colors: {len(brand.colors.palette)} in palette")
        print(f"   Fonts: {len(brand.fonts)} fonts")
        print(f"   Tone: {brand.tone}")
        print(f"   Saved to: {save_path}")
        
        return "demo-techcorp"
        
    except Exception as e:
        print(f"❌ Error creating brand: {e}")
        return None

def demo_content_generation(brand_slug):
    """Demo generating content"""
    print(f"\n📝 Demo: Generating Content for {brand_slug}\n")
    
    try:
        from app.generate import ContentGenerator
        
        generator = ContentGenerator()
        
        # Generate a one-pager
        result = generator.generate_content(
            brand_slug=brand_slug,
            template="onepager",
            x="AI-powered analytics platform",
            y="to democratize data insights",
            z="data analysts and business users",
            w="Our platform transforms complex data into actionable insights through intuitive visualizations and automated reporting.",
            cta="Start your free trial",
            to_html=True
        )
        
        if "error" in result:
            print(f"❌ Content generation failed: {result['error']}")
            return False
        
        print("✅ Content generated successfully!")
        print(f"   Template: onepager")
        print(f"   Markdown: {result['paths']['md']}")
        if result['paths']['html']:
            print(f"   HTML: {result['paths']['html']}")
        
        # Show outline
        outline = result.get('outline', {})
        if outline:
            print(f"\n📋 Generated Outline:")
            print(f"   Headline: {outline.get('headline', 'N/A')}")
            if outline.get('subhead'):
                print(f"   Subhead: {outline['subhead']}")
            print(f"   CTA: {outline.get('cta', 'N/A')}")
            print(f"   Sections: {len(outline.get('sections', []))}")
            
            for i, section in enumerate(outline.get('sections', [])[:2]):  # Show first 2 sections
                print(f"     {i+1}. {section.get('title', 'N/A')}")
                bullets = section.get('bullets', [])
                if bullets:
                    print(f"        - {bullets[0]}")
                    if len(bullets) > 1:
                        print(f"        - {bullets[1]}")
                        if len(bullets) > 2:
                            print(f"        - ... and {len(bullets)-2} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return False

def demo_template_rendering():
    """Demo template rendering without LLM"""
    print(f"\n🎭 Demo: Template Rendering\n")
    
    try:
        from app.templates_loader import TemplatesLoader
        
        loader = TemplatesLoader()
        
        # Test context
        context = {
            "brand": {
                "name": "Demo Brand",
                "website": "https://demo.example.com"
            },
            "outline": {
                "headline": "Revolutionary Product Launch",
                "subhead": "Transforming the industry landscape",
                "sections": [
                    {
                        "title": "The Problem",
                        "bullets": [
                            "Current solutions are outdated and inefficient",
                            "Users struggle with complex workflows",
                            "Integration challenges across platforms"
                        ]
                    },
                    {
                        "title": "Our Solution",
                        "bullets": [
                            "Modern, intuitive interface design",
                            "Seamless integration with existing tools",
                            "AI-powered automation and insights"
                        ]
                    }
                ],
                "cta": "Join the revolution today"
            }
        }
        
        # Render all templates
        templates = ["onepager", "newsletter", "blogpost"]
        
        for template in templates:
            result = loader.render_template(template, context)
            if result:
                print(f"✅ {template.title()} template rendered:")
                print(f"   Length: {len(result)} characters")
                print(f"   Preview: {result[:100]}...")
            else:
                print(f"❌ {template.title()} template failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rendering templates: {e}")
        return False

def main():
    """Run the demo"""
    print("🚀 Brand Content Generator Demo\n")
    print("This demo will:")
    print("1. Create a sample brand identity")
    print("2. Generate content using templates")
    print("3. Show template rendering capabilities")
    print("\nNote: LLM features require OPENAI_API_KEY in .env file\n")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. LLM features may not work.")
        print("   Copy env.example to .env and add your OPENAI_API_KEY")
    
    try:
        # Demo 1: Brand creation
        brand_slug = demo_brand_creation()
        if not brand_slug:
            print("❌ Brand creation failed, skipping content generation")
            return
        
        # Demo 2: Template rendering
        demo_template_rendering()
        
        # Demo 3: Content generation (if LLM is available)
        try:
            demo_content_generation(brand_slug)
        except Exception as e:
            print(f"\n⚠️  Content generation demo skipped (likely missing API key): {e}")
            print("   To enable: set OPENAI_API_KEY in .env file")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\n📁 Generated files:")
        print(f"   Brand: data/brands/{brand_slug}.json")
        print(f"   Drafts: data/drafts/")
        
        print(f"\n🔧 Try these commands:")
        print(f"   python cli.py show-brand {brand_slug}")
        print(f"   python cli.py list-brands")
        print(f"   python -m app.main  # Start Flask server")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 