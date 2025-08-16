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
    """Ingest brand from website URL with comprehensive UI/layout analysis"""
    typer.echo(f"Ingesting brand from {url}...")

    try:
        # Fetch HTML
        html = fetch_html(url, 7000)
        if not html:
            typer.echo("❌ Failed to fetch HTML from URL")
            return
        
        # Extract metadata
        typer.echo("📋 Extracting metadata...")
        meta = extract_meta(html, url)
        if meta.get('title'):
            typer.echo(f"📋 Title: {meta['title']}")
        
        # Extract social media presence
        typer.echo("📱 Analyzing social media presence...")
        from app.scrape import extract_social_media
        social_media = extract_social_media(html, url)
        if social_media:
            typer.echo(f"📱 Social platforms: {', '.join(social_media.keys())}")
        
        # Extract contact information
        typer.echo("📞 Extracting contact information...")
        from app.scrape import extract_contact_info
        contact_info = extract_contact_info(html, url)
        if contact_info:
            typer.echo(f"📞 Contact methods: {', '.join(contact_info.keys())}")
        
        # Extract navigation structure
        typer.echo("🧭 Analyzing navigation structure...")
        from app.scrape import extract_navigation
        navigation = extract_navigation(html, url)
        if navigation:
            typer.echo(f"🧭 Main nav items: {', '.join(navigation[:5])}")
        
        # Extract content structure
        typer.echo("📚 Analyzing content structure...")
        from app.scrape import extract_content_structure
        content_structure = extract_content_structure(html)
        if content_structure:
            typer.echo(f"📚 Content types: {', '.join(content_structure.keys())}")
        
        # Extract business information
        typer.echo("🏢 Extracting business information...")
        from app.scrape import extract_business_info
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
        
        # Extract colors and fonts
        palette = []
        color_roles = {}
        css_links = find_css_links(html, url)
        
        # Enhanced color extraction from HTML FIRST (most accurate)
        typer.echo("🎨 Extracting colors from HTML...")
        from app.scrape import analyze_color_scheme
        color_scheme = analyze_color_scheme(html, url)
        if color_scheme and color_scheme.get('accents'):
            palette = color_scheme['accents']
            color_roles = {
                'primary': color_scheme.get('primary'),
                'secondary': color_scheme.get('secondary'),
                'accent': color_scheme.get('accents')[2] if len(color_scheme['accents']) > 2 else None,
                'muted': color_scheme.get('accents')[3] if len(color_scheme['accents']) > 3 else None
            }
            typer.echo(f"🎨 Extracted {len(palette)} colors from HTML")
        
        # Download images and extract additional colors if HTML extraction failed
        for i, img in enumerate(images[:5]):  # Download top 5 images
            if img['src']:
                filename = f"image_{i+1}.jpg"
                save_path = os.path.join(asset_dir, "raw", filename)
                
                if download_image(img['src'], save_path):
                    downloaded_images.append(save_path)
                    typer.echo(f"🖼️  Downloaded: {filename}")
                    
                    # Extract palette from logo or first image ONLY if HTML extraction failed
                    if not palette and (img.get('is_logo', False) or i == 0):
                        typer.echo("🎨 Extracting color palette from image...")
                        img_palette, img_primary, img_secondary = download_and_extract_palette(img['src'], save_path)
                        if img_palette:
                            palette = img_palette
                            color_roles = {
                                'primary': img_primary,
                                'secondary': img_secondary,
                                'accent': img_palette[2] if len(img_palette) > 2 else None,
                                'muted': img_palette[3] if len(img_palette) > 3 else None
                            }
                            typer.echo(f"🎨 Extracted {len(palette)} colors from image")
                            if img.get('is_logo', False):
                                logo_path = save_path
                                typer.echo("🎨 Logo identified for color extraction")
        
        # Use default palette if extraction failed
        if not palette:
            typer.echo("🎨 Using default color palette...")
            palette, color_roles = get_default_palette()
        
        # Ensure we have proper color roles
        if not color_roles.get('primary') and palette:
            color_roles['primary'] = palette[0]
        if not color_roles.get('secondary') and len(palette) > 1:
            color_roles['secondary'] = palette[1]
        if not color_roles.get('accent') and len(palette) > 2:
            color_roles['accent'] = palette[2]
        if not color_roles.get('muted') and len(palette) > 3:
            color_roles['muted'] = palette[3]
        
        # Extract fonts
        typer.echo("🔤 Extracting fonts...")
        from app.scrape import detect_typography
        typography_info = detect_typography(html, url)
        if typography_info and typography_info.get('families'):
            fonts_detected = typography_info['families']
            typer.echo(f"🔤 Detected fonts: {', '.join(fonts_detected[:5])}")
        else:
            # Fallback to CSS-based extraction
            fonts_detected = get_fonts_from_css_urls(css_links)
            if fonts_detected:
                typer.echo(f"🔤 Detected fonts from CSS: {', '.join(fonts_detected[:5])}")
            else:
                typer.echo("🔤 Using default fonts...")
                fonts_detected = get_default_fonts()
        
        # Extract text samples for tone analysis
        text_samples = visible_text_samples(html)
        
        # UI/Layout Analysis for design patterns
        typer.echo("🎨 Analyzing UI structure and layout patterns...")
        from app.scrape import extract_ui_structure, capture_page_screenshot, extract_css_structure
        ui_layout_data = extract_ui_structure(html, url)
        
        # Normalize ui_layout data to prevent Pydantic validation errors
        from app.adapters import coerce_ui_layout
        ui_layout_data = coerce_ui_layout(ui_layout_data)
        
        # Extract CSS structure
        css_structure = extract_css_structure(html, url)
        ui_layout_data['css_structure'] = css_structure
        
        # Capture page screenshot
        screenshot_path = os.path.join(asset_dir, "screenshot.png")
        if capture_page_screenshot(url, screenshot_path):
            ui_layout_data['screenshot_path'] = screenshot_path
            typer.echo(f"📸 Screenshot saved to {screenshot_path}")
        
        # Additional fallback: Extract colors directly from screenshot if available
        if (not color_roles.get('primary') or not palette) and ui_layout_data.get('screenshot_path'):
            try:
                from app.scrape import extract_dominant_colors_from_image
                screenshot_pal = extract_dominant_colors_from_image(ui_layout_data['screenshot_path'])
                if screenshot_pal and screenshot_pal.get('palette'):
                    if not color_roles.get('primary'):
                        color_roles['primary'] = screenshot_pal.get('primary')
                    if not color_roles.get('secondary'):
                        color_roles['secondary'] = screenshot_pal.get('secondary')
                    if not palette:
                        palette = screenshot_pal.get('palette', palette)
                    typer.echo(f"🎨 Extracted palette from screenshot: {len(screenshot_pal.get('palette', []))} colors")
            except Exception as e:
                typer.echo(f"⚠️  Screenshot palette extraction failed: {e}")
        
        # Generate tone and keywords using LLM
        typer.echo("🧠 Analyzing brand voice...")
        design_advisor = DesignAdvisorService()
        voice_result = design_advisor.analyze_voice(text_samples, url)
        tone = voice_result.get('tone', '')
        keywords = voice_result.get('keywords', [])
        
        if tone:
            typer.echo(f"🧠 Brand tone: {tone}")
        if keywords:
            typer.echo(f"🧠 Key themes: {', '.join(keywords[:8])}")
        
        # Create brand identity
        typer.echo("🏷️  Creating brand identity...")
        from app.brand import BrandIdentity
        
        brand = BrandIdentity(
            slug=slug,
            name=meta.get('title', urlparse(url).netloc),
            website=url,
            tagline=meta.get('description', ''),
            description=meta.get('og_description', meta.get('description', '')),
            colors={
                "primary": color_roles.get('primary'),
                "secondary": color_roles.get('secondary'),
                "accent": color_roles.get('accent'),
                "muted": color_roles.get('muted'),
                "palette": palette
            },
            fonts_detected=fonts_detected,
            tone=tone,
            keywords=keywords,
            logo_path=logo_path,
            images=downloaded_images,
            source_notes=f"Scraped from {url}",
            ui_layout=ui_layout_data  # Include comprehensive UI/layout data
        )
        
        # Get design advice
        typer.echo("🎨 Getting design advice...")
        design_advice = design_advisor.get_design_advice(brand)
        brand = design_advisor.apply_design_advice(brand, design_advice)
        
        # Save brand
        from app.brand import save_brand
        save_path = save_brand(brand, slug)
        
        typer.echo(f"✅ Brand ingested successfully!")
        typer.echo(f"   📁 Saved to: {save_path}")
        typer.echo(f"   🎨 Colors: {len(palette)} in palette")
        typer.echo(f"   🔤 Fonts: {len(fonts_detected)} detected")
        typer.echo(f"   🏷️  Name: {brand.name}")
        typer.echo(f"   🎯 Tone: {brand.tone}")
        
        # Show color breakdown
        if color_roles:
            typer.echo("   🎨 Color roles:")
            typer.echo(f"      Primary: {color_roles.get('primary', 'Not set')}")
            typer.echo(f"      Secondary: {color_roles.get('secondary', 'Not set')}")
            typer.echo(f"      Accent: {color_roles.get('accent', 'Not set')}")
            typer.echo(f"      Muted: {color_roles.get('muted', 'Not set')}")
        
        # Show UI/Layout analysis summary
        if ui_layout_data:
            typer.echo("\n🎨 UI/Layout Analysis Summary:")
            if ui_layout_data.get('page_structure'):
                structure = ui_layout_data['page_structure']
                typer.echo(f"   📄 Page sections: {len(structure.get('sections', []))}")
                if structure.get('header'):
                    typer.echo(f"   🧭 Header: {structure['header'].get('tag', 'N/A')}")
                if structure.get('hero'):
                    typer.echo(f"   🎯 Hero: {structure['hero'].get('tag', 'N/A')}")
                if structure.get('footer'):
                    typer.echo(f"   👣 Footer: {structure['footer'].get('tag', 'N/A')}")
            
            if ui_layout_data.get('design_patterns'):
                patterns = ui_layout_data['design_patterns']
                typer.echo(f"   🎨 Design patterns: {len(patterns)} found")
                for pattern in patterns[:3]:
                    typer.echo(f"     • {pattern.get('type', 'N/A')} ({pattern.get('layout_type', 'N/A')})")
            
            if ui_layout_data.get('spacing_system'):
                spacing = ui_layout_data['spacing_system']
                if spacing.get('common_values'):
                    typer.echo(f"   📏 Common spacing: {', '.join(spacing['common_values'][:5])}")
        
        # Show comprehensive summary
        typer.echo("\n📋 Brand Summary:")
        typer.echo(f"   Name: {brand.name}")
        typer.echo(f"   Website: {brand.website}")
        typer.echo(f"   Colors: {len(brand.colors.palette)} palette colors")
        typer.echo(f"   Fonts: {len(brand.fonts_detected)} detected")
        typer.echo(f"   Images: {len(brand.images)} downloaded")
        typer.echo(f"   Tone: {brand.tone}")
        typer.echo(f"   Keywords: {len(brand.keywords)} identified")
        if ui_layout_data:
            typer.echo(f"   UI Patterns: {len(ui_layout_data.get('design_patterns', []))} detected")
            typer.echo(f"   Layout Sections: {len(ui_layout_data.get('page_structure', {}).get('sections', []))}")
        
        return brand
        
    except Exception as e:
        typer.echo(f"❌ Error ingesting brand: {e}")
        return None

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
    template: str = typer.Option("auto", "--template", "-t", help="Template: auto, onepager, newsletter, blogpost, or specific template ID"),
    x: str = typer.Option(..., "--x", "-x", help="What we're building"),
    y: str = typer.Option(..., "--y", "-y", help="Why it matters"),
    z: str = typer.Option(..., "--z", "-z", help="Target audience"),
    w: str = typer.Option("", "--w", help="Additional context or path:./file.txt"),
    cta: str = typer.Option("", "--cta", help="Call to action"),
    hero: str = typer.Option("skip", "--hero", help="Hero image: auto, skip, or path:./image.png"),
    layout: str = typer.Option("auto", "--layout", help="Layout selection: auto, manual, or specific template ID"),
    channels: str = typer.Option("onepager", "--channels", help="Channels to generate: onepager,story,linkedin (comma-separated)"),
    variants: int = typer.Option(1, "--variants", help="Number of variants to generate when using auto-layout"),
    brief: str = typer.Option("", "--brief", help="Brief file path for automatic channel/deliverable detection")
):
    """Generate content using brand identity and template with multiple export formats"""
    typer.echo(f"Generating content for brand {slug}...")
    
    try:
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Parse channels
        channel_list = [ch.strip() for ch in channels.split(",")]
        
        # Handle auto-layout vs manual template selection
        if layout == "auto" or template == "auto":
            typer.echo("🎯 Using adaptive template selection...")
            
            # Import the new adaptive system
            from app.layout_selector import analyze_brand_content_fit, get_template_recommendations
            from app.palette_harmonizer import propose_theme, propose_theme_variants
            from app.judges import judge_color_schemes
            
            # Generate color theme variants
            theme_variants = propose_theme_variants(brand.model_dump(), variants)
            typer.echo(f"🎨 Generated {len(theme_variants)} color theme variants")
            
            # Judge color schemes
            rankings = judge_color_schemes(theme_variants, brand.model_dump())
            best_theme = theme_variants[rankings[0]]
            typer.echo(f"🎨 Selected theme: {best_theme.get('variant_name', 'base')}")
            
            # Generate content for each channel
            all_results = {}
            
            for channel in channel_list:
                typer.echo(f"\n📱 Generating for {channel} channel...")
                
                # Get template recommendations
                recommendations = get_template_recommendations(brand, channel, include_reasoning=True, top_k=variants)
                
                if not recommendations:
                    typer.echo(f"⚠️  No templates found for {channel} channel")
                    continue
                
                typer.echo(f"🎯 Top {channel} templates:")
                for i, rec in enumerate(recommendations[:variants]):
                    typer.echo(f"  {i+1}. {rec['id']} (Score: {rec['score']:.2f})")
                    if rec.get('reasoning'):
                        for reason in rec['reasoning'][:2]:
                            typer.echo(f"     • {reason}")
                
                # Generate content for top template
                top_template = recommendations[0]
                typer.echo(f"🎨 Using template: {top_template['id']}")
                
                # Generate content using existing system
                from app.generate import generate_assets
                result = generate_assets(slug, brand.model_dump(), channel, x, y, z, w, cta, hero)
                
                # Store results
                all_results[channel] = {
                    'template': top_template,
                    'theme': best_theme,
                    'result': result
                }
                
                typer.echo(f"✅ Generated {channel} content successfully!")
                typer.echo(f"   📁 HTML: {result['paths']['html']}")
                if result['paths']['pdf']:
                    typer.echo(f"   📄 PDF: {result['paths']['pdf']}")
            
            # Show summary
            typer.echo(f"\n🎉 Multi-channel generation complete!")
            typer.echo(f"📊 Generated for {len(all_results)} channels:")
            for channel, data in all_results.items():
                template_id = data['template']['id']
                score = data['template']['score']
                typer.echo(f"   • {channel}: {template_id} (Score: {score:.2f})")
            
            return all_results
            
        else:
            # Use existing manual template system
            typer.echo(f"🎯 Using manual template: {template}")
            
            # Generate content using existing system
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
            
            return result
        
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
        
        # Prepare custom data with basic content
        custom_data = {}
        
        # Basic content
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
        
        # Show what was rendered
        if custom_data:
            typer.echo(f"\n🎯 Custom content rendered:")
            if custom_data.get('title'):
                typer.echo(f"   Title: {custom_data['title']}")
            if custom_data.get('subtitle'):
                typer.echo(f"   Subtitle: {custom_data['subtitle']}")
        
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

