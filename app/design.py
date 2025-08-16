import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

from .llm import get_llm_provider
from .brand import BrandIdentity, Colors, Typography, DesignAdvisor
from .html_tokens import default_tokens

DESIGN_SYS_PROMPT = """You are a senior brand designer. Given palette + detected fonts + brand adjectives,
propose:
- typography.heading and .body (Google Fonts or common system faces)
- colors.primary/secondary/accent/muted (must come from provided palette or sensible neutrals)
- spacing scale (integers in px): 4,6,8 keys only
- radius.md (px)
- heroBrief: a short image prompt (style+mood) consistent with tone/keywords
Return ONLY JSON with:
{ "typography": { "heading":"...", "body":"..." },
  "colors": { "primary":"#....","secondary":"#....","accent":"#....","muted":"#...." },
  "spacing": { "4": 16, "6": 24, "8": 32 },
  "radius": { "md": 16 },
  "heroBrief": "..." }"""

def propose_design(identity: dict) -> dict:
    palette = identity.get("colors", {}).get("palette", [])
    fonts = identity.get("fonts_detected", []) or identity.get("fonts", [])
    tone = identity.get("tone", "")
    keywords = ", ".join(identity.get("keywords", [])[:12])
    user = f"""palette: {palette}
detected_fonts: {fonts}
tone: {tone}
keywords: {keywords}"""
    out = generate_json(DESIGN_SYS_PROMPT, user)
    # merge into identity.typography/colors and build tokens
    identity.setdefault("typography", {})
    identity["typography"]["heading"] = out.get("typography", {}).get("heading") or identity["typography"].get("heading") or "Inter"
    identity["typography"]["body"] = out.get("typography", {}).get("body") or identity["typography"].get("body") or "Inter"
    identity["colors"]["primary"] = out.get("colors", {}).get("primary") or identity["colors"].get("primary")
    identity["colors"]["secondary"] = out.get("colors", {}).get("secondary") or identity["colors"].get("secondary")
    identity["colors"]["accent"] = out.get("colors", {}).get("accent") or identity["colors"].get("secondary")
    identity["colors"]["muted"] = out.get("colors", {}).get("muted") or "#EBEEF3"
    identity["heroBrief"] = out.get("heroBrief", "")
    tokens = default_tokens(identity["colors"], identity["typography"]["heading"], identity["typography"]["body"])
    # allow spacing/radius overrides
    if "spacing" in out: tokens["spacing"].update({k:str(int(v)) for k,v in out["spacing"].items()})
    if "radius" in out and "md" in out["radius"]: tokens["radius"]["md"] = int(out["radius"]["md"])
    return {"identity": identity, "tokens": tokens}

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
        """Generate content outline using LLM with UI/layout data integration"""
        word_count_bands = {
            'onepager': '400-700',
            'newsletter': '450-900',
            'blogpost': '800-1200'
        }
        
        word_count = word_count_bands.get(template, '400-700')
        
        # Extract UI/layout insights for content structure
        ui_insights = self._extract_ui_insights_for_content(brand)
        
        system_prompt = """You are a precise marketing writer who creates content that matches the brand's visual design patterns and layout structure. Obey the BrandIdentity voice strictly. Avoid clichés and filler. Keep claims factual. Write for the specified audience Z. Use the UI/layout insights to create content that feels authentic to the brand's design language. Output ONLY valid JSON that matches the required schema."""
        
        user_prompt = f"""Brand Identity: {json.dumps(brand.dict(), indent=2)}

UI/Layout Insights: {json.dumps(ui_insights, indent=2)}

Template: {template}
X (What we're building): {x}
Y (Why it matters): {y}
Z (Target audience): {z}
W (Additional context): {w}

Word count target: {word_count} words

Use the UI/layout insights to:
1. Structure content sections based on detected design patterns
2. Match the brand's visual hierarchy and spacing preferences
3. Incorporate component patterns (cards, grids, buttons) naturally
4. Follow the brand's content organization style

Return ONLY the JSON object with fields {{headline, subhead?, sections[{{title,bullets[],content_type?,layout_style?}}], cta, meta{{seoTitle,seoDesc,tags[]}}}}. No prose."""
        
        try:
            response = self.llm.generate_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Content outline generation failed: {e}")
            return self._get_default_outline_with_ui(template, x, y, z, w, ui_insights)
    
    def _extract_ui_insights_for_content(self, brand: BrandIdentity) -> Dict[str, Any]:
        """Extract UI/layout insights that should influence content generation"""
        ui_layout = brand.ui_layout
        
        insights = {
            'design_patterns': [],
            'content_structure': {},
            'visual_hierarchy': {},
            'component_preferences': {},
            'layout_style': 'default'
        }
        
        # Extract design patterns
        if ui_layout.design_patterns:
            for pattern in ui_layout.design_patterns:
                insights['design_patterns'].append({
                    'type': pattern.type,
                    'layout_type': pattern.layout_type,
                    'alignment': pattern.alignment
                })
        
        # Extract content structure preferences
        if ui_layout.page_structure:
            structure = ui_layout.page_structure
            insights['content_structure'] = {
                'has_hero': bool(structure.hero),
                'has_sidebar': bool(structure.sidebar),
                'section_count': len(structure.sections),
                'section_types': [s.get('content_type', 'general') for s in structure.sections[:5]]
            }
        
        # Extract visual hierarchy preferences
        if ui_layout.visual_hierarchy:
            hierarchy = ui_layout.visual_hierarchy
            insights['visual_hierarchy'] = {
                'heading_levels': list(hierarchy.headings.keys()),
                'text_sizes': hierarchy.text_sizes[:5],
                'emphasis_styles': hierarchy.emphasis
            }
        
        # Extract component preferences
        if ui_layout.component_patterns:
            components = ui_layout.component_patterns
            insights['component_preferences'] = {
                'button_styles': [btn.get('variant', 'default') for btn in components.buttons[:3]],
                'card_layouts': [card.get('layout', 'default') for card in components.cards[:3]],
                'form_style': components.forms[0].get('layout', 'default') if components.forms else 'default'
            }
        
        # Determine overall layout style
        if ui_layout.layout_grid.grid_systems:
            insights['layout_style'] = 'grid-based'
        elif any(p.layout_type == 'flexbox' for p in ui_layout.design_patterns):
            insights['layout_style'] = 'flexbox-based'
        elif ui_layout.spacing_system.common_values:
            insights['layout_style'] = 'spacing-system'
        
        return insights
    
    def _get_default_outline_with_ui(self, template: str, x: str, y: str, z: str, w: str, ui_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Return default outline that incorporates UI/layout insights"""
        # Use UI insights to structure the default outline
        layout_style = ui_insights.get('layout_style', 'default')
        section_count = ui_insights.get('content_structure', {}).get('section_count', 3)
        
        # Adjust section count based on detected patterns
        if layout_style == 'grid-based':
            section_count = min(section_count, 4)  # Grid layouts work well with 2x2 or 3x1
        elif layout_style == 'spacing-system':
            section_count = min(section_count, 5)  # Spacing systems can handle more sections
        
        sections = []
        for i in range(section_count):
            if i == 0:
                sections.append({
                    "title": "The Challenge",
                    "bullets": [f"Current solutions don't address {x} effectively", f"Organizations struggle with {y}"],
                    "content_type": "problem",
                    "layout_style": "text"
                })
            elif i == 1:
                sections.append({
                    "title": "Our Solution",
                    "bullets": [f"Innovative approach to {x}", f"Designed specifically for {z}"],
                    "content_type": "solution",
                    "layout_style": "card"
                })
            elif i == 2:
                sections.append({
                    "title": "Key Benefits",
                    "bullets": ["Improved efficiency", "Better user experience", "Cost-effective solution"],
                    "content_type": "benefits",
                    "layout_style": "grid"
                })
            elif i == 3:
                sections.append({
                    "title": "Why Choose Us",
                    "bullets": ["Proven track record", "Expert team", "Ongoing support"],
                    "content_type": "differentiation",
                    "layout_style": "list"
                })
            elif i == 4:
                sections.append({
                    "title": "Next Steps",
                    "bullets": ["Schedule a consultation", "See a demo", "Get started today"],
                    "content_type": "cta",
                    "layout_style": "button"
                })
        
        return {
            "headline": f"Building {x}",
            "subhead": f"To {y}",
            "sections": sections,
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
