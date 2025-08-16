#!/usr/bin/env python3
"""
CLI interface for Brand Content Generator
"""

import typer
import os
import sys
from pathlib import Path

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.brand import load_brand, ensure_asset_dirs, get_asset_dir
from app.scrape import fetch_html, extract_meta, find_images, find_css_links, visible_text_samples, download_image
from app.palette import download_and_extract_palette, get_default_palette
from app.fonts import get_fonts_from_css_urls, get_default_fonts
from app.llm import get_llm_provider
from app.design import DesignAdvisorService
from app.imgfm import generate_hero_image
from app.html_tokens import generate_tokens, get_google_fonts_links
from urllib.parse import urlparse

app = typer.Typer(help="Brand Content Generator CLI")

@app.command()
def ingest(url: str, slug: str):
    """Ingest brand from website URL"""
    typer.echo(f"Ingesting brand from {url}...")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        typer.echo("❌ OPENAI_API_KEY environment variable not set")
        return
    
    typer.echo(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Fetch and parse HTML
        from app.scrape import fetch_html, extract_meta, find_images, find_css_links, visible_text_samples
        from app.scrape import extract_social_media, extract_contact_info, extract_navigation, extract_content_structure
        from app.scrape import analyze_color_scheme, detect_typography, extract_business_info
        
        html = fetch_html(url)
        if not html:
            typer.echo("❌ Failed to fetch HTML")
            return
        
        # Extract comprehensive metadata
        typer.echo("📄 Extracting comprehensive metadata...")
        meta = extract_meta(html, url)
        typer.echo(f"📄 Title: {meta.get('title', 'N/A')}")
        typer.echo(f"📝 Description: {meta.get('description', 'N/A')[:100]}...")
        typer.echo(f"🖼️  OG Image: {meta.get('og_image', 'N/A')}")
        
        # Extract social media presence
        typer.echo("📱 Analyzing social media presence...")
        social_media = extract_social_media(html, url)
        if social_media:
            typer.echo(f"📱 Social platforms: {', '.join(social_media.keys())}")
        
        # Extract contact information
        typer.echo("📞 Extracting contact information...")
        contact_info = extract_contact_info(html, url)
        if contact_info:
            typer.echo(f"📞 Contact methods: {', '.join(contact_info.keys())}")
        
        # Extract navigation structure
        typer.echo("🧭 Analyzing navigation structure...")
        navigation = extract_navigation(html, url)
        if navigation:
            typer.echo(f"🧭 Main nav items: {', '.join(navigation[:5])}")
        
        # Extract content structure
        typer.echo("📚 Analyzing content structure...")
        content_structure = extract_content_structure(html)
        if content_structure:
            typer.echo(f"📚 Content types: {', '.join(content_structure.keys())}")
        
        # Extract business information
        typer.echo("🏢 Extracting business information...")
        business_info = extract_business_info(html, url)
        if business_info:
            typer.echo(f"🏢 Business details: {', '.join(business_info.keys())}")
        
        # Enhanced image analysis
        typer.echo("🖼️  Enhanced image analysis...")
        images = find_images(html, url, 10)  # Increased from 3 to 10
        typer.echo(f"🖼️  Found {len(images)} images")
        
        # Download and analyze images
        downloaded_images = []
        logo_path = None
        from app.brand import ensure_asset_dirs, get_asset_dir
        ensure_asset_dirs(slug)
        asset_dir = get_asset_dir(slug)
        
        for i, img in enumerate(images[:5]):  # Download top 5 images
            if img['src']:
                filename = f"image_{i+1}.jpg"
                save_path = os.path.join(asset_dir, "raw", filename)
                if download_image(img['src'], save_path):
                    downloaded_images.append(save_path)
                    if img.get('is_logo') and not logo_path:
                        logo_path = save_path
                    typer.echo(f"💾 Downloaded {filename}")
        
        # Enhanced color analysis
        typer.echo("🎨 Enhanced color analysis...")
        from app.scrape import analyze_color_scheme
        color_scheme = analyze_color_scheme(html, url)
        if color_scheme:
            typer.echo(f"🎨 Primary scheme: {color_scheme.get('primary', 'N/A')}")
            typer.echo(f"🎨 Secondary scheme: {color_scheme.get('secondary', 'N/A')}")
            typer.echo(f"🎨 Accent colors: {len(color_scheme.get('accents', []))}")
        
        # Enhanced typography detection
        typer.echo("🔤 Enhanced typography detection...")
        from app.scrape import detect_typography
        typography_info = detect_typography(html, url)
        if typography_info:
            typer.echo(f"🔤 Font families: {', '.join(typography_info.get('families', []))}")
            typer.echo(f"🔤 Font weights: {', '.join(map(str, typography_info.get('weights', [])))}")
        
        # CSS analysis
        css_links = find_css_links(html, url)
        typer.echo(f"🎨 Found {len(css_links)} CSS files")
        
        # Text analysis
        text_samples = visible_text_samples(html, max_chars=2000)  # Increased from 1500
        typer.echo(f"📝 Extracted {len(text_samples)} text samples")
        
        # Enhanced LLM analysis
        typer.echo("🤖 Enhanced LLM analysis...")
        from app.design import DesignAdvisorService
        design_advisor = DesignAdvisorService()
        
        # Voice analysis with more context
        typer.echo("🎯 Analyzing brand voice and personality...")
        voice_result = design_advisor.analyze_voice(text_samples, url)
        tone = voice_result.get('tone', '')
        keywords = voice_result.get('keywords', [])
        typer.echo(f"🎯 Tone: {tone}")
        typer.echo(f"🏷️  Keywords: {', '.join(keywords[:8])}...")
        
        # Create BrandIdentity object
        from app.brand import BrandIdentity, save_brand
        from urllib.parse import urlparse
        
        # Prepare colors from color scheme
        primary_color = color_scheme.get('primary') if color_scheme else None
        secondary_color = color_scheme.get('secondary') if color_scheme else None
        palette = color_scheme.get('accents', []) if color_scheme else []
        
        # Prepare fonts from typography detection
        fonts_detected = typography_info.get('families', []) if typography_info else []
        
        brand = BrandIdentity(
            slug=slug,
            name=meta.get('title', urlparse(url).netloc),
            website=url,
            tagline=meta.get('description', ''),
            description=meta.get('og_description', meta.get('description', '')),
            colors={
                "primary": primary_color,
                "secondary": secondary_color,
                "palette": palette
            },
            fonts_detected=fonts_detected,
            tone=tone,
            keywords=keywords,
            logo_path=logo_path,
            images=downloaded_images,
            source_notes=f"Scraped from {url}"
        )
        
        # Enhanced design advice
        typer.echo("🎨 Getting comprehensive design advice...")
        design_advice = design_advisor.get_design_advice(brand)
        
        typer.echo(f"🔤 Typography: {design_advice.get('typography', {}).get('heading', 'N/A')} + {design_advice.get('typography', {}).get('body', 'N/A')}")
        typer.echo(f"📐 Layout: Variant {design_advice.get('layout', 'A')}")
        typer.echo(f"🎨 Hero brief: {design_advice.get('heroBrief', 'N/A')[:50]}...")
        
        # Apply design advice
        brand = design_advisor.apply_design_advice(brand, design_advice)
        
        # Save enhanced brand identity
        typer.echo("💾 Saving enhanced brand identity...")
        from app.brand import save_brand
        save_path = save_brand(brand, slug)
        
        typer.echo(f"✅ Brand '{slug}' saved to {save_path}")
        typer.echo(f"📊 Total data points captured: {len(brand.dict())}")
        
        # Show summary
        typer.echo("\n📋 Brand Summary:")
        typer.echo(f"   Name: {brand.name}")
        typer.echo(f"   Website: {brand.website}")
        typer.echo(f"   Colors: {len(brand.colors.palette)} palette colors")
        typer.echo(f"   Fonts: {len(brand.fonts_detected)} detected")
        typer.echo(f"   Images: {len(brand.images)} downloaded")
        typer.echo(f"   Tone: {brand.tone}")
        typer.echo(f"   Keywords: {len(brand.keywords)} identified")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

@app.command()
def upload(
    slug: str = typer.Argument(..., help="Brand slug"),
    files: list[Path] = typer.Argument(..., help="Files to upload")
):
    """Upload additional assets for a brand"""
    typer.echo(f"Uploading {len(files)} files for brand {slug}...")
    
    try:
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Ensure asset directories
        ensure_asset_dirs(slug)
        asset_dir = get_asset_dir(slug)
        upload_dir = os.path.join(asset_dir, "uploads")
        
        uploaded_files = []
        
        for file_path in files:
            if file_path.exists():
                # Copy file to uploads directory
                dest_path = os.path.join(upload_dir, file_path.name)
                import shutil
                shutil.copy2(file_path, dest_path)
                uploaded_files.append(dest_path)
                typer.echo(f"💾 Uploaded: {file_path.name}")
                
                # Add to brand images if it's an image
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    if dest_path not in brand.images:
                        brand.images.append(dest_path)
            else:
                typer.echo(f"⚠️  File not found: {file_path}")
        
        # Update brand and save
        from app.brand import save_brand
        save_path = save_brand(brand, slug)
        
        typer.echo(f"✅ Uploaded {len(uploaded_files)} files")
        typer.echo(f"📁 Brand updated: {save_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def generate(
    slug: str = typer.Argument(..., help="Brand slug"),
    template: str = typer.Argument(..., help="Template: onepager, newsletter, or blogpost"),
    x: str = typer.Option(..., "--x", "-x", help="What we're building"),
    y: str = typer.Option(..., "--y", "-y", help="Why it matters"),
    z: str = typer.Option(..., "--z", "-z", help="Target audience"),
    w: str = typer.Option("", "--w", "-w", help="Additional context or path:./file.txt"),
    cta: str = typer.Option("", "--cta", help="Call to action"),
    hero: str = typer.Option("skip", "--hero", help="Hero image: auto, skip, or path:./image.png")
):
    """Generate content using brand identity and template with multiple export formats"""
    typer.echo(f"Generating {template} content for brand {slug}...")
    
    try:
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Generate content using new system
        from app.generate import generate_assets
        result = generate_assets(slug, brand.model_dump(), template, x, y, z, w, cta, hero)
        
        # Show results
        typer.echo("✅ Content generated successfully!")
        typer.echo(f"📁 HTML: {result['paths']['html']}")
        if result['paths']['pdf']:
            typer.echo(f"📄 PDF: {result['paths']['pdf']}")
        if result['paths']['docx']:
            typer.echo(f"📝 DOCX: {result['paths']['docx']}")
        if result['paths']['zip']:
            typer.echo(f"📦 ZIP Package: {result['paths']['zip']}")
        
        # Show public URLs if available
        if any(result['public'].values()):
            typer.echo(f"\n🌐 Public URLs (for Canva import):")
            if result['public']['html']:
                typer.echo(f"   HTML: {result['public']['html']}")
            if result['public']['pdf']:
                typer.echo(f"   PDF: {result['public']['pdf']}")
            if result['public']['hero']:
                typer.echo(f"   Hero: {result['public']['hero']}")
        
        # Show design tokens
        tokens = result.get('tokens', {})
        if tokens:
            typer.echo(f"\n🎨 Design Tokens:")
            typer.echo(f"   Typography: {tokens.get('font_heading', 'N/A')} + {tokens.get('font_body', 'N/A')}")
            typer.echo(f"   Colors: Primary {tokens.get('colors', {}).get('primary', 'N/A')}")
            typer.echo(f"   Max width: {tokens.get('max_width', 'N/A')}px")
        
        # Show outline
        outline = result.get('outline', {})
        if outline:
            typer.echo(f"\n📋 Generated Outline:")
            typer.echo(f"   Headline: {outline.get('headline', 'N/A')}")
            if outline.get('subhead'):
                typer.echo(f"   Subhead: {outline['subhead']}")
            typer.echo(f"   CTA: {outline.get('cta', 'N/A')}")
            typer.echo(f"   Sections: {len(outline.get('sections', []))}")
        
        # Show hero image info
        if result['public']['hero']:
            typer.echo(f"\n🖼️  Hero Image: {result['public']['hero']}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def render(
    slug: str = typer.Argument(..., help="Brand slug"),
    template: str = typer.Argument(..., help="Template: onepager, newsletter, or blogpost"),
    format: str = typer.Option("png", "--format", "-f", help="Output format: png or pdf"),
    output: str = typer.Option("", "--output", "-o", help="Output filename (optional)"),
    width: int = typer.Option(1200, "--width", "-w", help="Output width in pixels"),
    height: int = typer.Option(1600, "--height", "-h", help="Output height in pixels"),
    scale: int = typer.Option(2, "--scale", "-s", help="Device scale factor (1-3, default: 2 for retina)"),
    title: str = typer.Option("", "--title", "-t", help="Custom title for the content"),
    subtitle: str = typer.Option("", "--subtitle", help="Custom subtitle"),
    cta: str = typer.Option("", "--cta", help="Custom call to action"),
    hero: str = typer.Option("", "--hero", help="Hero image path (optional)")
):
    """Render brand-styled assets (PNG or PDF) from templates using Playwright"""
    typer.echo(f"Rendering {template} template for brand {slug} to {format.upper()}...")
    
    try:
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Validate format
        if format.lower() not in ['png', 'pdf']:
            typer.echo(f"❌ Invalid format: {format}. Use 'png' or 'pdf'", err=True)
            raise typer.Exit(1)
        
        # Validate scale
        if scale < 1 or scale > 3:
            typer.echo(f"❌ Invalid scale: {scale}. Must be between 1 and 3", err=True)
            raise typer.Exit(1)
        
        # Prepare custom data
        custom_data = {}
        if title:
            custom_data['title'] = title
        if subtitle:
            custom_data['subtitle'] = subtitle
        if cta:
            custom_data['cta'] = cta
        if hero:
            custom_data['hero_url'] = hero
        
        # Import renderer functions
        from app.renderer import render_template_with_brand, render_to_bytes, get_mimetype_and_filename
        
        # Render template to HTML
        typer.echo("📄 Rendering template to HTML...")
        html = render_template_with_brand(template, brand.model_dump(), custom_data)
        
        if not html:
            typer.echo("❌ Failed to render template", err=True)
            raise typer.Exit(1)
        
        # Create render payload
        from app.renderer import RenderPayload
        payload = RenderPayload(
            template=template,
            format=format.lower(),
            data=custom_data,
            width=width,
            height=height,
            scale=scale
        )
        
        # Render to bytes
        typer.echo(f"🎨 Rendering to {format.upper()}...")
        out_bytes = render_to_bytes(payload, html)
        
        # Generate output filename
        if not output:
            output = f"{slug}-{template}-{format}.{format.lower()}"
        
        # Save file
        with open(output, 'wb') as f:
            f.write(out_bytes)
        
        typer.echo(f"✅ Successfully rendered to {output}")
        typer.echo(f"📏 Dimensions: {width}x{height} pixels")
        if format.lower() == 'png':
            typer.echo(f"🔍 Scale: {scale}x (output: {width*scale}x{height*scale})")
        typer.echo(f"📁 File size: {len(out_bytes) / 1024:.1f} KB")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def list_brands():
    """List all available brands"""
    try:
        brands_dir = "data/brands"
        if not os.path.exists(brands_dir):
            typer.echo("No brands found")
            return
        
        brands = []
        for filename in os.listdir(brands_dir):
            if filename.endswith('.json'):
                slug = filename[:-5]  # Remove .json extension
                brands.append(slug)
        
        if brands:
            typer.echo("Available brands:")
            for brand in brands:
                typer.echo(f"  • {brand}")
        else:
            typer.echo("No brands found")
            
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def show_brand(slug: str = typer.Argument(..., help="Brand slug")):
    """Show details of a specific brand"""
    try:
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"Brand: {brand.name}")
        typer.echo(f"Website: {brand.website}")
        if brand.tagline:
            typer.echo(f"Tagline: {brand.tagline}")
        if brand.description:
            typer.echo(f"Description: {brand.description}")
        
        typer.echo(f"Colors: {len(brand.colors.palette)} in palette")
        if brand.colors.primary:
            typer.echo(f"  Primary: {brand.colors.primary}")
        if brand.colors.secondary:
            typer.echo(f"  Secondary: {brand.colors.secondary}")
        
        typer.echo(f"Fonts Detected: {', '.join(brand.fonts_detected)}")
        typer.echo(f"Typography: {brand.typography.heading or 'N/A'} + {brand.typography.body or 'N/A'}")
        typer.echo(f"Layout: Variant {brand.design_advisor.layout_variant}")
        typer.echo(f"Tone: {brand.tone}")
        typer.echo(f"Keywords: {', '.join(brand.keywords[:5])}...")
        
        if brand.logo_path:
            typer.echo(f"Logo: {brand.logo_path}")
        typer.echo(f"Images: {len(brand.images)} total")
        
        if brand.design_advisor.hero_brief:
            typer.echo(f"Hero Brief: {brand.design_advisor.hero_brief[:100]}...")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def design_tokens(slug: str = typer.Argument(..., help="Brand slug")):
    """Show design tokens for a brand"""
    try:
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        tokens = generate_tokens(brand)
        google_fonts = get_google_fonts_links(tokens)
        
        typer.echo(f"🎨 Design Tokens for {brand.name}")
        typer.echo(f"Typography:")
        typer.echo(f"  Heading: {tokens['font_heading']}")
        typer.echo(f"  Body: {tokens['font_body']}")
        typer.echo(f"  Fallbacks: {', '.join(tokens['font_fallbacks'][:3])}")
        
        typer.echo(f"\nLayout:")
        typer.echo(f"  Variant: {tokens['layout_variant']}")
        typer.echo(f"  Max Width: {tokens['max_width']}px")
        
        typer.echo(f"\nColors:")
        for key, value in tokens['colors'].items():
            if key != 'palette':
                typer.echo(f"  {key}: {value}")
        
        typer.echo(f"\nSpacing Scale:")
        for key, value in list(tokens['spacing'].items())[:5]:
            typer.echo(f"  {key}: {value}px")
        
        typer.echo(f"\nFont Scale:")
        for key, value in list(tokens['scale'].items())[:5]:
            typer.echo(f"  {key}: {value}px")
        
        if google_fonts:
            typer.echo(f"\nGoogle Fonts:")
            for font_link in google_fonts:
                typer.echo(f"  {font_link}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 