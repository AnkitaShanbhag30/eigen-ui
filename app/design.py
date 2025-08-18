import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

from .llm import get_llm_provider
from .brand import BrandIdentity, Colors, Typography, DesignAdvisor
from .html_tokens import default_tokens

DESIGN_SYS_PROMPT = """You are a senior brand designer.

Given palette + detected fonts + brand adjectives, propose a cohesive, accessible design system.

Follow these guardrails while deciding, but OUTPUT MUST STAY IN THE SAME JSON SHAPE BELOW:
- Visual hierarchy & typography: establish a 1.25 typographic scale; use sensible font weights (300, 400, 600, 700);
  line-height ~1.2 for headings, ~1.5 for body, ~1.4 for UI; letter-spacing: -0.02em for large type, 0 for body,
  up to +0.05em for small caps. Choose Google Fonts or common system families.
- Color & contrast: pick roles from the provided palette or sensible neutrals; ensure WCAG AA contrast ≥ 4.5:1 for body text.
- Spacing & layout: use a consistent 4px/8px-based rhythm; return spacing integers in px for keys 4,6,8 only.
- Radius: prefer modern, soft radii; return a single medium radius in px.
- Hero brief: short prompt matching tone/keywords; avoid any text-in-image requests.

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
        
        system_prompt = """You are a senior brand designer and web typographer.

Given the brand context (palette, detected fonts, logo hints, tone, keywords), propose:
- Typography pairing (Google Fonts family names) honoring a 1.25 scale, weights 300/400/600/700,
  line-heights ~1.2/1.5, sensible letter-spacing as needed.
- Layout variant A|B|C matching brand personality.
- Spacing/radius scales using a 4px/8px rhythm; include a reasonable typographic scale array.
- Color role assignments prioritizing WCAG AA contrast ≥ 4.5:1 for body text.
- A brief for a hero/cover image prompt (avoid any text-in-image).

