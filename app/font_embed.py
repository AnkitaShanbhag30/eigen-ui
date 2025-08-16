# app/font_embed.py
import base64
import os
from typing import Optional

def font_to_b64(path: str) -> Optional[str]:
    """Convert font file to base64 string for embedding in HTML"""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return None

def get_google_fonts_css(font_families: list) -> str:
    """Generate Google Fonts CSS link for detected fonts"""
    if not font_families:
        return ""
    
    # Clean up font names and create Google Fonts URL
    clean_fonts = []
    for font in font_families[:3]:  # Limit to 3 fonts
        if font and font not in ['sans-serif', 'serif', 'monospace']:
            # Remove quotes and clean up font name
            clean_font = font.replace('"', '').replace("'", "").split(',')[0].strip()
            if clean_font and len(clean_font) > 1:
                clean_fonts.append(clean_font.replace(' ', '+'))
    
    if not clean_fonts:
        return ""
    
    # Create Google Fonts URL
    font_url = f"https://fonts.googleapis.com/css2?family={'&family='.join(clean_fonts)}:wght@300;400;500;600;700&display=swap"
    return f'<link href="{font_url}" rel="stylesheet">'
