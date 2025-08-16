from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from .brand import BrandIdentity, save_brand, load_brand, ensure_asset_dirs, get_asset_dir
from .scrape import fetch_html, extract_meta, find_images, find_css_links, visible_text_samples, download_image
from .palette import download_and_extract_palette, get_default_palette
from .fonts import get_fonts_from_css_urls, get_default_fonts
from .llm import get_llm_provider
from .generate import ContentGenerator
from .design import DesignAdvisorService
from .imgfm import generate_hero_image
import json
from urllib.parse import urlparse
import re

bp = Blueprint("api", __name__)

@bp.route('/ingest', methods=['POST'])
def ingest_brand():
    """Ingest brand from URL and create BrandIdentity with design advice"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        url = data.get('url')
        slug = data.get('slug')
        max_images = data.get('max_images', 3)
        timeout_ms = data.get('timeout_ms', 7000)
        
        if not url or not slug:
            return jsonify({"error": "URL and slug are required"}), 400
        
        # Fetch HTML
        html = fetch_html(url, timeout_ms)
        if not html:
            return jsonify({"error": "Failed to fetch HTML from URL"}), 400
        
        # Extract metadata
        meta = extract_meta(html, url)
        
        # Find images
        images = find_images(html, url, max_images)
        
        # Find CSS links
        css_links = find_css_links(html, url)
        
        # Extract text samples
        text_samples = visible_text_samples(html)
        
        # Ensure asset directories
        ensure_asset_dirs(slug)
        asset_dir = get_asset_dir(slug)
        
        # Download images and extract palette
        downloaded_images = []
        palette = []
        primary_color = None
        secondary_color = None
        logo_path = None
        
        for i, img in enumerate(images):
            if img['src']:
                # Determine if this is a logo
                is_logo = img.get('is_logo', False)
                
                # Download image
                filename = f"image_{i+1}.jpg"
                if is_logo:
                    filename = f"logo_{i+1}.jpg"
                
                save_path = os.path.join(asset_dir, "raw", filename)
                if download_image(img['src'], save_path):
                    downloaded_images.append(save_path)
                    
                    # Extract palette from logo or first image
                    if (is_logo or i == 0) and not palette:
                        img_palette, img_primary, img_secondary = download_and_extract_palette(img['src'], save_path)
                        if img_palette:
                            palette = img_palette
                            primary_color = img_primary
                            secondary_color = img_secondary
                            if is_logo:
                                logo_path = save_path
        
        # Use default palette if extraction failed
        if not palette:
            palette, primary_color, secondary_color = get_default_palette()
        
        # Extract fonts
        fonts_detected = get_fonts_from_css_urls(css_links)
        if not fonts_detected:
            fonts_detected = get_default_fonts()
        
        # Generate tone and keywords using LLM
        design_advisor = DesignAdvisorService()
        voice_result = design_advisor.analyze_voice(text_samples, url)
        tone = voice_result.get('tone', '')
        keywords = voice_result.get('keywords', [])
        
        # Create initial BrandIdentity
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
        
        # Get design advice
        design_advice = design_advisor.get_design_advice(brand)
        brand = design_advisor.apply_design_advice(brand, design_advice)
        
        # Save brand
        save_path = save_brand(brand, slug)
        
        return jsonify({
            "brandId": slug,
            "identity": brand.dict(),
            "design_advice": design_advice,
            "message": f"Brand ingested successfully with design advice. Saved to {save_path}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_assets():
    """Upload additional assets for a brand"""
    try:
        slug = request.form.get('slug')
        if not slug:
            return jsonify({"error": "Slug is required"}), 400
        
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            return jsonify({"error": f"Brand {slug} not found"}), 404
        
        # Ensure asset directories
        ensure_asset_dirs(slug)
        asset_dir = get_asset_dir(slug)
        upload_dir = os.path.join(asset_dir, "uploads")
        
        uploaded_files = []
        
        # Handle file uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    
                    # Add to brand images
                    if filename not in brand.images:
                        brand.images.append(file_path)
        
        # Update brand and save
        save_brand(brand, slug)
        
        return jsonify({
            "message": f"Uploaded {len(uploaded_files)} files",
            "files": uploaded_files,
            "brand": brand.dict()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/generate', methods=['POST'])
def generate_content():
    """Generate content using brand identity and template with multiple export formats"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        slug = data.get('slug')
        template = data.get('template')
        x = data.get('x', '')
        y = data.get('y', '')
        z = data.get('z', '')
        w = data.get('w', '')
        cta = data.get('cta', '')
        hero = data.get('hero', 'auto')
        qa = data.get('qa', False)
        
        if not all([slug, template, x, y, z]):
            return jsonify({"error": "slug, template, x, y, and z are required"}), 400
        
        # Check if brand exists
        brand = load_brand(slug)
        if not brand:
            return jsonify({"error": f"Brand {slug} not found"}), 404
        
        # Generate content
        generator = ContentGenerator()
        result = generator.generate_content(slug, template, x, y, z, w, cta, hero, qa)
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        # Return result (omit large content if too big)
        response = {
            "paths": result["paths"],
            "outline": result["outline"],
            "tokens": result["tokens"],
            "zip_path": result["zip_path"],
            "hero_path": result["hero_path"]
        }
        
        # Include HTML content if not too large
        if "html" in result["paths"] and result["paths"]["html"]:
            try:
                with open(result["paths"]["html"], 'r', encoding='utf-8') as f:
                    html_content = f.read()
                if len(html_content) < 50000:  # 50KB limit
                    response["html_preview"] = html_content[:2000] + "..." if len(html_content) > 2000 else html_content
            except Exception as e:
                print(f"Error reading HTML for preview: {e}")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/brands/<slug>', methods=['GET'])
def get_brand(slug):
    """Get brand identity by slug"""
    try:
        brand = load_brand(slug)
        if not brand:
            return jsonify({"error": f"Brand {slug} not found"}), 404
        
        return jsonify(brand.dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/brands', methods=['GET'])
def list_brands():
    """List all available brands"""
    try:
        brands_dir = "data/brands"
        if not os.path.exists(brands_dir):
            return jsonify({"brands": []})
        
        brands = []
        for filename in os.listdir(brands_dir):
            if filename.endswith('.json'):
                slug = filename[:-5]  # Remove .json extension
                brands.append(slug)
        
        return jsonify({"brands": brands})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/brands/<slug>/design', methods=['GET'])
def get_brand_design(slug):
    """Get design tokens and advice for a brand"""
    try:
        brand = load_brand(slug)
        if not brand:
            return jsonify({"error": f"Brand {slug} not found"}), 404
        
        from .html_tokens import generate_tokens, get_google_fonts_links
        
        tokens = generate_tokens(brand)
        google_fonts = get_google_fonts_links(tokens)
        
        return jsonify({
            "brand": brand.dict(),
            "tokens": tokens,
            "google_fonts": google_fonts
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 