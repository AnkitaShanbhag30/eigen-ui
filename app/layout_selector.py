"""
Layout Selector System
Scores each template against brand JSON + content outline and chooses top-k.
Supports A/B testing or ensemble generation.
"""

from typing import List, Dict, Tuple, Optional

# Handle imports for both direct execution and module import
try:
    from .template_registry import TEMPLATES, TemplateMeta, Channel
except ImportError:
    try:
        from template_registry import TEMPLATES, TemplateMeta, Channel
    except ImportError:
        # Fallback for testing
        TEMPLATES = []
        TemplateMeta = type('TemplateMeta', (), {})
        Channel = str

def features_from_brand(brand) -> Dict[str, float]:
    """Extract features from brand data for template matching"""
    # Handle both dict and Pydantic models
    if hasattr(brand, 'model_dump'):
        brand_dict = brand.model_dump()
    else:
        brand_dict = brand
    
    ui = brand_dict.get("ui_layout", {})
    page_structure = ui.get("page_structure", {})
    business_info = brand_dict.get("source_notes", "")
    tagline = brand_dict.get("tagline", "")
    
    # Detect features from UI layout analysis
    detected = {
        "has_products": 0.0,
        "has_pricing": 0.0,
        "has_testimonials": 0.0,
        "has_values": 0.0,
        "has_features": 0.0,
        "has_social_proof": 0.0,
        "has_pdp": 0.0,
        "has_personalization": 0.0,
        "has_data": 0.0,
        "has_ai": 0.0,
        "has_search": 0.0,
        "has_announcement": 0.0,
        "has_results": 0.0,
        "has_transformation": 0.0,
    }
    
    # Product detection
    if "has_products" in business_info or "products" in business_info.lower():
        detected["has_products"] = 1.0
    elif any(word in tagline.lower() for word in ["product", "platform", "solution", "tool"]):
        detected["has_products"] = 0.8
    
    # Pricing detection
    if "has_pricing" in business_info or "pricing" in business_info.lower():
        detected["has_pricing"] = 1.0
    elif any(word in tagline.lower() for word in ["pricing", "cost", "price", "subscription"]):
        detected["has_pricing"] = 0.7
    
    # Testimonials detection
    if "has_testimonials" in business_info:
        detected["has_testimonials"] = 1.0
    elif any(word in tagline.lower() for word in ["testimonial", "review", "feedback", "customer"]):
        detected["has_testimonials"] = 0.6
    
    # Values detection
    if "has_values" in business_info:
        detected["has_values"] = 1.0
    elif any(word in tagline.lower() for word in ["value", "mission", "purpose", "vision"]):
        detected["has_values"] = 0.5
    
    # Features detection
    if page_structure.get("content", {}).get("has_buttons") or page_structure.get("content", {}).get("has_forms"):
        detected["has_features"] = 0.8
    elif any(word in tagline.lower() for word in ["feature", "capability", "functionality"]):
        detected["has_features"] = 0.6
    
    # AI detection
    if "ai" in brand_dict.get("name", "").lower() or "ai" in tagline.lower():
        detected["has_ai"] = 1.0
        detected["has_search"] = 0.7  # AI often implies search
        detected["has_personalization"] = 0.8  # AI often implies personalization
    
    # Personalization detection
    if "personalization" in tagline.lower() or "personalized" in tagline.lower():
        detected["has_personalization"] = 1.0
        detected["has_data"] = 0.8
    
    # Social proof detection
    if detected["has_testimonials"] > 0.5:
        detected["has_social_proof"] = 0.8
    
    # PDP detection (Product Detail Page)
    if detected["has_products"] > 0.5:
        detected["has_pdp"] = 0.8
    
    # Data detection
    if any(word in tagline.lower() for word in ["data", "analytics", "insights", "metrics"]):
        detected["has_data"] = 0.7
    
    # Search detection
    if any(word in tagline.lower() for word in ["search", "discover", "find", "explore"]):
        detected["has_search"] = 0.8
    
    # Announcement detection
    if any(word in tagline.lower() for word in ["new", "launch", "announce", "release"]):
        detected["has_announcement"] = 0.7
    
    # Results/transformation detection
    if any(word in tagline.lower() for word in ["result", "outcome", "transform", "improve", "boost"]):
        detected["has_results"] = 0.7
        detected["has_transformation"] = 0.7
    
    return detected

def score_template(template: TemplateMeta, features: Dict[str, float]) -> float:
    """Score a template against detected features"""
    score = 0.0
    
    # Base score from fingerprint matching
    for feature, weight in template.fingerprint.items():
        feature_value = features.get(feature, 0.0)
        score += weight * feature_value
    
    # Bonus for density matching (if we have content density info)
    # This could be enhanced with actual content analysis
    
    return score

def pick_templates(brand, channel: Channel, top_k: int = 3, 
                  content_density: Optional[str] = None) -> List[TemplateMeta]:
    """Pick top-k templates for a brand and channel"""
    features = features_from_brand(brand)
    
    # Filter by channel
    candidates = [t for t in TEMPLATES if channel in t.channels]
    
    # Score and rank candidates
    scored = []
    for template in candidates:
        score = score_template(template, features)
        scored.append((score, template))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Return top-k
    return [template for score, template in scored[:top_k]]

def get_template_recommendations(brand, channel: Channel, 
                               include_reasoning: bool = False, top_k: int = 5) -> List[Dict]:
    """Get template recommendations with optional reasoning"""
    features = features_from_brand(brand)
    templates = pick_templates(brand, channel, top_k=top_k)
    
    recommendations = []
    for template in templates:
        score = score_template(template, features)
        rec = {
            "template": template,
            "score": score,
            "id": template.id,
            "path": template.path,
            "hero_style": template.hero_style,
            "density": template.density,
            "aspect_hint": template.aspect_hint
        }
        
        if include_reasoning:
            # Explain why this template was chosen
            reasons = []
            for feature, weight in template.fingerprint.items():
                feature_value = features.get(feature, 0.0)
                if feature_value > 0.3:  # Only mention relevant features
                    reasons.append(f"{feature}: {feature_value:.1f} (weight: {weight:.1f})")
            
            rec["reasoning"] = reasons
            rec["features"] = features
        
        recommendations.append(rec)
    
    return recommendations

def analyze_brand_content_fit(brand, channel: Channel) -> Dict:
    """Analyze how well a brand fits different content types"""
    features = features_from_brand(brand)
    
    # Get all templates for the channel
    channel_templates = [t for t in TEMPLATES if channel in t.channels]
    
    # Analyze fit for each content type
    content_analysis = {}
    for template in channel_templates:
        content_type = template.id.split('.')[-1]  # e.g., "hero-left-cta"
        score = score_template(template, features)
        
        if content_type not in content_analysis:
            content_analysis[content_type] = []
        
        content_analysis[content_type].append({
            "template_id": template.id,
            "score": score,
            "density": template.density,
            "hero_style": template.hero_style
        })
    
    # Sort each content type by score
    for content_type in content_analysis:
        content_analysis[content_type].sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "channel": channel,
        "detected_features": features,
        "content_analysis": content_analysis,
        "recommendations": get_template_recommendations(brand, channel, top_k=3)
    }
