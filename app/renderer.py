import io
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
from playwright.sync_api import sync_playwright


class RenderPayload(BaseModel):
    template: str = Field(..., description="Template name without .html, e.g., 'onepager'")
    format: str = Field("png", description="'png' or 'pdf'")
    data: Dict[str, Any] = Field(default_factory=dict)
    width: int = 1200
    height: int = 1600
    scale: int = 2  # device scale factor (2=retina)
    # For PDF, width/height are still used to compute size in inches at 96 dpi


def _render_png(html: str, width: int, height: int, scale: int) -> bytes:
    """Render HTML to PNG using Playwright Chromium"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(device_scale_factor=scale, viewport={"width": width, "height": height})
            page.set_content(html, wait_until="networkidle")
            buf = page.screenshot(full_page=False)
            browser.close()
            return buf
    except Exception as e:
        # Ensure browser is closed on any error
        if 'browser' in locals():
            try:
                browser.close()
            except:
                pass
        raise e


def _render_pdf(html: str, width_px: int, height_px: int, dpi: int = 96) -> bytes:
    """Render HTML to PDF using Playwright Chromium"""
    try:
        w_in = width_px / dpi
        h_in = height_px / dpi
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            pdf_bytes = page.pdf(width=f"{w_in}in", height=f"{h_in}in", print_background=True)
            browser.close()
            return pdf_bytes
    except Exception as e:
        # Ensure browser is closed on any error
        if 'browser' in locals():
            try:
                browser.close()
            except:
                pass
        raise e


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
