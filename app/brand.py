from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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

class LayoutElement(BaseModel):
    """Represents a layout element with its properties"""
    tag: str
    classes: List[str] = Field(default_factory=list)
    id: Optional[str] = None
    text_content: str = ""
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "width": 0, "height": 0})
    styles: Dict[str, str] = Field(default_factory=dict)
    children_count: int = 0
    is_visible: bool = True

class DesignPattern(BaseModel):
    """Represents a design pattern found on the page"""
    type: str  # 'grid', 'card', 'hero', 'navigation', 'footer', 'sidebar'
    elements: List[LayoutElement] = Field(default_factory=list)
    layout_type: str = "block"  # 'horizontal', 'vertical', 'grid', 'flexbox'
    spacing: Dict[str, int] = Field(default_factory=dict)
    alignment: str = "left"  # 'left', 'center', 'right', 'justify'

class PageStructure(BaseModel):
    """Represents the overall page structure"""
    header: Optional[Dict[str, Any]] = None
    hero: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    sidebar: Optional[Dict[str, Any]] = None
    footer: Optional[Dict[str, Any]] = None
    sections: List[Dict[str, Any]] = Field(default_factory=list)

class SpacingSystem(BaseModel):
    """Represents the spacing system used on the page"""
    margins: List[str] = Field(default_factory=list)
    padding: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    common_values: List[str] = Field(default_factory=list)

class LayoutGrid(BaseModel):
    """Represents grid layout information"""
    grid_systems: List[Dict[str, Any]] = Field(default_factory=list)
    column_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    breakpoints: List[str] = Field(default_factory=list)

class ComponentPatterns(BaseModel):
    """Represents common component patterns"""
    buttons: List[Dict[str, Any]] = Field(default_factory=list)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    navigation: List[Dict[str, Any]] = Field(default_factory=list)
    cards: List[Dict[str, Any]] = Field(default_factory=list)

class VisualHierarchy(BaseModel):
    """Represents visual hierarchy information"""
    headings: Dict[str, int] = Field(default_factory=dict)
    text_sizes: List[str] = Field(default_factory=list)
    emphasis: List[str] = Field(default_factory=list)

class InteractionPatterns(BaseModel):
    """Represents interaction patterns and behaviors"""
    hover_effects: List[Dict[str, Any]] = Field(default_factory=list)
    click_handlers: List[Dict[str, Any]] = Field(default_factory=list)
    form_interactions: List[Dict[str, Any]] = Field(default_factory=list)

class CSSStructure(BaseModel):
    """Represents CSS structure and organization"""
    inline_styles: Dict[str, int] = Field(default_factory=dict)
    css_classes: Dict[str, int] = Field(default_factory=dict)
    css_variables: List[str] = Field(default_factory=list)
    media_queries: List[str] = Field(default_factory=list)

class UILayoutData(BaseModel):
    """Comprehensive UI and layout data extracted from the brand"""
    page_structure: PageStructure = PageStructure()
    design_patterns: List[DesignPattern] = Field(default_factory=list)
    spacing_system: SpacingSystem = SpacingSystem()
    layout_grid: LayoutGrid = LayoutGrid()
    component_patterns: ComponentPatterns = ComponentPatterns()
    visual_hierarchy: VisualHierarchy = VisualHierarchy()
    responsive_breakpoints: List[str] = Field(default_factory=list)
    interaction_patterns: InteractionPatterns = InteractionPatterns()
    css_structure: CSSStructure = CSSStructure()
    screenshot_path: Optional[str] = None
    layout_analysis: Dict[str, Any] = Field(default_factory=dict)

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
    logo_path_public: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    source_notes: Optional[str] = None
    ui_layout: UILayoutData = UILayoutData()  # New field for UI/layout data

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
        
        brand = BrandIdentity(**data)
        
        # Compute public logo URL if logo_path exists
        if brand.logo_path:
            from .util import public_url
            brand.logo_path_public = public_url(brand.logo_path)
        
        return brand
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