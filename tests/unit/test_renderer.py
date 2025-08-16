import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.renderer import (
    RenderPayload, 
    validate_render_payload, 
    render_to_bytes, 
    get_mimetype_and_filename,
    _render_png,
    _render_pdf
)


class TestRenderPayload:
    """Test RenderPayload model validation"""
    
    def test_valid_payload(self):
        """Test valid payload creation"""
        data = {
            "template": "onepager",
            "format": "png",
            "data": {"title": "Test"},
            "width": 1200,
            "height": 1600,
            "scale": 2
        }
        payload = RenderPayload(**data)
        assert payload.template == "onepager"
        assert payload.format == "png"
        assert payload.data == {"title": "Test"}
        assert payload.width == 1200
        assert payload.height == 1600
        assert payload.scale == 2
    
    def test_default_values(self):
        """Test default values are set correctly"""
        data = {"template": "onepager"}
        payload = RenderPayload(**data)
        assert payload.format == "png"
        assert payload.data == {}
        assert payload.width == 1200
        assert payload.height == 1600
        assert payload.scale == 2
    
    def test_missing_template(self):
        """Test missing required template field"""
        data = {"format": "png"}
        with pytest.raises(ValueError):
            RenderPayload(**data)


class TestValidateRenderPayload:
    """Test payload validation function"""
    
    def test_valid_payload(self):
        """Test valid payload passes validation"""
        data = {
            "template": "onepager",
            "format": "png",
            "scale": 2
        }
        payload = validate_render_payload(data)
        assert isinstance(payload, RenderPayload)
        assert payload.template == "onepager"
    
    def test_invalid_format(self):
        """Test invalid format raises error"""
        data = {
            "template": "onepager",
            "format": "invalid",
            "scale": 2
        }
        with pytest.raises(Exception):
            validate_render_payload(data)
    
    def test_invalid_scale_too_low(self):
        """Test scale below 1 raises error"""
        data = {
            "template": "onepager",
            "format": "png",
            "scale": 0
        }
        with pytest.raises(Exception):
            validate_render_payload(data)
    
    def test_invalid_scale_too_high(self):
        """Test scale above 3 raises error"""
        data = {
            "template": "onepager",
            "format": "png",
            "scale": 4
        }
        with pytest.raises(Exception):
            validate_render_payload(data)
    
    def test_valid_scale_boundaries(self):
        """Test scale boundaries 1 and 3 are valid"""
        for scale in [1, 2, 3]:
            data = {
                "template": "onepager",
                "format": "png",
                "scale": scale
            }
            payload = validate_render_payload(data)
            assert payload.scale == scale


class TestGetMimetypeAndFilename:
    """Test mimetype and filename generation"""
    
    def test_png_format(self):
        """Test PNG format returns correct mimetype and filename"""
        payload = RenderPayload(template="onepager", format="png")
        mimetype, filename = get_mimetype_and_filename(payload)
        assert mimetype == "image/png"
        assert filename == "onepager.png"
    
    def test_pdf_format(self):
        """Test PDF format returns correct mimetype and filename"""
        payload = RenderPayload(template="onepager", format="pdf")
        mimetype, filename = get_mimetype_and_filename(payload)
        assert mimetype == "application/pdf"
        assert filename == "onepager.pdf"
    
    def test_invalid_format(self):
        """Test invalid format raises error"""
        payload = RenderPayload(template="onepager", format="invalid")
        with pytest.raises(ValueError):
            get_mimetype_and_filename(payload)


class TestRenderToBytes:
    """Test render_to_bytes function"""
    
    @patch('app.renderer._render_png')
    def test_render_png(self, mock_render_png):
        """Test PNG rendering calls correct function"""
        mock_render_png.return_value = b"png_data"
        payload = RenderPayload(template="onepager", format="png", scale=2)
        html = "<html>test</html>"
        
        result = render_to_bytes(payload, html)
        
        assert result == b"png_data"
        mock_render_png.assert_called_once_with(html, 1200, 1600, 2)
    
    @patch('app.renderer._render_pdf')
    def test_render_pdf(self, mock_render_pdf):
        """Test PDF rendering calls correct function"""
        mock_render_pdf.return_value = b"pdf_data"
        payload = RenderPayload(template="onepager", format="pdf")
        html = "<html>test</html>"
        
        result = render_to_bytes(payload, html)
        
        assert result == b"pdf_data"
        mock_render_pdf.assert_called_once_with(html, 1200, 1600)
    
    def test_unsupported_format(self):
        """Test unsupported format raises error"""
        payload = RenderPayload(template="onepager", format="invalid")
        html = "<html>test</html>"
        
        with pytest.raises(ValueError, match="Unsupported format"):
            render_to_bytes(payload, html)