@app.command()
def recommend_templates(
    slug: str = typer.Argument(..., help="Brand slug"),
    channel: str = typer.Option("onepager", "--channel", help="Channel: onepager, story, or linkedin"),
    include_reasoning: bool = typer.Option(True, "--reasoning", help="Include reasoning for recommendations")
):
    """Show template recommendations for a brand and channel"""
    try:
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Import the new adaptive system
        from app.layout_selector import get_template_recommendations, analyze_brand_content_fit
        
        typer.echo(f"🎯 Template Recommendations for {brand.name} ({channel} channel)")
        typer.echo(f"🎨 Brand: {brand.name}")
        typer.echo(f"🏷️  Tagline: {brand.tagline or 'N/A'}")
        typer.echo(f"🎨 Colors: {brand.colors.primary}, {brand.colors.secondary}")
        typer.echo(f"🔤 Fonts: {', '.join(brand.fonts_detected[:3])}")
        
        # Get recommendations
        recommendations = get_template_recommendations(brand, channel, include_reasoning=include_reasoning, top_k=5)
        
        if not recommendations:
            typer.echo(f"⚠️  No templates found for {channel} channel")
            return
        
        typer.echo(f"\n📊 Top {len(recommendations)} Template Recommendations:")
        typer.echo("=" * 60)
        
        for i, rec in enumerate(recommendations):
            typer.echo(f"\n{i+1}. {rec['id']}")
            typer.echo(f"   🎯 Score: {rec['score']:.2f}")
            typer.echo(f"   🎨 Hero Style: {rec['hero_style']}")
            typer.echo(f"   📏 Density: {rec['density']}")
            typer.echo(f"   📐 Aspect: {rec['aspect_hint']}")
            
            if include_reasoning and rec.get('reasoning'):
                typer.echo(f"   💡 Why this template:")
                for reason in rec['reasoning'][:3]:
                    typer.echo(f"      • {reason}")
        
        # Show brand analysis
        analysis = analyze_brand_content_fit(brand, channel)
        typer.echo(f"\n🔍 Brand Feature Analysis:")
        typer.echo("=" * 60)
        
        features = analysis['detected_features']
        for feature, score in features.items():
            if score > 0.3:  # Only show relevant features
                emoji = "✅" if score > 0.7 else "🟡" if score > 0.5 else "🟠"
                typer.echo(f"   {emoji} {feature}: {score:.1f}")
        
        typer.echo(f"\n💡 Tips:")
        typer.echo(f"   • Use '--layout auto' to automatically select the best template")
        typer.echo(f"   • Use '--channels {channel},linkedin' to generate across multiple channels")
        typer.echo(f"   • Use '--variants 3' to generate multiple template options")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def show_theme(
    slug: str = typer.Argument(..., help="Brand slug"),
    variants: int = typer.Option(1, "--variants", help="Number of theme variants to generate")
):
    """Show the brand's color theme and design tokens"""
    try:
        brand = load_brand(slug)
        if not brand:
            typer.echo(f"❌ Brand {slug} not found", err=True)
            raise typer.Exit(1)
        
        # Import the new palette harmonizer
        from app.palette_harmonizer import propose_theme, propose_theme_variants, validate_theme_contrast, get_color_usage_guide
        
        typer.echo(f"🎨 Color Theme for {brand.name}")
        typer.echo(f"🎨 Brand Colors: {brand.colors.primary}, {brand.colors.secondary}")
        typer.echo("=" * 60)
        
        # Generate theme variants
        theme_variants = propose_theme_variants(brand.model_dump(), variants)
        
        for i, theme in enumerate(theme_variants):
            variant_name = theme.get('variant_name', 'base')
            typer.echo(f"\n{i+1}. Theme Variant: {variant_name}")
            typer.echo("-" * 40)
            
            # Show base colors
            base_colors = theme['base_colors']
            typer.echo(f"   🎨 Base Colors:")
            typer.echo(f"      Primary: {base_colors['primary']}")
            typer.echo(f"      Secondary: {base_colors['secondary']}")
            typer.echo(f"      Accent: {base_colors['accent']}")
            typer.echo(f"      Muted: {base_colors['muted']}")
            
            # Show key tokens
            tokens = theme['tokens']
            typer.echo(f"\n   🎯 Key Tokens:")
            typer.echo(f"      Background: {tokens['bg']}")
            typer.echo(f"      Surface: {tokens['surface']}")
            typer.echo(f"      Text: {tokens['text']}")
            typer.echo(f"      Brand-500: {tokens['brand-500']}")
            typer.echo(f"      Accent-500: {tokens['accent-500']}")
            
            # Show color pairs
            pairs = theme['pairs']
            typer.echo(f"\n   🔗 Color Pairs:")
            typer.echo(f"      CTA Button: {pairs['cta_bg']} on {pairs['cta_fg']}")
            typer.echo(f"      Cards: {pairs['card_bg']} with {pairs['card_fg']} text")
            typer.echo(f"      Links: {pairs['link']} (hover: {pairs['link_hover']})")
            
            # Validate contrast
            validation = validate_theme_contrast(theme)
            status = "✅ Valid" if validation['valid'] else "❌ Issues"
            typer.echo(f"\n   ✅ Contrast: {status}")
            if not validation['valid']:
                for issue in validation['issues']:
                    typer.echo(f"      ⚠️  {issue}")
        
        # Show usage guide
        usage_guide = get_color_usage_guide(theme_variants[0])
        typer.echo(f"\n📖 Color Usage Guide:")
        typer.echo("=" * 60)
        
        typer.echo(f"\n🎨 Backgrounds:")
        for name, color in usage_guide['backgrounds'].items():
            typer.echo(f"   {name}: {color}")
        
        typer.echo(f"\n🔤 Text:")
        for name, color in usage_guide['text'].items():
            typer.echo(f"   {name}: {color}")
        
        typer.echo(f"\n🔘 Interactive:")
        buttons = usage_guide['interactive']['buttons']
        typer.echo(f"   Primary Button: {buttons['primary']['bg']} on {buttons['primary']['fg']}")
        typer.echo(f"   Secondary Button: {buttons['secondary']['bg']} on {buttons['secondary']['fg']}")
        
        typer.echo(f"\n💡 Tips:")
        typer.echo(f"   • Use '--variants 3' to see different color variations")
        typer.echo(f"   • All colors are WCAG AA compliant")
        typer.echo(f"   • Colors automatically adapt to your brand")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 