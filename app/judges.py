"""
AI Judges System
Re-ranks color schemes, templates, and content for taste, brand fit, and accessibility.
Integrates with existing LLM providers for intelligent decision making.
"""

from typing import List, Dict, Any, Optional
from .palette_harmonizer import validate_theme_contrast
from .layout_selector import score_template

def judge_color_schemes(candidates: List[Dict], brand: Dict, llm_provider=None) -> List[int]:
    """Rank color schemes for taste, brand fit, and accessibility"""
    if not candidates:
        return []
    
    # If no LLM provider, use rule-based ranking
    if not llm_provider:
        return _rule_based_color_ranking(candidates, brand)
    
    try:
        # Create prompt for LLM
        brand_name = brand.get("name", "Brand")
        brand_tone = brand.get("tone", "professional")
        brand_keywords = brand.get("keywords", [])
        
        prompt = f"""
        You are an accessibility-first brand design judge.
        Rank these color schemes for {brand_name} based on:
        1. Taste and visual appeal
        2. Brand fit ({brand_tone} tone, keywords: {', '.join(brand_keywords[:5])})
        3. Accessibility and contrast (WCAG AA for body text)
        4. Practical UI usage (primary/action, secondary/info, semantic/status roles)
        
        Color schemes:
        {_format_color_schemes_for_llm(candidates)}
        
        Return only the ranking as a JSON array of indices, best to worst.
        Example: [0, 2, 1] means scheme 0 is best, scheme 2 is second, scheme 1 is worst.
        """
        
        # Call LLM (this would integrate with your existing LLM system)
        # For now, return rule-based ranking
        return _rule_based_color_ranking(candidates, brand)
        
    except Exception as e:
        # Fallback to rule-based ranking
        return _rule_based_color_ranking(candidates, brand)

def _rule_based_color_ranking(candidates: List[Dict], brand: Dict) -> List[int]:
    """Rule-based color scheme ranking when LLM is unavailable"""
    scored = []
    
    for i, scheme in enumerate(candidates):
        score = 0.0
        
        # Accessibility score (40% weight)
        contrast_validation = validate_theme_contrast(scheme)
        if contrast_validation["valid"]:
            score += 0.4
        else:
            # Penalize based on number of contrast issues
            score += max(0, 0.4 - (contrast_validation["overall_score"] * 0.1))
        
        # Brand fit score (35% weight)
        brand_fit = _calculate_brand_fit_score(scheme, brand)
        score += brand_fit * 0.35
        
        # Visual harmony score (25% weight)
        harmony_score = _calculate_harmony_score(scheme)
        score += harmony_score * 0.25
        
        scored.append((score, i))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [index for score, index in scored]

def _calculate_brand_fit_score(scheme: Dict, brand: Dict) -> float:
    """Calculate how well a color scheme fits the brand"""
    score = 0.0
    
    # Check if brand colors are preserved
    brand_colors = brand.get("colors", {})
    scheme_colors = scheme.get("base_colors", {})
    
    if brand_colors.get("primary") == scheme_colors.get("primary"):
        score += 0.3
    if brand_colors.get("secondary") == scheme_colors.get("secondary"):
        score += 0.2
    
    # Check tone alignment
    brand_tone = brand.get("tone", "").lower()
    if "professional" in brand_tone or "corporate" in brand_tone:
        # Prefer more muted, professional colors
        if _is_muted_scheme(scheme):
            score += 0.2
    elif "creative" in brand_tone or "vibrant" in brand_tone:
        # Prefer more vibrant colors
        if _is_vibrant_scheme(scheme):
            score += 0.2
    
    # Check industry fit
    brand_name = brand.get("name", "").lower()
    if "ai" in brand_name or "tech" in brand_name:
        # Tech brands often work well with blues and modern colors
        if _has_tech_colors(scheme):
            score += 0.1
    
    return min(1.0, score)

def _calculate_harmony_score(scheme: Dict) -> float:
    """Calculate visual harmony score for a color scheme"""
    score = 0.0
    tokens = scheme.get("tokens", {})
    
    # Check for balanced color distribution
    brand_colors = [k for k in tokens.keys() if k.startswith("brand-")]
    accent_colors = [k for k in tokens.keys() if k.startswith("accent-")]
    neutral_colors = [k for k in tokens.keys() if k.startswith("neutral-")]
    
    # Balanced distribution is good
    if len(brand_colors) >= 8 and len(accent_colors) >= 8 and len(neutral_colors) >= 8:
        score += 0.3
    
    # Check for good contrast range
    if tokens.get("brand-50") and tokens.get("brand-900"):
        score += 0.2
    
    # Check for semantic color presence
    if all(k in tokens for k in ["success", "warning", "error"]):
        score += 0.2
    
    # Check for good surface/text contrast
    if tokens.get("surface") and tokens.get("text"):
        score += 0.3
    
    return min(1.0, score)

