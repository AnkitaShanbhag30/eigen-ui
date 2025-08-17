from pathlib import Path
import os

def resolve_templates(force_html=False):
    """
    Resolve which template engine to use.
    
    Args:
        force_html (bool): If True, force HTML engine regardless of Dyad availability
        
    Returns:
        dict: Template engine configuration
    """
    if force_html:
        return {"engine": "html", "entry": None}
    
    # Previously, we used Dyad React SSR when TSX templates were present.
    # We now always use the HTML engine and delegate generation to the V0 wrapper.
    # Keeping the structure in case future engines are reintroduced.
    
    # Fallback to HTML engine
    return {"engine": "html", "entry": None}
