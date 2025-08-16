from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
import os
from typing import Dict, Any, Optional, List

def get_env():
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    return Environment(
        loader=FileSystemLoader(tpl_dir),
        autoescape=select_autoescape(["html","xml"])
    )

class TemplatesLoader:
    """Loads and manages Jinja2 templates for content generation"""
    
    def __init__(self):
        # Set up Jinja2 environment with standard settings
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Available templates - updated to support new channels
        self.templates = {
            'onepager': 'onepager.html.j2',
            'newsletter': 'newsletter.html.j2',
            'blogpost': 'blogpost.html.j2',
            'story': 'story/story-highlights.html.j2',  # Default story template
            'linkedin': 'linkedin/li-product-announcement.html.j2'  # Default LinkedIn template
        }
    
    def get_template(self, template_name: str) -> Optional[Template]:
        """Get a specific template by name"""
        if template_name not in self.templates:
            return None
        
        try:
            return self.env.get_template(self.templates[template_name])
        except Exception as e:
            print(f"Error loading template {template_name}: {e}")
            return None
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        template = self.get_template(template_name)
        if not template:
            return ""
        
        try:
            return template.render(**context)
        except Exception as e:
            print(f"Error rendering template {template_name}: {e}")
            return ""
    
    def list_templates(self) -> List[str]:
        """List available template names"""
        return list(self.templates.keys())
    
    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists"""
        return template_name in self.templates
    
    def get_template_path(self, template_name: str) -> Optional[str]:
        """Get the file path for a template"""
        if template_name not in self.templates:
            return None
        
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        return os.path.join(template_dir, self.templates[template_name]) 