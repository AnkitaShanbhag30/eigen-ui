"""
Palette Harmonizer System
Provides token scales, pairing rules, contrast checks, and AI-judged color combinations.
Uses OkLCH color space for better perceptual uniformity.
"""

from typing import Dict, List, Tuple, Optional
import math

try:
    from coloraide import Color
    COLORAIDE_AVAILABLE = True
except ImportError:
    Color = None
    COLORAIDE_AVAILABLE = False

def to_oklch(hex_str: str) -> Tuple[float, float, float]:
    """Convert hex color to OkLCH color space"""
    if COLORAIDE_AVAILABLE and Color:
        try:
            c = Color(hex_str).convert("oklch")
            return float(c.l), float(c.c), float(c.h)
        except Exception:
            pass
    
    # Fallback to rough luminance calculation
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    
    r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
    # Convert to relative luminance (Y)
    Y = (0.2126*r + 0.7152*g + 0.0722*b)/255.0
    return (Y, 0.08, 30.0)  # Default chroma and hue

def from_oklch(L: float, C: float, H: float) -> str:
    """Convert OkLCH color space to hex string"""
    if COLORAIDE_AVAILABLE and Color:
        try:
            return Color("oklch", [L, C, H]).convert("srgb").to_string(hex=True)
        except Exception:
            pass
    
    # Fallback: clamp grayscale
    v = max(0, min(255, int(L * 255)))
    return f"#{v:02x}{v:02x}{v:02x}"

def tone_scale(base_hex: str, steps: List[float] = None) -> List[str]:
    """Generate tone scale from base color"""
    if steps is None:
        steps = [0.98, 0.95, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.05]
    
    L, C, H = to_oklch(base_hex)
    
    # Keep hue, vary lightness, adjust chroma for darker colors
    colors = []
    for l in steps:
        # Reduce chroma for very light and very dark colors
        chroma_factor = 1.0
        if l < 0.2 or l > 0.9:
            chroma_factor = 0.5
        elif l < 0.3 or l > 0.8:
            chroma_factor = 0.8
        
        adjusted_chroma = max(0.02, C * chroma_factor)
        colors.append(from_oklch(L=l, C=adjusted_chroma, H=H))
    
    return colors

