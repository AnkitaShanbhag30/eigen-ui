import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

from .llm import get_llm_provider
from .brand import BrandIdentity, Colors, Typography, DesignAdvisor

class DesignAdvisorService:
    """Service for design advice using LLM analysis"""
    
    def __init__(self):
        self.llm = get_llm_provider()
    
    def analyze_voice(self, text_samples: List[str], website_url: str) -> Dict[str, Any]:
        """Analyze brand voice from text samples"""
        if not text_samples:
            return {"tone": "professional and engaging", "keywords": ["innovation", "quality", "service"]}
        
        system_prompt = """You are a concise brand voice analyst. Given site copy samples, return JSON:
{ "tone": "<5-10 words summary>", "keywords": ["...10-20 items..."] }
Return ONLY JSON."""
        
        user_prompt = f"Analyze these text samples from {website_url}:\n\n" + "\n\n".join(text_samples[:3])
        
        try:
            response = self.llm.generate_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Voice analysis failed: {e}")
            return {"tone": "professional and engaging", "keywords": ["innovation", "quality", "service"]}
    
    def get_design_advice(self, brand: BrandIdentity) -> Dict[str, Any]:
        """Get comprehensive design advice for a brand"""
        colors = brand.colors
        fonts_detected = brand.fonts_detected
        tone = brand.tone
        keywords = brand.keywords
        
        # Build context for design advisor
        context = f"""
Brand Context:
- Name: {brand.name}
- Tone: {tone}
- Keywords: {', '.join(keywords[:10])}
- Detected fonts: {', '.join(fonts_detected) if fonts_detected else 'None detected'}
- Primary color: {colors.primary or 'Not set'}
- Secondary color: {colors.secondary or 'Not set'}
- Palette: {', '.join(colors.palette[:5]) if colors.palette else 'Not set'}
"""
        
        system_prompt = """You are a senior brand designer and web typographer. Given the brand context (palette, detected fonts, logo hints, tone, keywords), propose typography pairing (Google Fonts family names), layout variant A|B|C, spacing/radius scales, and color role assignments prioritizing contrast ≥ 4.5:1 for body text. Also provide a brief for a hero/cover image prompt. Return ONLY JSON with:
{ "typography": { "heading": "...", "body": "..." },
  "layout": "A|B|C",
  "spacing": {"base": 16, "scale": [1,1.25,1.6,2] },
  "radius": {"sm":8,"md":14,"lg":22},
  "colors": {"primary":"...","secondary":"...","accent":"...","muted":"..."},
  "heroBrief": "..." }"""
        
        user_prompt = f"{context}\n\nProvide design advice for this brand."
        
        try:
            response = self.llm.generate_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Design advice failed: {e}")
            return self._get_default_design_advice()
    
    def _get_default_design_advice(self) -> Dict[str, Any]:
        """Return default design advice when LLM fails"""
        return {
            "typography": {
                "heading": "Inter",
                "body": "Inter"
            },
            "layout": "A",
            "spacing": {
                "base": 16,
                "scale": [1, 1.25, 1.6, 2]
            },
            "radius": {
                "sm": 8,
                "md": 14,
                "lg": 22
            },
            "colors": {
                "primary": "#2563EB",
                "secondary": "#F59E0B",
                "accent": "#10B981",
                "muted": "#6B7280"
            },
            "heroBrief": "Minimal abstract background with subtle geometric shapes, professional business aesthetic"
        }
    
    def generate_content_outline(self, brand: BrandIdentity, template: str, x: str, y: str, z: str, w: str) -> Dict[str, Any]:
        """Generate content outline using LLM"""
        word_count_bands = {
            'onepager': '400-700',
            'newsletter': '450-900',
            'blogpost': '800-1200'
        }
        
        word_count = word_count_bands.get(template, '400-700')
        
        system_prompt = """You are a precise marketing writer. Obey the BrandIdentity voice strictly. Avoid clichés and filler. Keep claims factual. Write for the specified audience Z. Output ONLY valid JSON that matches the required schema."""
        
        user_prompt = f"""Brand Identity: {json.dumps(brand.dict(), indent=2)}

Template: {template}
X (What we're building): {x}
Y (Why it matters): {y}
Z (Target audience): {z}
W (Additional context): {w}

Word count target: {word_count} words

Return ONLY the JSON object with fields {{headline, subhead?, sections[{{title,bullets[]}}], cta, meta{{seoTitle,seoDesc,tags[]}}}}. No prose."""
        
        try:
            response = self.llm.generate_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Content outline generation failed: {e}")
            return self._get_default_outline(template, x, y, z, w)
    
    def _get_default_outline(self, template: str, x: str, y: str, z: str, w: str) -> Dict[str, Any]:
        """Return default outline when LLM fails"""
        return {
            "headline": f"Building {x}",
            "subhead": f"To {y}",
            "sections": [
                {
                    "title": "The Challenge",
                    "bullets": [f"Current solutions don't address {x} effectively", f"Organizations struggle with {y}"]
                },
                {
                    "title": "Our Solution",
                    "bullets": [f"Innovative approach to {x}", f"Designed specifically for {z}"]
                },
                {
                    "title": "Key Benefits",
                    "bullets": ["Improved efficiency", "Better user experience", "Cost-effective solution"]
                }
            ],
            "cta": "Get Started Today",
            "meta": {
                "seoTitle": f"Building {x} - {y}",
                "seoDesc": f"Discover how we're building {x} to {y} for {z}",
                "tags": [x, y, z, "innovation", "solution"]
            }
        }
    
    def polish_content(self, outline: Dict[str, Any], brand: BrandIdentity) -> Dict[str, Any]:
        """Polish and refine content using LLM"""
        system_prompt = """You are a marketing editor. Improve flow, clarity, and specificity. Keep factual, concise. Return ONLY the polished outline JSON with identical shape."""
        
        user_prompt = f"""Brand tone: {brand.tone}
Keywords: {', '.join(brand.keywords[:10])}

Polish this content outline:
{json.dumps(outline, indent=2)}"""
        
        try:
            response = self.llm.generate_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Content polish failed: {e}")
            return outline
    
    def visual_qa_analysis(self, html_content: str, tokens: Dict[str, Any], brand: BrandIdentity) -> Optional[Dict[str, Any]]:
        """Analyze visual design using multimodal LLM (if available)"""
        # This would require a multimodal LLM that can analyze images
        # For now, we'll return None to indicate QA is not available
        # In a full implementation, this would:
        # 1. Render HTML to PNG
        # 2. Send PNG to multimodal LLM
        # 3. Get feedback and token tweaks
        # 4. Return suggestions
        
        print("Visual QA analysis not implemented in this version")
        return None
    
    def apply_design_advice(self, brand: BrandIdentity, design_advice: Dict[str, Any]) -> BrandIdentity:
        """Apply design advice to brand identity"""
        # Update typography
        if "typography" in design_advice:
            brand.typography.heading = design_advice["typography"].get("heading")
            brand.typography.body = design_advice["typography"].get("body")
        
        # Update design advisor
        if "layout" in design_advice:
            brand.design_advisor.layout_variant = design_advice["layout"]
        
        if "spacing" in design_advice:
            brand.design_advisor.spacing_scale = design_advice["spacing"].get("scale", [1, 1.25, 1.6, 2])
        
        if "radius" in design_advice:
            brand.design_advisor.radius = design_advice["radius"]
        
        if "heroBrief" in design_advice:
            brand.design_advisor.hero_brief = design_advice["heroBrief"]
        
        # Update colors if provided
        if "colors" in design_advice:
            colors = design_advice["colors"]
            if colors.get("primary"):
                brand.colors.primary = colors["primary"]
            if colors.get("secondary"):
                brand.colors.secondary = colors["secondary"]
            if colors.get("accent"):
                brand.colors.accent = colors["accent"]
            if colors.get("muted"):
                brand.colors.muted = colors["muted"]
        
        return brand
