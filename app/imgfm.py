import os
import requests
import json
import base64
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
from datetime import datetime
from .brand import get_asset_dir, ensure_asset_dirs
from PIL import Image
from io import BytesIO

class ImageProvider(ABC):
    """Abstract base class for image generation providers"""
    
    @abstractmethod
    def generate_image(self, prompt: str, brand_keywords: list, palette_hints: str) -> Optional[str]:
        """Generate image and return local file path"""
        pass

class OpenAIImageProvider(ImageProvider):
    """OpenAI DALL-E image generation provider"""
    
    def __init__(self):
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_image(self, prompt: str, brand_keywords: list, palette_hints: str) -> Optional[str]:
        """Generate image using OpenAI DALL-E"""
        try:
            # Build enhanced prompt
            enhanced_prompt = f"{prompt} Style: {', '.join(brand_keywords)}. {palette_hints}. Minimal, abstract, professional, suitable for business use."
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1792x1024",
                quality="standard",
                n=1
            )
            
            # Download the image
            image_url = response.data[0].url
            return self._download_image(image_url)
            
        except Exception as e:
            print(f"OpenAI image generation error: {e}")
            return None
    
    def _download_image(self, image_url: str) -> Optional[str]:
        """Download image from URL to local storage"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary location (will be moved to brand assets)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            temp_path = f"temp_hero_{timestamp}.png"
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

class StabilityProvider(ImageProvider):
    """Stability AI image generation provider"""
    
    def __init__(self):
        api_key = os.getenv('STABILITY_API_KEY')
        if not api_key:
            raise ValueError("STABILITY_API_KEY environment variable not set")
        
        self.api_key = api_key
        self.api_host = 'https://api.stability.ai'
    
    def generate_image(self, prompt: str, brand_keywords: list, palette_hints: str) -> Optional[str]:
        """Generate image using Stability AI"""
        try:
            # Build enhanced prompt
            enhanced_prompt = f"{prompt} Style: {', '.join(brand_keywords)}. {palette_hints}. Minimal, abstract, professional."
            
            response = requests.post(
                f"{self.api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "text_prompts": [
                        {
                            "text": enhanced_prompt,
                            "weight": 1
                        }
                    ],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1792,
                    "samples": 1,
                    "steps": 30,
                }
            )
            
            if response.status_code != 200:
                print(f"Stability API error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            temp_path = f"temp_hero_{timestamp}.png"
            
            import base64
            image_data = base64.b64decode(data["artifacts"][0]["base64"])
            
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            return temp_path
            
        except Exception as e:
            print(f"Stability image generation error: {e}")
            return None

class FalProvider(ImageProvider):
    """Fal.ai image generation provider"""
    
    def __init__(self):
        api_key = os.getenv('FAL_API_KEY')
        if not api_key:
            raise ValueError("FAL_API_KEY environment variable not set")
        
        self.api_key = api_key
    
    def generate_image(self, prompt: str, brand_keywords: list, palette_hints: Union[List[str], str]) -> Optional[str]:
        """Generate image using Fal.ai Imagen 4 Ultra (preview)."""
        try:
            # Normalize palette hints
            if isinstance(palette_hints, list):
                palette_str = ", ".join([str(p) for p in palette_hints if p])
            else:
                palette_str = str(palette_hints or "")

            # Construct prompt: thematic but slightly specific, discourage text/logos
            style_tags = ", ".join([kw for kw in brand_keywords[:3]]) if brand_keywords else "modern, clean"
            constraints = (
                "No text, captions, signage, watermarks, or logos. "
                "No UI mockups or screenshots. "
                "Crisp, high-quality, professional."
            )
            color_hint = f" Color accents: {palette_str}." if palette_str else ""
            enhanced_prompt = f"{prompt}. Style: {style_tags}.{color_hint} {constraints}"

            response = requests.post(
                "https://fal.run/fal-ai/imagen4/preview/ultra",
                headers={
                    "Authorization": f"Key {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": enhanced_prompt,
                    "aspect_ratio": "16:9",
                    "num_images": 1,
                    "negative_prompt": "text, caption, letters, words, logo, watermark, low quality"
                },
                timeout=60
            )

            if response.status_code != 200:
                print(f"Fal.ai API error: {response.status_code} - {response.text[:200]}")
                return None

            data = response.json()
            images = data.get("images") or []
            if not images or not images[0].get("url"):
                print("No images in Fal.ai response")
                return None

            return self._download_image(images[0]["url"])

        except Exception as e:
            print(f"Fal.ai image generation error: {e}")
            return None
    
    def _download_image(self, image_url: str) -> Optional[str]:
        """Download image from URL to local storage"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            temp_path = f"temp_hero_{timestamp}.png"
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

def get_image_provider() -> Optional[ImageProvider]:
    """Get the configured image generation provider"""
    provider = os.getenv('IMAGE_PROVIDER')
    if provider:
        provider = provider.lower()
        if provider == 'openai':
            return OpenAIImageProvider()
        if provider == 'stability':
            return StabilityProvider()
        if provider == 'fal':
            return FalProvider()
        print(f"Unknown image provider '{provider}', defaulting based on available keys")
    # Auto-select based on available API keys
    if os.getenv('FAL_API_KEY'):
        return FalProvider()
    if os.getenv('OPENAI_API_KEY'):
        return OpenAIImageProvider()
    if os.getenv('STABILITY_API_KEY'):
        return StabilityProvider()
    return None

