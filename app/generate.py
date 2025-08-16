import os, json, time, zipfile
from typing import Dict
from .llm import generate_json
from .templates_loader import get_env
from .html_tokens import default_tokens
from .imgfm import gen_hero_image
from .util import ensure_dir, public_url
from docx import Document
from docx.shared import Pt
from markdown_it import MarkdownIt

def _font_links(heading, body):
    # Basic Google Fonts includes; safe even if font not present
    def link_for(name):
      q = name.replace(" ", "+")
      return f'<link href="https://fonts.googleapis.com/css2?family={q}:wght@400;600;700&display=swap" rel="stylesheet"/>'
    if heading == body:
        return link_for(heading)
    return link_for(heading) + link_for(body)

def outline_for(template: str, brand: Dict, x: str, y: str, z: str, w: str, cta: str) -> Dict:
    """Generate content outline using enhanced brand-aware system"""
    try:
        from .design import DesignAdvisorService
        
        # Create design advisor service
        design_advisor = DesignAdvisorService()
        
        # Convert brand dict to BrandIdentity object if needed
        if isinstance(brand, dict):
            from .brand import BrandIdentity
            brand_obj = BrandIdentity(**brand)
        else:
            brand_obj = brand
        
        # Generate enhanced content outline using brand insights
        outline = design_advisor.generate_content_outline(template, x, y, z, w, cta, brand_obj)
        
        if outline and isinstance(outline, dict):
            return outline
        else:
            print(f"Warning: Enhanced content generation returned invalid result: {outline}")
            return _get_fallback_outline(template, x, y, z, cta)
            
    except Exception as e:
        print(f"Warning: Enhanced content generation failed: {e}")
        return _get_fallback_outline(template, x, y, z, cta)

def _get_fallback_outline(template: str, x: str, y: str, z: str, cta: str) -> Dict:
    """Fallback outline when LLM fails"""
    return {
        "headline": f"{x} - {y}",
        "subhead": f"Transform your {z} experience with our innovative solution",
        "sections": [
            {
                "title": "Why Choose Us",
                "bullets": [
                    f"Built specifically for {z}",
                    f"Delivers on {y}",
                    "Proven results and customer satisfaction"
                ]
            },
            {
                "title": "Key Benefits",
                "bullets": [
                    "Streamlined workflow",
                    "Increased efficiency",
                    "Better outcomes"
                ]
            }
        ],
        "cta": cta or "Get Started Today"
    }

def polish_outline(o: Dict, brand: Dict) -> Dict:
    """Polish the outline with better content"""
    if not o or not isinstance(o, dict):
        print(f"Warning: Invalid outline received: {o}")
        return o
    
    # For now, return the original outline to avoid LLM issues
    # In the future, this could be enhanced with LLM polishing
    return o

def render_html(template_key: str, brand: Dict, tokens: Dict, outline: Dict, hero_url: str|None):
    """Render HTML using the new template system with proper custom_data structure"""
    try:
        from .renderer import render_template_with_brand
        
        # Prepare custom data from outline and other parameters
        custom_data = {
            'title': outline.get("headline", ""),
            'subtitle': outline.get("subhead", ""),
            'cta': outline.get("cta", ""),
            'hero_url': hero_url,
            'outline': outline,
            'font_links': _font_links(brand["typography"]["heading"], brand["typography"]["body"])
        }
        
        # Use the new renderer system
        html = render_template_with_brand(template_key, brand, custom_data)
        return html
        
    except Exception as e:
        # Fallback to old system if new renderer fails
        print(f"⚠️  New renderer failed, falling back to old system: {e}")
        env = get_env()
        
        # Handle new channel structure
        template_path = template_key
        if template_key == 'story':
            template_path = 'story/story-highlights.html.j2'
        elif template_key == 'linkedin':
            template_path = 'linkedin/li-product-announcement.html.j2'
        else:
            template_path = f"{template_key}.html.j2"
        
        try:
            tpl = env.get_template(template_path)
        except Exception as template_error:
            print(f"⚠️  Template not found: {template_path}, trying fallback...")
            # Try the base template as last resort
            tpl = env.get_template("onepager.html.j2")
        
        # Ensure outline has minimum content
        if not outline.get("headline"):
            outline["headline"] = f"Welcome to {brand.get('name', 'Our Platform')}"
        if not outline.get("subhead"):
            outline["subhead"] = f"Discover how we can help you achieve your goals"
        if not outline.get("sections"):
            outline["sections"] = [
                {
                    "title": "Get Started",
                    "bullets": ["Simple setup", "Quick results", "Expert support"]
                }
            ]
        if not outline.get("cta"):
            outline["cta"] = "Learn More"
        
        html = tpl.render(
            brand=brand,
            tokens=tokens,
            outline=outline,
            hero_url=hero_url,
            title=outline.get("headline",""),
            font_links=_font_links(brand["typography"]["heading"], brand["typography"]["body"])
        )
        return html

