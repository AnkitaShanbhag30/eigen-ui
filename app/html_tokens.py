from typing import Dict, Any, List
from .brand import BrandIdentity, Colors, Typography, DesignAdvisor
import colorsys

def default_tokens(colors: Dict, heading="Inter", body="Inter"):
    return {
        "font_heading": heading,
        "font_body": body,
        "spacing": {"4":16,"6":24,"8":32},
        "radius": {"md":16},
        "colors": {
            "primary": colors.get("primary") or "#2D5BFF",
            "secondary": colors.get("secondary") or "#00C2A8",
            "accent": colors.get("accent") or colors.get("secondary") or "#00C2A8",
            "muted": colors.get("muted") or "#EBEEF3",
            "text": "#0B0B0B",
            "bg": "#FFFFFF",
        },
        "max_width": 880
    }

def compute_contrast_ratio(color1: str, color2: str) -> float:
    """Compute WCAG contrast ratio between two colors"""
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    
    def luminance(r: float, g: float, b: float) -> float:
        def adjust(c: float) -> float:
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    lum1 = luminance(*rgb1)
    lum2 = luminance(*rgb2)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)

def ensure_text_contrast(bg_color: str, text_color: str = None) -> str:
    """Ensure text color meets WCAG contrast requirements"""
    if text_color is None:
        text_color = "#000000"
    
    # Check contrast with current text color
    contrast = compute_contrast_ratio(bg_color, text_color)
    
    if contrast >= 4.5:  # WCAG AA standard
        return text_color
    
    # Try black and white to see which has better contrast
    black_contrast = compute_contrast_ratio(bg_color, "#000000")
    white_contrast = compute_contrast_ratio(bg_color, "#FFFFFF")
    
    if black_contrast >= 4.5:
        return "#000000"
    elif white_contrast >= 4.5:
        return "#FFFFFF"
    else:
        # If neither meets contrast, return the better one
        return "#000000" if black_contrast > white_contrast else "#FFFFFF"

def generate_tokens(brand: BrandIdentity) -> Dict[str, Any]:
    """Generate design tokens from brand identity and design advisor"""
    colors = brand.colors
    typography = brand.typography
    design = brand.design_advisor
    
    # Ensure we have fallback colors
    if not colors.primary:
        colors.primary = "#2563EB"
    if not colors.secondary:
        colors.secondary = "#F59E0B"
    if not colors.accent:
        colors.accent = colors.secondary
    if not colors.muted:
        colors.muted = "#6B7280"
    
    # Ensure text colors meet contrast requirements
    colors.text = ensure_text_contrast(colors.bg, colors.text)
    
    # Generate spacing scale based on design advisor
    base_spacing = 16
    spacing_scale = design.spacing_scale
    spacing = {
        "1": int(base_spacing * spacing_scale[0]),
        "2": int(base_spacing * spacing_scale[0]),
        "3": int(base_spacing * spacing_scale[1]),
        "4": int(base_spacing * spacing_scale[1]),
        "6": int(base_spacing * spacing_scale[2]),
        "8": int(base_spacing * spacing_scale[2]),
        "12": int(base_spacing * spacing_scale[3]),
        "16": int(base_spacing * spacing_scale[3]),
        "24": int(base_spacing * spacing_scale[3] * 1.5),
        "32": int(base_spacing * spacing_scale[3] * 2)
    }
    
    # Generate font scale
    base_font_size = 16
    font_scale = {
        "xs": int(base_font_size * 0.75),
        "sm": int(base_font_size * 0.875),
        "base": base_font_size,
        "lg": int(base_font_size * 1.125),
        "xl": int(base_font_size * 1.25),
        "2xl": int(base_font_size * 1.5),
        "3xl": int(base_font_size * 2),
        "4xl": int(base_font_size * 2.5),
        "5xl": int(base_font_size * 3)
    }
    
    # Generate line heights
    leading = {
        "tight": 1.15,
        "normal": 1.4,
        "loose": 1.6,
        "relaxed": 1.8
    }
    
    # Generate shadows based on layout variant
    shadow_intensity = {"A": 0.08, "B": 0.12, "C": 0.16}[design.layout_variant]
    shadows = {
        "sm": f"0 1px 2px rgba(0,0,0,{shadow_intensity})",
        "md": f"0 4px 6px rgba(0,0,0,{shadow_intensity})",
        "lg": f"0 10px 15px rgba(0,0,0,{shadow_intensity})",
        "xl": f"0 20px 25px rgba(0,0,0,{shadow_intensity})"
    }
    
    # Generate border radius based on design advisor
    radius = design.radius
    
    # Generate max width based on layout variant
    max_widths = {"A": 860, "B": 1024, "C": 1200}
    max_width = max_widths.get(design.layout_variant, 860)
    
    tokens = {
        "font_heading": typography.heading or "Inter",
        "font_body": typography.body or "Inter",
        "font_fallbacks": typography.fallbacks,
        "scale": font_scale,
        "leading": leading,
        "spacing": spacing,
        "radius": radius,
        "shadows": shadows,
        "colors": {
            "primary": colors.primary,
            "secondary": colors.secondary,
            "accent": colors.accent,
            "muted": colors.muted,
            "bg": colors.bg,
            "text": colors.text,
            "palette": colors.palette
        },
        "max_width": max_width,
        "layout_variant": design.layout_variant
    }
    
    return tokens