def save_hero_image(brand_slug: str, image_path: str) -> Optional[str]:
    """Save hero image to brand assets directory"""
    try:
        ensure_asset_dirs(brand_slug)
        asset_dir = get_asset_dir(brand_slug)
        hero_dir = os.path.join(asset_dir, "hero")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        hero_filename = f"hero_{timestamp}.png"
        hero_path = os.path.join(hero_dir, hero_filename)
        
        # Move temporary file to hero directory
        import shutil
        shutil.move(image_path, hero_path)
        
        return hero_path
        
    except Exception as e:
        print(f"Error saving hero image: {e}")
        return None

def generate_hero_image(brand_slug: str, hero_brief: str, brand_keywords: list, palette_hints: str) -> Optional[str]:
    """Generate and save hero image for a brand"""
    provider = get_image_provider()
    
    if not provider:
        print("No image provider configured, skipping hero generation")
        return None
    
    if not hero_brief:
        print("No hero brief provided, skipping hero generation")
        return None
    
    try:
        print(f"Generating hero image for {brand_slug}...")
        
        # Generate image
        temp_path = provider.generate_image(hero_brief, brand_keywords, palette_hints)
        
        if not temp_path:
            print("Failed to generate hero image")
            return None
        
        # Save to brand assets
        hero_path = save_hero_image(brand_slug, temp_path)
        
        if hero_path:
            print(f"Hero image saved to: {hero_path}")
            return hero_path
        else:
            print("Failed to save hero image")
            return None
            
    except Exception as e:
        print(f"Error in hero image generation: {e}")
        return None

from typing import Optional

def generate_hero_image_remote_url(prompt: str, brand_keywords: list, palette_hints: Union[List[str], str]) -> Optional[str]:
    """Generate a hero image via Fal Imagen 4 Ultra and return the hosted URL (no download)."""
    try:
        api_key = os.getenv('FAL_API_KEY')
        if not api_key:
            return None
        if isinstance(palette_hints, list):
            palette_str = ", ".join([str(p) for p in palette_hints if p])
        else:
            palette_str = str(palette_hints or "")
        style_tags = ", ".join([kw for kw in brand_keywords[:3]]) if brand_keywords else "modern, clean"
        constraints = (
            "No text, words, captions, subtitles, signage, labels, logos, watermarks, typography, letters. "
            "Crisp, high-quality, professional."
        )
        color_hint = f" Color accents: {palette_str}." if palette_str else ""
        enhanced_prompt = f"{prompt}. Style: {style_tags}.{color_hint} {constraints}"
        response = requests.post(
            "https://fal.run/fal-ai/imagen4/preview/ultra",
            headers={
                "Authorization": f"Key {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": enhanced_prompt,
                "aspect_ratio": "16:9",
                "num_images": 1,
                "negative_prompt": "text, words, captions, subtitles, signage, labels, logos, watermarks, typography, letters, low quality"
            },
            timeout=60
        )
        if response.status_code != 200:
            return None
        data = response.json()
        images = data.get("images") or []
        if not images or not images[0].get("url"):
            return None
        return images[0]["url"]
    except Exception:
        return None

def gen_hero_image(prompt: str, out_path: str) -> Optional[str]:
    """Generate a single hero image to local path using preferred provider.

    Preference order:
      1) Fal (Imagen 4 Ultra) if FAL_API_KEY is set or IMAGE_PROVIDER=fal
      2) OpenAI DALL-E-3 if OPENAI_API_KEY is set or IMAGE_PROVIDER=openai
    """
    try:
        image_provider_env = (os.getenv("IMAGE_PROVIDER") or "").lower()
        if image_provider_env == "fal" or os.getenv("FAL_API_KEY"):
            # Use Fal Imagen 4 Ultra
            api_key = os.getenv('FAL_API_KEY')
            if not api_key:
                return None
            constraints = (
                "No text, captions, signage, watermarks, or logos. "
                "Crisp, high-quality, professional."
            )
            enhanced_prompt = f"{prompt}. {constraints}"
            resp = requests.post(
                "https://fal.run/fal-ai/imagen4/preview/ultra",
                headers={
                    "Authorization": f"Key {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": enhanced_prompt,
                    "aspect_ratio": "16:9",
                    "num_images": 1,
                    "negative_prompt": "text, caption, letters, words, logo, watermark, low quality"
                },
                timeout=60
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            images = data.get("images") or []
            if not images or not images[0].get("url"):
                return None
            url = images[0]["url"]
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with open(out_path, 'wb') as f:
                f.write(r.content)
            return out_path

        # Fallback to OpenAI
        if image_provider_env == "openai" or os.getenv("OPENAI_API_KEY"):
            import openai
            client = openai.OpenAI()
            res = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1600x900"
            )
            b64 = res.data[0].b64_json
            img = Image.open(BytesIO(base64.b64decode(b64)))
            img.save(out_path, format="PNG")
            return out_path
        return None
    except Exception:
        return None
