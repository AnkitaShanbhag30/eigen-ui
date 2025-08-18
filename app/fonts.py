import requests
import re
from typing import List, Set, Optional
from urllib.parse import urljoin

def fetch_css(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch CSS content from URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching CSS from {url}: {e}")
        return None

def extract_google_fonts(css_content: str) -> List[str]:
    """Extract font families from Google Fonts CSS"""
    fonts = []
    
    # Look for Google Fonts family parameter
    family_matches = re.findall(r'family=([^&]+)', css_content)
    for match in family_matches:
        # Split by + and clean up
        font_names = [name.strip() for name in match.split('+')]
        fonts.extend(font_names)
    
    return fonts

def extract_font_faces(css_content: str) -> List[str]:
    """Extract font families from @font-face declarations"""
    fonts = []
    
    # Look for @font-face font-family declarations
    font_face_matches = re.findall(r'@font-face\s*{[^}]*font-family\s*:\s*["\']?([^"\';}]+)', css_content, re.IGNORECASE)
    for match in font_face_matches:
        # Clean up font name
        font_name = match.strip().strip('"\'')
        if font_name:
            fonts.append(font_name)
    
    return fonts

def extract_font_families(css_content: str) -> List[str]:
    """Extract all font families from CSS content"""
    fonts = []
    
    # Extract from Google Fonts
    fonts.extend(extract_google_fonts(css_content))
    
    # Extract from @font-face
    fonts.extend(extract_font_faces(css_content))
    
    # Look for general font-family declarations
    font_family_matches = re.findall(r'font-family\s*:\s*([^;]+)', css_content, re.IGNORECASE)
    for match in font_family_matches:
        # Split by comma and clean up
        font_names = [name.strip().strip('"\'') for name in match.split(',')]
        fonts.extend([name for name in font_names if name])
    
    return fonts

def get_fonts_from_css_urls(css_urls: List[str]) -> List[str]:
    """Fetch CSS from multiple URLs and extract font families"""
    all_fonts = []
    
    for url in css_urls:
        css_content = fetch_css(url)
        if css_content:
            fonts = extract_font_families(css_content)
            all_fonts.extend(fonts)
    
    # Remove duplicates and clean up
    unique_fonts = list(set(all_fonts))
    clean_fonts = []
    
    for font in unique_fonts:
        # Remove common CSS values and clean up
        if font.lower() not in ['inherit', 'initial', 'unset', 'serif', 'sans-serif', 'monospace']:
            clean_fonts.append(font)
    
    return clean_fonts[:10]  # Limit to 10 fonts

def get_default_fonts() -> List[str]:
    """Return default fonts when extraction fails"""
    return ["Inter"] 

def _extract_fonts_from_html(html: str) -> List[str]:
    """Lightweight extraction of font families from HTML inline styles or link tags."""
    fonts: List[str] = []
    try:
        # Look for Google Fonts link tags
        link_matches = re.findall(r'href="https://fonts.googleapis.com/[^\"]+family=([^"]+)', html, re.IGNORECASE)
        for match in link_matches:
            parts = [p.strip() for p in match.split("&")[0].split(':')[0].split('+') if p.strip()]
            fonts.extend(parts)

        # Look for inline style="font-family: ..." occurrences
        inline_matches = re.findall(r'font-family\s*:\s*([^;"\']+)', html, re.IGNORECASE)
        for m in inline_matches:
            for name in [n.strip().strip('"\'') for n in m.split(',')]:
                if name and name.lower() not in ['inherit', 'initial', 'unset', 'serif', 'sans-serif', 'monospace']:
                    fonts.append(name)
    except Exception:
        pass
    # Deduplicate and cap
    uniq: List[str] = []
    for f in fonts:
        if f not in uniq:
            uniq.append(f)
    return uniq[:10]

def get_fonts_from_html_and_css(html: str, css_urls: List[str]) -> List[str]:
    """Extract fonts from both HTML and linked CSS.

    - HTML: parse Google Fonts links and inline font-family usage
    - CSS: fetch each CSS and extract @font-face and font-family declarations
    """
    fonts = []
    fonts.extend(_extract_fonts_from_html(html or ""))
    try:
        fonts.extend(get_fonts_from_css_urls(css_urls or []))
    except Exception:
        pass
    # Normalize and dedupe
    clean = []
    for f in fonts:
        if f and f not in clean:
            clean.append(f)
    return clean[:10] if clean else get_default_fonts()