def _is_muted_scheme(scheme: Dict) -> bool:
    """Check if a color scheme is muted"""
    tokens = scheme.get("tokens", {})
    # Check if we have muted variants
    return any("muted" in k for k in tokens.keys())

def _is_vibrant_scheme(scheme: Dict) -> bool:
    """Check if a color scheme is vibrant"""
    tokens = scheme.get("tokens", {})
    # Check if we have bright accent colors
    return any("accent" in k and "50" in k for k in tokens.keys())

def _has_tech_colors(scheme: Dict) -> bool:
    """Check if a color scheme has tech-appropriate colors"""
    tokens = scheme.get("tokens", {})
    # Tech brands often use blues, grays, and modern colors
    return any("blue" in str(v).lower() or "gray" in str(v).lower() for v in tokens.values())

def _format_color_schemes_for_llm(candidates: List[Dict]) -> str:
    """Format color schemes for LLM prompt"""
    formatted = []
    
    for i, scheme in enumerate(candidates):
        base_colors = scheme.get("base_colors", {})
        variant_name = scheme.get("variant_name", "base")
        
        scheme_info = f"Scheme {i} ({variant_name}):\n"
        scheme_info += f"  Primary: {base_colors.get('primary', 'N/A')}\n"
        scheme_info += f"  Secondary: {base_colors.get('secondary', 'N/A')}\n"
        scheme_info += f"  Accent: {base_colors.get('accent', 'N/A')}\n"
        scheme_info += f"  Muted: {base_colors.get('muted', 'N/A')}\n"
        
        # Add contrast validation
        contrast_validation = validate_theme_contrast(scheme)
        if contrast_validation["valid"]:
            scheme_info += "  ✓ Contrast: Valid\n"
        else:
            scheme_info += f"  ✗ Contrast: {len(contrast_validation['issues'])} issues\n"
        
        formatted.append(scheme_info)
    
    return "\n".join(formatted)

def judge_template_selection(templates: List[Dict], brand: Dict, 
                           content_outline: Dict, llm_provider=None) -> List[int]:
    """Rank templates for content fit and brand alignment"""
    if not templates:
        return []
    
    # If no LLM provider, use rule-based ranking
    if not llm_provider:
        return _rule_based_template_ranking(templates, brand, content_outline)
    
    try:
        # Create prompt for LLM
        brand_name = brand.get("name", "Brand")
        content_type = content_outline.get("template", "onepager")
        
        prompt = f"""
        You are a senior UX judge. Rank these templates for {brand_name} {content_type} based on:
        1. Content fit (headlines, sections, CTA placement; unique sections, non-redundant)
        2. Brand personality alignment
        3. Visual hierarchy and readability (assume ~1.25 type scale, 4/8px rhythm)
        4. Accessibility (focus states, adequate contrast, touch target sizing on mobile)
        
        Templates:
        {_format_templates_for_llm(templates)}
        
        Content outline:
        {_format_content_outline_for_llm(content_outline)}
        
        Return only the ranking as a JSON array of indices, best to worst.
        """
        
        # Call LLM (this would integrate with your existing LLM system)
        # For now, return rule-based ranking
        return _rule_based_template_ranking(templates, brand, content_outline)
        
    except Exception as e:
        # Fallback to rule-based ranking
        return _rule_based_template_ranking(templates, brand, content_outline)

def _rule_based_template_ranking(templates: List[Dict], brand: Dict, 
                                content_outline: Dict) -> List[int]:
    """Rule-based template ranking when LLM is unavailable"""
    scored = []
    
    for i, template_info in enumerate(templates):
        score = 0.0
        
        # Content fit score (40% weight)
        content_fit = _calculate_content_fit_score(template_info, content_outline)
        score += content_fit * 0.4
        
        # Brand alignment score (35% weight)
        brand_alignment = _calculate_brand_alignment_score(template_info, brand)
        score += brand_alignment * 0.35
        
        # Visual hierarchy score (25% weight)
        hierarchy_score = _calculate_hierarchy_score(template_info)
        score += hierarchy_score * 0.25
        
        scored.append((score, i))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [index for score, index in scored]

