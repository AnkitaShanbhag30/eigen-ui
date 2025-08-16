import os
from PIL import Image
from colorthief import ColorThief
import requests
from typing import List, Tuple, Optional
import re

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex string"""
    return f"#{r:02x}{g:02x}{b:02x}"

def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors"""
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

def extract_palette(image_path: str, color_count: int = 8) -> List[str]:
    """Extract color palette from image using ColorThief"""
    try:
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=color_count, quality=1)
        return [rgb_to_hex(r, g, b) for r, g, b in palette]
    except Exception as e:
        print(f"Error extracting palette from {image_path}: {e}")
        return []

def get_dominant_colors(image_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Get primary and secondary colors from image"""
    try:
        color_thief = ColorThief(image_path)
        primary = color_thief.get_color(quality=1)
        primary_hex = rgb_to_hex(*primary)
        
        # Get secondary color (most contrasting)
        palette = color_thief.get_palette(color_count=8, quality=1)
        secondary = None
        max_distance = 0
        
        for color in palette:
            distance = color_distance(primary, color)
            if distance > max_distance and distance > 100:  # Threshold for contrast
                max_distance = distance
                secondary = color
        
        secondary_hex = rgb_to_hex(*secondary) if secondary else None
        
        return primary_hex, secondary_hex
    except Exception as e:
        print(f"Error getting dominant colors from {image_path}: {e}")
        return None, None

def download_and_extract_palette(image_url: str, save_path: str) -> Tuple[List[str], Optional[str], Optional[str]]:
    """Download image and extract its palette"""
    # Download image
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        # Extract palette
        palette = extract_palette(save_path)
        primary, secondary = get_dominant_colors(save_path)
        
        return palette, primary, secondary
        
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return [], None, None

def get_default_palette() -> Tuple[List[str], str, str]:
    """Return default palette when extraction fails"""
    default_palette = ["#222222", "#777777", "#EAEAEA"]
    return default_palette, "#222222", "#777777" 