def get_google_fonts_links(tokens: Dict[str, Any]) -> List[str]:
    """Generate Google Fonts links for the selected typography"""
    fonts = []
    
    # Add heading font if it's a Google Font
    if tokens["font_heading"] and tokens["font_heading"] != "Inter":
        fonts.append(tokens["font_heading"])
    
    # Add body font if it's a Google Font
    if tokens["font_body"] and tokens["font_body"] != "Inter":
        fonts.append(tokens["font_body"])
    
    # Remove duplicates and filter known Google Fonts
    google_fonts = {
        "Inter", "Roboto", "Open Sans", "Lato", "Poppins", "Montserrat", 
        "Source Sans Pro", "Nunito", "Ubuntu", "Raleway", "PT Sans",
        "Merriweather", "Playfair Display", "Lora", "Crimson Text",
        "Libre Baskerville", "Source Serif Pro", "Noto Serif", "Bitter"
    }
    
    fonts = [f for f in fonts if f in google_fonts]
    
    if not fonts:
        return []
    
    # Generate Google Fonts link
    font_families = "&family=".join([f"{f}:wght@400;500;600;700" for f in fonts])
    return [f"https://fonts.googleapis.com/css2?{font_families}&display=swap"]

def generate_css_variables(tokens: Dict[str, Any]) -> str:
    """Generate CSS variables from tokens"""
    css_vars = []
    
    # Font variables
    css_vars.append(f'--font-heading: "{tokens["font_heading"]}", {", ".join(tokens["font_fallbacks"])};')
    css_vars.append(f'--font-body: "{tokens["font_body"]}", {", ".join(tokens["font_fallbacks"])};')
    
    # Color variables
    for key, value in tokens["colors"].items():
        if key != "palette":
            css_vars.append(f'--color-{key}: {value};')
    
    # Spacing variables
    for key, value in tokens["spacing"].items():
        css_vars.append(f'--space-{key}: {value}px;')
    
    # Font scale variables
    for key, value in tokens["scale"].items():
        css_vars.append(f'--text-{key}: {value}px;')
    
    # Radius variables
    for key, value in tokens["radius"].items():
        css_vars.append(f'--radius-{key}: {value}px;')
    
    # Shadow variables
    for key, value in tokens["shadows"].items():
        css_vars.append(f'--shadow-{key}: {value};')
    
    # Layout variables
    css_vars.append(f'--max-width: {tokens["max_width"]}px;')
    
    return "\n  ".join(css_vars)
