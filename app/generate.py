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
    sys = "You are a precise marketing writer. Return ONLY valid JSON."
    # Use format() instead of f-string to avoid format specifier issues
    user = """template:{}
brand_tone:{}
keywords:{}
audience:{}
goal:{}
project:{}
notes:{}
schema: {{"headline":"","subhead":"","sections":[{{"title":"","bullets":[]}}], "cta":"", "meta":{{"seoTitle":"","seoDesc":"","tags":[]}}}}
word_band: onepager=400-700, newsletter=450-900, blogpost=800-1200""".format(
        template,
        brand.get('tone',''),
        ', '.join(brand.get('keywords',[])[:12]),
        z, y, x, w
    )
    return generate_json(sys, user)

def polish_outline(o: Dict, brand: Dict) -> Dict:
    sys = "You are a marketing editor. Improve clarity and specificity. Return ONLY the same JSON shape."
    user = json.dumps({"outline": o, "tone": brand.get("tone","")})
    return generate_json(sys, user)

def render_html(template_key: str, brand: Dict, tokens: Dict, outline: Dict, hero_url: str|None):
    env = get_env()
    tpl = env.get_template(f"{template_key}.html.j2")
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

def generate_assets(slug: str, brand: Dict, template: str, x:str,y:str,z:str,w:str,cta:str, hero_mode:str="skip"):
    ts = int(time.time())
    drafts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "drafts", slug))
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "assets", slug))
    ensure_dir(drafts_dir); ensure_dir(assets_dir)

    outline = polish_outline(outline_for(template, brand, x,y,z,w,cta), brand)

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
    with open(html_path, "w", encoding="utf-8") as f: f.write(html)

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