def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG contrast ratio between two colors"""
    def rel_lum(hex_color: str) -> float:
        """Calculate relative luminance"""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        x = [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)]
        
        def linearize(v: float) -> float:
            """Linearize sRGB values"""
            return v/12.92 if v <= 0.03928 else ((v + 0.055)/1.055)**2.4
        
        r, g, b = map(linearize, x)
        return 0.2126*r + 0.7152*g + 0.0722*b
    
    L1, L2 = rel_lum(hex1), rel_lum(hex2)
    L1, L2 = max(L1, L2), min(L1, L2)
    return (L1 + 0.05)/(L2 + 0.05)

def is_contrast_safe(bg_color: str, fg_color: str, level: str = "AA") -> bool:
    """Check if color combination meets WCAG contrast requirements"""
    ratio = contrast_ratio(bg_color, fg_color)
    
    if level == "AAA":
        return ratio >= 7.0  # AAA standard
    elif level == "AA":
        return ratio >= 4.5  # AA standard (body text)
    elif level == "AA_LARGE":
        return ratio >= 3.0  # AA standard (large text)
    else:
        return ratio >= 4.5  # Default to AA

def propose_theme(brand: Dict) -> Dict:
    """Propose a complete color theme with tokens and pairings"""
    # Extract brand colors
    colors = brand.get("colors", {})
    primary = colors.get("primary", "#241461")
    secondary = colors.get("secondary", "#0099ff")
    accent = colors.get("accent", "#3a3a3a")
    muted = colors.get("muted", "#d9d8fc")
    
    # Generate tone scales
    brand_scale = tone_scale(primary)
    accent_scale = tone_scale(secondary)
    neutral_scale = tone_scale(accent)
    surface_scale = tone_scale("#ffffff")
    
    # Create token system
    tokens = {
        # Background and surface colors
        "bg": surface_scale[0],           # Pure white
        "surface": surface_scale[2],      # Very light gray
        "surface-contrast": brand_scale[8], # Dark brand color
        
        # Text colors
        "text": "#0B0B0B",               # Near black
        "text-muted": neutral_scale[4],   # Medium gray
        
        # Brand colors
        "brand-50": brand_scale[0],      # Very light brand
        "brand-100": brand_scale[1],
        "brand-200": brand_scale[2],
        "brand-300": brand_scale[3],
        "brand-400": brand_scale[4],
        "brand-500": primary,            # Base brand color
        "brand-600": brand_scale[5],
        "brand-700": brand_scale[6],
        "brand-800": brand_scale[7],
        "brand-900": brand_scale[8],     # Very dark brand
        
        # Accent colors
        "accent-50": accent_scale[0],
        "accent-100": accent_scale[1],
        "accent-200": accent_scale[2],
        "accent-300": accent_scale[3],
        "accent-400": accent_scale[4],
        "accent-500": secondary,         # Base accent color
        "accent-600": accent_scale[5],
        "accent-700": accent_scale[6],
        "accent-800": accent_scale[7],
        "accent-900": accent_scale[8],
        
        # Neutral colors
        "neutral-50": neutral_scale[0],
        "neutral-100": neutral_scale[1],
        "neutral-200": neutral_scale[2],
        "neutral-300": neutral_scale[3],
        "neutral-400": neutral_scale[4],
        "neutral-500": accent,           # Base neutral color
        "neutral-600": neutral_scale[5],
        "neutral-700": neutral_scale[6],
        "neutral-800": neutral_scale[7],
        "neutral-900": neutral_scale[8],
        
        # Semantic colors
        "success": "#10b981",            # Green
        "warning": "#f59e0b",            # Amber
        "error": "#ef4444",              # Red
        "info": secondary,               # Use accent for info
        
        # Muted colors
        "muted": muted,
        "muted-foreground": neutral_scale[6],
    }
    
    # Create color pairings with contrast safety
    pairs = {}
    
    # CTA button pairings
    cta_bg = tokens["brand-500"]
    cta_fg = "#ffffff"
    if not is_contrast_safe(cta_bg, cta_fg, "AA"):
        # Try darker brand color
        cta_bg = tokens["brand-700"]
        if not is_contrast_safe(cta_bg, cta_fg, "AA"):
            cta_fg = "#000000"  # Fallback to black
    
    pairs["cta_bg"] = cta_bg
    pairs["cta_fg"] = cta_fg
    
    # Chip/tag pairings
    chip_bg = tokens["muted"]
    chip_fg = tokens["brand-700"]
    if not is_contrast_safe(chip_bg, chip_fg, "AA"):
        chip_fg = tokens["brand-900"]
    
    pairs["chip_bg"] = chip_bg
    pairs["chip_fg"] = chip_fg
    
    # Card pairings
    card_bg = tokens["surface"]
    card_fg = tokens["text"]
    if not is_contrast_safe(card_bg, card_fg, "AA"):
        card_bg = tokens["bg"]  # Fallback to white
    
    pairs["card_bg"] = card_bg
    pairs["card_fg"] = card_fg
    
    # Link pairings
    pairs["link"] = tokens["accent-500"]
    pairs["link_hover"] = tokens["accent-700"]
    
    # Border pairings
    pairs["border"] = tokens["neutral-200"]
    pairs["border-focus"] = tokens["brand-500"]
    
    return {
        "tokens": tokens,
        "pairs": pairs,
        "base_colors": {
            "primary": primary,
            "secondary": secondary,
            "accent": accent,
            "muted": muted
        }
    }

def propose_theme_variants(brand: Dict, num_variants: int = 3) -> List[Dict]:
    """Propose multiple theme variants with slight variations"""
    base_theme = propose_theme(brand)
    variants = [base_theme]
    
    if num_variants > 1:
        # Create variants with different chroma adjustments
        colors = brand.get("colors", {})
        primary = colors.get("primary", "#241461")
        secondary = colors.get("secondary", "#0099ff")
        
        # Variant 1: Higher chroma (more vibrant)
        if COLORAIDE_AVAILABLE:
            try:
                c = Color(primary).convert("oklch")
                L, C, H = float(c.l), float(c.c), float(c.h)
                # Increase chroma by 20%
                vibrant_primary = Color("oklch", [L, C * 1.2, H]).convert("srgb").to_string(hex=True)
                
                variant_colors = colors.copy()
                variant_colors["primary"] = vibrant_primary
                variant_brand = brand.copy()
                variant_brand["colors"] = variant_colors
                
                variant_theme = propose_theme(variant_brand)
                variant_theme["variant_name"] = "vibrant"
                variants.append(variant_theme)
            except Exception:
                pass
        
        # Variant 2: Lower chroma (more muted)
        if COLORAIDE_AVAILABLE:
            try:
                c = Color(primary).convert("oklch")
                L, C, H = float(c.l), float(c.c), float(c.h)
                # Decrease chroma by 20%
                muted_primary = Color("oklch", [L, C * 0.8, H]).convert("srgb").to_string(hex=True)
                
                variant_colors = colors.copy()
                variant_colors["primary"] = muted_primary
                variant_brand = brand.copy()
                variant_brand["colors"] = variant_colors
                
                variant_theme = propose_theme(variant_brand)
                variant_theme["variant_name"] = "muted"
                variants.append(variant_theme)
            except Exception:
                pass
    
    return variants[:num_variants]

def validate_theme_contrast(theme: Dict) -> Dict:
    """Validate theme contrast ratios and suggest fixes"""
    tokens = theme["tokens"]
    pairs = theme["pairs"]
    
    issues = []
    fixes = {}
    
    # Check CTA contrast
    cta_bg = pairs.get("cta_bg", tokens.get("brand-500"))
    cta_fg = pairs.get("cta_fg", "#ffffff")
    if not is_contrast_safe(cta_bg, cta_fg, "AA"):
        issues.append(f"CTA contrast too low: {contrast_ratio(cta_bg, cta_fg):.2f}")
        # Suggest fix
        if is_contrast_safe(cta_bg, "#000000", "AA"):
            fixes["cta_fg"] = "#000000"
        else:
            fixes["cta_bg"] = tokens.get("brand-700", "#000000")
    
    # Check card contrast
    card_bg = pairs.get("card_bg", tokens.get("surface"))
    card_fg = pairs.get("card_fg", tokens.get("text"))
    if not is_contrast_safe(card_bg, card_fg, "AA"):
        issues.append(f"Card contrast too low: {contrast_ratio(card_bg, card_fg):.2f}")
        fixes["card_bg"] = tokens.get("bg", "#ffffff")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "fixes": fixes,
        "overall_score": len(issues)  # Lower is better
    }

def get_color_usage_guide(theme: Dict) -> Dict:
    """Get usage guide for the color theme"""
    tokens = theme["tokens"]
    pairs = theme["pairs"]
    
    return {
        "backgrounds": {
            "primary": tokens["bg"],
            "secondary": tokens["surface"],
            "brand": tokens["brand-50"],
            "accent": tokens["accent-50"]
        },
        "text": {
            "primary": tokens["text"],
            "secondary": tokens["text-muted"],
            "brand": tokens["brand-700"],
            "accent": tokens["accent-700"]
        },
        "interactive": {
            "buttons": {
                "primary": {"bg": pairs["cta_bg"], "fg": pairs["cta_fg"]},
                "secondary": {"bg": tokens["surface"], "fg": tokens["text"], "border": pairs["border"]}
            },
            "links": {"normal": pairs["link"], "hover": pairs["link_hover"]}
        },
        "components": {
            "cards": {"bg": pairs["card_bg"], "fg": pairs["card_fg"], "border": pairs["border"]},
            "chips": {"bg": pairs["chip_bg"], "fg": pairs["chip_fg"]}
        }
    }
