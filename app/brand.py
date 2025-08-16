from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import os
import re
from pathlib import Path

class Colors(BaseModel):
    primary: Optional[str] = None
    secondary: Optional[str] = None
    accent: Optional[str] = None
    muted: Optional[str] = None
    bg: str = "#FFFFFF"
    text: str = "#0B0B0B"
    palette: List[str] = Field(default_factory=list)

class Typography(BaseModel):
    heading: Optional[str] = None
    body: Optional[str] = None
    fallbacks: List[str] = Field(default_factory=lambda: ["Inter", "system-ui", "Segoe UI", "Roboto", "Helvetica", "Arial"])

class DesignAdvisor(BaseModel):
    typography: Typography = Typography()
    layout_variant: str = "A"  # A, B, or C
    spacing_scale: List[float] = Field(default_factory=lambda: [1, 1.25, 1.6, 2])
    radius: Dict[str, int] = Field(default_factory=lambda: {"sm": 8, "md": 14, "lg": 22})
    hero_brief: Optional[str] = None

class BrandIdentity(BaseModel):
    slug: str
    name: str
    website: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    colors: Colors = Colors()
    fonts_detected: List[str] = Field(default_factory=list)
    typography: Typography = Typography()
    design_advisor: DesignAdvisor = DesignAdvisor()
    tone: str = ""
    keywords: List[str] = Field(default_factory=list)
    logo_path: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    source_notes: Optional[str] = None

def sanitize_slug(slug: str) -> str:
    """Convert slug to safe filename"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', slug.lower())

def get_brand_path(slug: str) -> str:
    """Get path for brand JSON file"""
    safe_slug = sanitize_slug(slug)
    return f"data/brands/{safe_slug}.json"

def save_brand(brand: BrandIdentity, slug: str) -> str:
    """Save brand identity to JSON file"""
    path = get_brand_path(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(brand.dict(), f, indent=2)
    
    return path

def load_brand(slug: str) -> Optional[BrandIdentity]:
    """Load brand identity from JSON file"""
    path = get_brand_path(slug)
    
    if not os.path.exists(path):
        return None
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return BrandIdentity(**data)
    except Exception as e:
        print(f"Error loading brand {slug}: {e}")
        return None

def get_asset_dir(slug: str) -> str:
    """Get directory for brand assets"""
    safe_slug = sanitize_slug(slug)
    return f"data/assets/{safe_slug}"

def ensure_asset_dirs(slug: str):
    """Ensure asset directories exist"""
    base_dir = get_asset_dir(slug)
    os.makedirs(f"{base_dir}/raw", exist_ok=True)
    os.makedirs(f"{base_dir}/uploads", exist_ok=True)
    os.makedirs(f"{base_dir}/hero", exist_ok=True)

def get_drafts_dir() -> str:
    """Get drafts directory path"""
    return "data/drafts"

def get_kits_dir() -> str:
    """Get brand kits directory path"""
    return "data/kits"

def ensure_output_dirs():
    """Ensure all output directories exist"""
    os.makedirs(get_drafts_dir(), exist_ok=True)
    os.makedirs(get_kits_dir(), exist_ok=True) 