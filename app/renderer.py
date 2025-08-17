import io
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
from playwright.sync_api import sync_playwright
from .templates_loader import TemplatesLoader
from .html_tokens import generate_tokens


class RenderPayload(BaseModel):
    template: str = Field(..., description="Template name without .html.j2, e.g., 'onepager'")
    format: str = Field("png", description="'png' or 'pdf'")
    data: Dict[str, Any] = Field(default_factory=dict)
    width: int = 1200
    height: int = 1600
    scale: int = 2  # device scale factor (2=retina)
    # For PDF, width/height are still used to compute size in inches at 96 dpi


def _render_png(html: str, width: int, height: int, scale: int) -> bytes:
    """Render HTML to PNG with enhanced quality settings"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": width, "height": height})
            page.emulate_media(media="screen")
            page.set_default_navigation_timeout(15000)
            page.set_default_timeout(15000)
            page.set_content(html, wait_until="networkidle")
            page.wait_for_timeout(150)
            buf = page.screenshot(full_page=False, animations="disabled", scale=scale)
            return buf
        finally:
            try:
                browser.close()
            except Exception:
                pass

def _render_pdf(html: str, width_px: int, height_px: int, dpi: int = 96) -> bytes:
    """Render HTML to PDF with enhanced quality settings"""
    w_in, h_in = width_px / dpi, height_px / dpi
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.emulate_media(media="print")
            page.set_default_navigation_timeout(15000)
            page.set_default_timeout(15000)
            page.set_content(html, wait_until="networkidle")
            page.wait_for_timeout(100)
            pdf = page.pdf(width=f"{w_in}in", height=f"{h_in}in", print_background=True)
            return pdf
        finally:
            try:
                browser.close()
            except Exception:
                pass


def validate_render_payload(data: Dict[str, Any]) -> RenderPayload:
    """Validate render payload and return RenderPayload object"""
    try:
        payload = RenderPayload(**data)
        # Additional validation
        if payload.format.lower() not in ['png', 'pdf']:
            raise ValidationError.from_exception(
                ValueError("Format must be 'png' or 'pdf'"), 
                model=RenderPayload
            )
        if payload.scale < 1 or payload.scale > 3:
            raise ValidationError.from_exception(
                ValueError("Scale must be between 1 and 3"), 
                model=RenderPayload
            )
        return payload
    except ValidationError as e:
        raise e


def render_to_bytes(payload: RenderPayload, html: str) -> bytes:
    """Render HTML to bytes based on format"""
    fmt = payload.format.lower()
    
    if fmt == "pdf":
        return _render_pdf(html, payload.width, payload.height)
    elif fmt == "png":
        return _render_png(html, payload.width, payload.height, payload.scale)
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def get_mimetype_and_filename(payload: RenderPayload) -> tuple[str, str]:
    """Get mimetype and filename for the rendered output"""
    fmt = payload.format.lower()
    if fmt == "pdf":
        return "application/pdf", f"{payload.template}.pdf"
    elif fmt == "png":
        return "image/png", f"{payload.template}.png"
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def render_template_with_brand(template_name: str, brand_data: Dict[str, Any], 
                             custom_data: Dict[str, Any] = None) -> str:
    """Render a template using the existing template system with brand data"""
    try:
        # Initialize template loader
        template_loader = TemplatesLoader()
        
        # Check if template exists
        if not template_loader.template_exists(template_name):
            raise ValueError(f"Template '{template_name}' not found. Available: {template_loader.list_templates()}")
        
        # Prepare context data with proper structure
        context = {
            'brand': brand_data,
            'title': custom_data.get('title', brand_data.get('name', 'Brand Content')),
            'subtitle': custom_data.get('subtitle', ''),
            'cta': custom_data.get('cta', ''),
            'hero_url': custom_data.get('hero_url', None),
            'font_links': custom_data.get('font_links', ''),
            'custom_data': custom_data or {}  # Pass all custom data for template access
        }
        
        # If custom data includes outline, use it; otherwise create a basic one
        if 'outline' in custom_data:
            context['outline'] = custom_data['outline']
        else:
            # Create basic outline from custom data
            context['outline'] = {
                'headline': custom_data.get('title', brand_data.get('name', 'Brand Content')),
                'subhead': custom_data.get('subtitle', custom_data.get('description', '')),
                'sections': custom_data.get('sections', []),
                'cta': custom_data.get('cta', 'Learn More')
            }
        
        # Generate design tokens for styling
        try:
            from .brand import BrandIdentity
            brand_obj = BrandIdentity(**brand_data)
            tokens = generate_tokens(brand_obj)
            context['tokens'] = tokens
        except Exception as e:
            # Fallback to basic tokens if generation fails
            context['tokens'] = {
                'colors': {
                    'primary': brand_data.get('colors', {}).get('primary', '#0C69F5'),
                    'secondary': brand_data.get('colors', {}).get('secondary', '#6b7280'),
                    'accent': brand_data.get('colors', {}).get('accent', '#f59e0b'),
                    'muted': brand_data.get('colors', {}).get('muted', '#9ca3af'),
                    'text': brand_data.get('colors', {}).get('text', '#111827'),
                    'bg': brand_data.get('colors', {}).get('bg', '#ffffff')
                },
                'font_heading': brand_data.get('typography', {}).get('heading', 'Inter'),
                'font_body': brand_data.get('typography', {}).get('body', 'Inter'),
                'spacing': {
                    '1': 4, '2': 8, '4': 16, '6': 24, '8': 32, '10': 40
                },
                'radius': {
                    'sm': 6, 'md': 12, 'lg': 20
                },
                'max_width': 1200
            }
        
        # Render the template
        return template_loader.render_template(template_name, context)
        
    except Exception as e:
        raise ValueError(f"Failed to render template '{template_name}': {str(e)}")
