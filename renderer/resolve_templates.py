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
    
    dyad_active = Path("data/templates/_active")
    
    # Check for Dyad templates
    if dyad_active.exists() and any(dyad_active.glob("**/*.tsx")):
        # Look for the main entry point
        entry_points = list(dyad_active.glob("**/*.tsx"))
        
        # Prefer index.tsx, then any .tsx file
        preferred_entry = None
        for entry in entry_points:
            if entry.name == "index.tsx":
                preferred_entry = entry
                break
        
        if not preferred_entry and entry_points:
            preferred_entry = entry_points[0]
        
        if preferred_entry:
            return {
                "engine": "react", 
                "entry": str(preferred_entry),
                "available_templates": [str(ep) for ep in entry_points]
            }
    
    # Fallback to HTML engine
    return {"engine": "html", "entry": None}