Return ONLY JSON with:
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
    
    def generate_content_outline(self, template: str, x: str, y: str, z: str, w: str, cta: str, brand: BrandIdentity) -> Dict[str, Any]:
        """Generate content outline using brand insights and UI/layout data"""
        try:
            # Extract UI/layout insights for content generation
            ui_insights = self._extract_ui_insights_for_content(brand)
            
            # Create enhanced system prompt using brand data
            system_prompt = self._create_enhanced_system_prompt(brand, ui_insights)
            
            # Create enhanced user prompt with brand context
            user_prompt = self._create_enhanced_user_prompt(template, x, y, z, w, cta, brand, ui_insights)
            
            # Generate content using LLM
            response = self.llm.generate_json(system_prompt, user_prompt)
            
            if response and isinstance(response, dict):
                # Validate and enhance the response
                enhanced_outline = self._enhance_outline_with_brand_data(response, brand, ui_insights)
                return enhanced_outline
            else:
                # Fallback to UI-aware default outline
                return self._get_default_outline_with_ui(template, x, y, z, w, ui_insights)
                
        except Exception as e:
            print(f"Content generation failed: {e}")
            # Fallback to UI-aware default outline
            ui_insights = self._extract_ui_insights_for_content(brand)
            return self._get_default_outline_with_ui(template, x, y, z, w, ui_insights)
    
    def _create_enhanced_system_prompt(self, brand: BrandIdentity, ui_insights: Dict[str, Any]) -> str:
        """Create an enhanced system prompt that leverages brand data"""
        return f"""You are a senior brand strategist and content creator. Your task is to create content that perfectly matches the brand's visual identity, tone, and design patterns.

BRAND IDENTITY:
- Name: {brand.name}
- Website: {brand.website}
- Tone: {brand.tone}
- Keywords: {', '.join(brand.keywords[:15])}

VISUAL DESIGN PATTERNS:
- Primary Color: {brand.colors.primary or 'Not specified'}
- Secondary Color: {brand.colors.secondary or 'Not specified'}
- Accent Colors: {', '.join(brand.colors.palette[:5]) if brand.colors.palette else 'Not specified'}
- Detected Fonts: {', '.join(brand.fonts_detected[:5]) if brand.fonts_detected else 'Not specified'}

UI/LAYOUT INSIGHTS:
- Layout Style: {ui_insights.get('layout_style', 'standard')}
- Content Structure: {ui_insights.get('content_structure', {}).get('section_count', 3)} sections detected
- Visual Hierarchy: {', '.join(ui_insights.get('visual_hierarchy', {}).get('heading_levels', ['h1', 'h2', 'h3']))}
- Component Patterns: {', '.join(ui_insights.get('component_preferences', {}).get('button_styles', ['standard']))}

INSTRUCTIONS:
1. Use the brand's exact tone and keywords
2. Match the detected layout patterns and section count
3. Incorporate the brand's color psychology and visual hierarchy
4. Create content that feels native to the brand's website
5. Use the detected component patterns (cards, grids, lists) appropriately
6. Ensure content flows with the brand's visual rhythm and spacing

QUALITY GUARDRAILS:
- Keep language specific, benefit-driven, and scannable (short sentences, strong verbs).
- Assume a 1.25 type scale, 4/8px spacing rhythm, and WCAG AA contrast; do not output these values, only reflect them in clarity and hierarchy.
- Avoid placeholders, vague claims, or repeated bullets; each section should add unique value.

Return ONLY valid JSON matching this exact schema:
{{
  "headline": "Compelling headline (5-8 words) that matches brand tone",
  "subhead": "Supporting subtitle explaining the value proposition",
  "sections": [
    {{
      "title": "Section title",
      "bullets": ["Key point 1", "Key point 2", "Key point 3"],
      "content_type": "problem|solution|benefits|features|testimonials|cta" - or you can useother similar content types, these are examples,
      "layout_style": "text|card|grid|list|hero",
      "visual_emphasis": "high|medium|low"
    }}
  ],
  "cta": "Clear call to action that matches brand voice",
  "meta": {{
    "seoTitle": "SEO-optimized title",
    "seoDesc": "SEO description using brand keywords",
    "tags": ["relevant", "brand", "keywords"],
    "layout_variant": "A|B|C",
    "color_scheme": "primary|secondary|accent|muted"
  }}
}}"""
    
    def _create_enhanced_user_prompt(self, template: str, x: str, y: str, z: str, w: str, cta: str, brand: BrandIdentity, ui_insights: Dict[str, Any]) -> str:
        """Create an enhanced user prompt with comprehensive brand context"""
        return f"""Create content for a {template} that perfectly embodies the brand identity.

CONTENT REQUIREMENTS:
- What we're building: {x}
- Why it matters: {y}
- Target audience: {z}
- Additional context: {w}
- Call to action: {cta}

BRAND CONTEXT:
- Brand voice: {brand.tone}
- Target keywords: {', '.join(brand.keywords[:10])}
- Business focus: {brand.description or 'Not specified'}

DESIGN INTEGRATION:
- Use {ui_insights.get('content_structure', {}).get('section_count', 3)} sections to match the brand's content structure
- Apply {ui_insights.get('layout_style', 'standard')} layout principles
- Incorporate {', '.join(ui_insights.get('component_preferences', {}).get('button_styles', ['standard']))} button styles
- Use {', '.join(ui_insights.get('visual_hierarchy', {}).get('heading_levels', ['h1', 'h2', 'h3']))} heading hierarchy

The content should feel like it was written by the brand team and designed by the brand's designers. Every element should reflect the brand's visual identity and user experience patterns."""
    
    def _enhance_outline_with_brand_data(self, outline: Dict[str, Any], brand: BrandIdentity, ui_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the generated outline with additional brand-specific data"""
        enhanced = outline.copy()
        
        # Add brand-specific metadata
        enhanced['brand_context'] = {
            'name': brand.name,
            'website': brand.website,
            'tone': brand.tone,
            'primary_color': brand.colors.primary,
            'secondary_color': brand.colors.secondary,
            'accent_colors': brand.colors.palette[:5] if brand.colors.palette else []
        }
        
        # Enhance sections with brand-specific styling
        if 'sections' in enhanced:
            for section in enhanced['sections']:
                # Add content type if not present
                if 'content_type' not in section:
                    section['content_type'] = self._detect_content_type_from_title(section.get('title', ''))
                
                # Add layout style based on content type and brand patterns
                if 'layout_style' not in section:
                    section['layout_style'] = self._get_optimal_layout_style(section['content_type'], ui_insights)
                
                # Add visual emphasis based on brand hierarchy
                if 'visual_emphasis' not in section:
                    section['visual_emphasis'] = self._get_visual_emphasis(section['content_type'])
        
        # Add meta information
        if 'meta' not in enhanced:
            enhanced['meta'] = {}
        
        enhanced['meta'].update({
            'layout_variant': ui_insights.get('layout_style', 'A'),
            'color_scheme': self._get_color_scheme_from_brand(brand),
            'typography_pair': f"{brand.typography.heading or 'Inter'} + {brand.typography.body or 'Inter'}",
            'brand_keywords': brand.keywords[:8]
        })
        
        return enhanced
    
    def _detect_content_type_from_title(self, title: str) -> str:
        """Detect content type from section title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['challenge', 'problem', 'issue']):
            return 'problem'
        elif any(word in title_lower for word in ['solution', 'approach', 'method']):
            return 'solution'
        elif any(word in title_lower for word in ['benefit', 'advantage', 'feature']):
            return 'benefits'
        elif any(word in title_lower for word in ['testimonial', 'review', 'quote']):
            return 'testimonials'
        elif any(word in title_lower for word in ['contact', 'start', 'get']):
            return 'cta'
        else:
            return 'general'
    
    def _get_optimal_layout_style(self, content_type: str, ui_insights: Dict[str, Any]) -> str:
        """Get optimal layout style based on content type and brand patterns"""
        layout_mapping = {
            'problem': 'text',
            'solution': 'card',
            'benefits': 'grid',
            'features': 'grid',
            'testimonials': 'card',
            'cta': 'hero'
        }
        
        # Use brand's preferred layout if available
        brand_layout = ui_insights.get('layout_style', 'standard')
        
        if brand_layout == 'grid-based' and content_type in ['benefits', 'features']:
            return 'grid'
        elif brand_layout == 'card-based' and content_type in ['solution', 'testimonials']:
            return 'card'
        else:
            return layout_mapping.get(content_type, 'text')
    
    def _get_visual_emphasis(self, content_type: str) -> str:
        """Get visual emphasis level based on content type"""
        emphasis_mapping = {
            'problem': 'high',
            'solution': 'high',
            'benefits': 'medium',
            'features': 'medium',
            'testimonials': 'low',
            'cta': 'high'
        }
        return emphasis_mapping.get(content_type, 'medium')
    
    def _get_color_scheme_from_brand(self, brand: BrandIdentity) -> str:
        """Get color scheme recommendation based on brand colors"""
        if brand.colors.primary and brand.colors.secondary:
            return 'primary'
        elif brand.colors.accent:
            return 'accent'
        elif brand.colors.palette:
            return 'palette'
        else:
            return 'neutral'
    
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
        system_prompt = """You are a marketing editor. Improve flow, clarity, and specificity.
Ensure scannability (short sentences, strong verbs), remove redundancy, and keep benefit-driven phrasing.
Preserve the original JSON shape and section count. Do not invent placeholders. Return ONLY the polished outline JSON with identical shape."""
        
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