def write_pdf(html: str, out_path: str) -> bool:
    import os
    if os.getenv("PREFERRED_PDF_ENGINE","weasyprint") != "weasyprint":
        return False
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(out_path)
        return True
    except Exception:
        return False

def write_docx(outline: Dict, brand: Dict, out_path: str):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = brand["typography"]["body"]
    style.font.size = Pt(11)
    h1 = doc.add_heading(outline.get("headline",""), 0)
    h1.style.font.name = brand["typography"]["heading"]
    if outline.get("subhead"):
        doc.add_paragraph(outline["subhead"])
    for s in outline.get("sections",[]):
        doc.add_heading(s.get("title",""), level=1)
        for b in s.get("bullets",[]):
            doc.add_paragraph(b, style=None).style = doc.styles['List Bullet']
    doc.add_paragraph(f"CTA: {outline.get('cta','')}")
    doc.save(out_path)

def zip_outputs(paths, out_zip):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p): z.write(p, arcname=os.path.basename(p))

def generate_assets(slug: str, brand: Dict, template: str, x:str,y:str,z:str,w:str,cta:str, hero_mode:str="skip", force_html:bool=False):
    ts = int(time.time())
    drafts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "drafts", slug))
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "assets", slug))
    ensure_dir(drafts_dir); ensure_dir(assets_dir)

    # Generate content outline
    print(f"🤖 Generating content outline for {template}...")
    outline = outline_for(template, brand, x, y, z, w, cta)
    
    # Ensure CTA is set
    if cta and cta.strip():
        outline["cta"] = cta.strip()
    
    # Polish the outline
    print(f"✨ Polishing content...")
    outline = polish_outline(outline, brand)
    
    # Debug output
    print(f"📝 Generated outline: {outline.get('headline', 'N/A')} | {outline.get('cta', 'N/A')} | {len(outline.get('sections', []))} sections")
    
    # build tokens
    heading = brand.get("typography",{}).get("heading","Inter")
    body = brand.get("typography",{}).get("body","Inter")
    tokens = default_tokens(brand.get("colors",{}), heading, body)

    hero_url = None
    if hero_mode.startswith("path:"):
        local = hero_mode.split("path:",1)[1]
        hero_url = public_url(local)
    elif hero_mode == "auto":
        tone = brand.get('tone','') or 'professional'
        prompt = brand.get("heroBrief","") or f"abstract clean hero image, {tone}"
        hero_path = os.path.join(assets_dir, f"hero_{ts}.png")
        if gen_hero_image(prompt, hero_path):
            hero_url = public_url(hero_path)

    html = render_html(template, brand, tokens, outline, hero_url)
    html_path = os.path.join(drafts_dir, f"{slug}-{template}-{ts}.html")
    
    # Check if Dyad templates are available and use SSR renderer
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from renderer.resolve_templates import resolve_templates
        import subprocess
        
        sel = resolve_templates()
        
        if sel["engine"] == "react" and not force_html:
            print("🎨 Using Dyad React SSR renderer...")
            entry = sel["entry"]
            # Ensure brand json exists at data/brands/{slug}.json
            brand_json_path = f"data/brands/{slug}.json"
            if not os.path.exists(brand_json_path):
                # Create brand json if it doesn't exist
                with open(brand_json_path, 'w') as f:
                    json.dump(brand, f, indent=2, default=str)
                print(f"💾 Created brand config: {brand_json_path}")
            
            try:
                subprocess.run([
                    "pnpm", "ssr",
                    "--brand", slug,
                    "--entry", entry,
                    "--out", html_path,
                    "--props", brand_json_path
                ], check=True)
                print(f"✅ SSR rendered to: {html_path}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ SSR renderer failed, falling back to HTML: {e}")
                with open(html_path, "w", encoding="utf-8") as f: 
                    f.write(html)
        else:
            # Use existing HTML writer
            with open(html_path, "w", encoding="utf-8") as f: 
                f.write(html)
    except Exception as e:
        print(f"⚠️ SSR integration failed, falling back to HTML: {e}")
        with open(html_path, "w", encoding="utf-8") as f: 
            f.write(html)

    pdf_path = os.path.join(drafts_dir, f"{slug}-{template}-{ts}.pdf")
    pdf_ok = write_pdf(html, pdf_path)
    if not pdf_ok: pdf_path = None

    docx_path = os.path.join(drafts_dir, f"{slug}-{template}-{ts}.docx")
    write_docx(outline, brand, docx_path)

    zip_path = os.path.join(drafts_dir, f"{slug}-{template}-{ts}.zip")
    zip_outputs([p for p in [html_path, pdf_path, docx_path] if p], zip_path)

    return {
        "outline": outline,
        "paths": {
            "html": html_path,
            "pdf": pdf_path,
            "docx": docx_path,
            "zip": zip_path
        },
        "public": {
            "html": public_url(html_path),
            "pdf": public_url(pdf_path) if pdf_path else None,
            "docx": public_url(docx_path),
            "zip": public_url(zip_path),
            "hero": hero_url
        },
        "tokens": tokens
    } 