class TestRenderPNG:
    """Test PNG rendering function"""
    
    @patch('app.renderer.sync_playwright')
    def test_render_png_success(self, mock_playwright):
        """Test successful PNG rendering"""
        # Mock Playwright context
        mock_context = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.__enter__.return_value = mock_context
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.screenshot.return_value = b"png_data"
        
        html = "<html>test</html>"
        result = _render_png(html, 1200, 1600, 2)
        
        assert result == b"png_data"
        mock_page.set_content.assert_called_once_with(html, wait_until="networkidle")
        mock_browser.close.assert_called_once()
    
    @patch('app.renderer.sync_playwright')
    def test_render_png_browser_cleanup(self, mock_playwright):
        """Test browser cleanup even if screenshot fails"""
        mock_context = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.__enter__.return_value = mock_context
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.screenshot.side_effect = Exception("Screenshot failed")
        
        with pytest.raises(Exception):
            _render_png("<html>test</html>", 1200, 1600, 2)
        
        # Ensure browser is closed even on error
        mock_browser.close.assert_called_once()


class TestRenderPDF:
    """Test PDF rendering function"""
    
    @patch('app.renderer.sync_playwright')
    def test_render_pdf_success(self, mock_playwright):
        """Test successful PDF rendering"""
        # Mock Playwright context
        mock_context = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.__enter__.return_value = mock_context
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.pdf.return_value = b"pdf_data"
        
        html = "<html>test</html>"
        result = _render_pdf(html, 1200, 1600)
        
        assert result == b"pdf_data"
        mock_page.set_content.assert_called_once_with(html, wait_until="networkidle")
        mock_page.pdf.assert_called_once_with(width="12.5in", height="16.666666666666668in", print_background=True)
        mock_browser.close.assert_called_once()
    
    @patch('app.renderer.sync_playwright')
    def test_render_pdf_custom_dpi(self, mock_playwright):
        """Test PDF rendering with custom DPI"""
        mock_context = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.__enter__.return_value = mock_context
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.pdf.return_value = b"pdf_data"
        
        html = "<html>test</html>"
        result = _render_pdf(html, 1200, 1600, dpi=72)
        
        assert result == b"pdf_data"
        mock_page.pdf.assert_called_once_with(width="16.666666666666668in", height="22.22222222222222in", print_background=True)
    
    @patch('app.renderer.sync_playwright')
    def test_render_pdf_browser_cleanup(self, mock_playwright):
        """Test browser cleanup even if PDF generation fails"""
        mock_context = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.__enter__.return_value = mock_context
        mock_context.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.pdf.side_effect = Exception("PDF generation failed")
        
        with pytest.raises(Exception):
            _render_pdf("<html>test</html>", 1200, 1600)
        
        # Ensure browser is closed even on error
        mock_browser.close.assert_called_once()


class TestIntegration:
    """Test integration scenarios"""
    
    def test_full_render_workflow(self):
        """Test complete render workflow with valid data"""
        # Test data
        data = {
            "template": "onepager",
            "format": "png",
            "data": {"title": "Test Title"},
            "width": 1200,
            "height": 1600,
            "scale": 2
        }
        
        # Validate payload
        payload = validate_render_payload(data)
        assert payload.template == "onepager"
        assert payload.format == "png"
        
        # Get mimetype and filename
        mimetype, filename = get_mimetype_and_filename(payload)
        assert mimetype == "image/png"
        assert filename == "onepager.png"
        
        # Test that payload can be used for rendering
        assert payload.width == 1200
        assert payload.height == 1600
        assert payload.scale == 2