def _calculate_content_fit_score(template_info: Dict, content_outline: Dict) -> float:
    """Calculate how well a template fits the content"""
    score = 0.0
    
    # Check if template has required slots
    template_slots = template_info.get("slots", [])
    required_sections = content_outline.get("sections", [])
    
    # Count matching sections
    matches = 0
    for section in required_sections:
        if any(slot in str(section).lower() for slot in template_slots):
            matches += 1
    
    if required_sections:
        score += (matches / len(required_sections)) * 0.5
    
    # Check density match
    template_density = template_info.get("density", "medium")
    content_length = len(str(content_outline))
    
    if template_density == "light" and content_length < 1000:
        score += 0.3
    elif template_density == "medium" and 1000 <= content_length < 2000:
        score += 0.3
    elif template_density == "heavy" and content_length >= 2000:
        score += 0.3
    
    return min(1.0, score)

def _calculate_brand_alignment_score(template_info: Dict, brand: Dict) -> float:
    """Calculate how well a template aligns with brand personality"""
    score = 0.0
    
    # Check hero style alignment
    hero_style = template_info.get("hero_style", "centered")
    brand_tone = brand.get("tone", "").lower()
    
    if "professional" in brand_tone and hero_style in ["centered", "left"]:
        score += 0.3
    elif "creative" in brand_tone and hero_style in ["right", "split"]:
        score += 0.3
    
    # Check if template supports brand features
    template_fingerprint = template_info.get("fingerprint", {})
    brand_features = _extract_brand_features(brand)
    
    feature_match = 0
    for feature, weight in template_fingerprint.items():
        if feature in brand_features:
            feature_match += weight
    
    if template_fingerprint:
        score += min(0.4, feature_match / sum(template_fingerprint.values()))
    
    return min(1.0, score)

def _calculate_hierarchy_score(template_info: Dict) -> float:
    """Calculate visual hierarchy score for a template"""
    score = 0.0
    
    # Check if template has good content structure
    slots = template_info.get("slots", [])
    
    # Hero section is important
    if "hero" in slots:
        score += 0.3
    
    # CTA placement is important
    if "cta" in slots:
        score += 0.2
    
    # Multiple content sections for good flow
    if len(slots) >= 4:
        score += 0.2
    
    # Check for good content distribution
    if "features" in slots or "benefits" in slots:
        score += 0.2
    
    # Social proof is valuable
    if "testimonials" in slots or "social_proof" in slots:
        score += 0.1
    
    return min(1.0, score)

def _extract_brand_features(brand: Dict) -> List[str]:
    """Extract brand features for template matching"""
    features = []
    
    # Extract from business info
    business_info = brand.get("source_notes", "").lower()
    if "has_products" in business_info:
        features.append("has_products")
    if "has_pricing" in business_info:
        features.append("has_pricing")
    if "has_testimonials" in business_info:
        features.append("has_testimonials")
    if "has_values" in business_info:
        features.append("has_values")
    
    # Extract from brand name and tone
    brand_name = brand.get("name", "").lower()
    if "ai" in brand_name:
        features.append("has_ai")
    
    return features

def _format_templates_for_llm(templates: List[Dict]) -> str:
    """Format templates for LLM prompt"""
    formatted = []
    
    for i, template_info in enumerate(templates):
        template = template_info.get("template", {})
        
        template_desc = f"Template {i}:\n"
        template_desc += f"  ID: {template.get('id', 'N/A')}\n"
        template_desc += f"  Hero style: {template.get('hero_style', 'N/A')}\n"
        template_desc += f"  Density: {template.get('density', 'N/A')}\n"
        template_desc += f"  Slots: {', '.join(template.get('slots', []))}\n"
        template_desc += f"  Fingerprint: {template.get('fingerprint', {})}\n"
        
        formatted.append(template_desc)
    
    return "\n".join(formatted)

def _format_content_outline_for_llm(content_outline: Dict) -> str:
    """Format content outline for LLM prompt"""
    outline_desc = f"Content Type: {content_outline.get('template', 'N/A')}\n"
    outline_desc += f"Headline: {content_outline.get('headline', 'N/A')}\n"
    outline_desc += f"Subhead: {content_outline.get('subhead', 'N/A')}\n"
    outline_desc += f"CTA: {content_outline.get('cta', 'N/A')}\n"
    outline_desc += f"Sections: {len(content_outline.get('sections', []))}\n"
    
    return outline_desc

def get_judgment_summary(rankings: Dict[str, List[int]], 
                        candidates: Dict[str, List]) -> str:
    """Generate a summary of all judgments"""
    summary = "AI Judgment Summary:\n\n"
    
    for category, ranking in rankings.items():
        summary += f"{category.title()}:\n"
        if category in candidates:
            for i, rank in enumerate(ranking):
                candidate = candidates[category][rank]
                if hasattr(candidate, 'get'):
                    name = candidate.get('variant_name', f'Variant {rank}')
                    summary += f"  {i+1}. {name} (Rank {rank})\n"
                else:
                    summary += f"  {i+1}. Variant {rank}\n"
        summary += "\n"
    
    return summary
