"""
Template Registry System
Allows growing a large corpus of templates without touching code each time.
Each template gets fingerprint, slots, density, hero_style, and channel metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Literal

Channel = Literal["onepager", "story", "linkedin"]

@dataclass
class TemplateMeta:
    id: str
    path: str
    channels: List[Channel]
    fingerprint: Dict[str, float]  # weights for: has_testimonials, has_pricing, has_products, has_values...
    slots: List[str]               # ["hero", "features_3up", "testimonials", "pricing", "cta", ...]
    density: Literal["light", "medium", "heavy"]
    hero_style: Literal["left", "right", "centered", "split"]
    aspect_hint: str = "16:9"      # 16:9, 4:5, 9:16

TEMPLATES: List[TemplateMeta] = [
    # One-pager Templates
    TemplateMeta(
        id="onepager.hero-left-cta",
        path="templates/onepager/hero-left-cta.html.j2",
        channels=["onepager"],
        fingerprint={"has_products": 0.6, "has_testimonials": 0.4, "has_pricing": 0.2},
        slots=["hero", "features_3up", "testimonials", "cta"],
        density="medium", 
        hero_style="left", 
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="onepager.hero-right-cta",
        path="templates/onepager/hero-right-cta.html.j2",
        channels=["onepager"],
        fingerprint={"has_products": 0.6, "has_values": 0.3},
        slots=["hero", "feature_rail", "cta"],
        density="light", 
        hero_style="right",
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="onepager.hero-centered-split",
        path="templates/onepager/hero-centered-split.html.j2",
        channels=["onepager"],
        fingerprint={"has_testimonials": 0.5, "has_values": 0.4, "has_pricing": 0.3},
        slots=["hero", "testimonials", "pricing", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="onepager.feature-rail-3up",
        path="templates/onepager/feature-rail-3up.html.j2",
        channels=["onepager"],
        fingerprint={"has_products": 0.8, "has_features": 0.7},
        slots=["hero", "features_3up", "cta"],
        density="heavy", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="onepager.testimonial-stack",
        path="templates/onepager/testimonial-stack.html.j2",
        channels=["onepager"],
        fingerprint={"has_testimonials": 0.9, "has_social_proof": 0.8},
        slots=["hero", "testimonials", "social_proof", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="onepager.pricing-2col",
        path="templates/onepager/pricing-2col.html.j2",
        channels=["onepager"],
        fingerprint={"has_pricing": 0.9, "has_products": 0.6},
        slots=["hero", "pricing", "features", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
    
    # Story Templates (9:16)
    TemplateMeta(
        id="story.story-pdp-cta",
        path="templates/story/story-pdp-cta.html.j2",
        channels=["story"],
        fingerprint={"has_products": 0.8, "has_pdp": 0.9},
        slots=["hero", "pdp_features", "cta"],
        density="light", 
        hero_style="centered",
        aspect_hint="9:16"
    ),
    TemplateMeta(
        id="story.story-highlights",
        path="templates/story/story-highlights.html.j2",
        channels=["story"],
        fingerprint={"has_personalization": 0.9, "has_data": 0.8},
        slots=["hero", "highlights", "personalization", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="9:16"
    ),
    TemplateMeta(
        id="story.story-ai-search",
        path="templates/story/story-ai-search.html.j2",
        channels=["story"],
        fingerprint={"has_ai": 0.9, "has_search": 0.8},
        slots=["hero", "ai_features", "search_demo", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="9:16"
    ),
    
    # LinkedIn Templates
    TemplateMeta(
        id="linkedin.li-product-announcement",
        path="templates/linkedin/li-product-announcement.html.j2",
        channels=["linkedin"],
        fingerprint={"has_products": 0.8, "has_announcement": 0.7},
        slots=["hero", "product_announcement", "cta"],
        density="light", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
    TemplateMeta(
        id="linkedin.li-before-after",
        path="templates/linkedin/li-before-after.html.j2",
        channels=["linkedin"],
        fingerprint={"has_results": 0.9, "has_transformation": 0.8},
        slots=["hero", "before_after", "results", "cta"],
        density="medium", 
        hero_style="centered",
        aspect_hint="16:9"
    ),
]

def get_templates_for_channel(channel: Channel) -> List[TemplateMeta]:
    """Get all templates for a specific channel"""
    return [t for t in TEMPLATES if channel in t.channels]

def get_template_by_id(template_id: str) -> TemplateMeta:
    """Get a specific template by ID"""
    for template in TEMPLATES:
        if template.id == template_id:
            return template
    raise ValueError(f"Template {template_id} not found")

def get_templates_by_fingerprint(fingerprint_weights: Dict[str, float], channel: Channel = None) -> List[TemplateMeta]:
    """Get templates sorted by fingerprint match"""
    candidates = TEMPLATES
    if channel:
        candidates = [t for t in TEMPLATES if channel in t.channels]
    
    # Score each template
    scored = []
    for template in candidates:
        score = sum(template.fingerprint.get(k, 0) * fingerprint_weights.get(k, 0) 
                   for k in set(template.fingerprint) | set(fingerprint_weights))
        scored.append((score, template))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [template for score, template in scored]
