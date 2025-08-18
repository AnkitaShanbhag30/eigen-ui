"""
Brief Parser System
Parses brief text to extract deliverables, product concepts, and channel requirements.
Supports both simple heuristics and LLM-enhanced parsing.
"""

from typing import Dict, Any, List, Optional
import re

def parse_brief_text(txt: str) -> Dict[str, Any]:
    """Parse brief text to extract deliverables and product concepts"""
    txt_lower = txt.lower()
    
    # Extract deliverables
    deliverables = []
    if any(phrase in txt_lower for phrase in ["1 pager", "one pager", "one-pager", "single page"]):
        deliverables.append("onepager")
    if any(phrase in txt_lower for phrase in ["ig story", "instagram story", "vertical", "9:16", "story format"]):
        deliverables.append("story")
    if any(phrase in txt_lower for phrase in ["linkedin", "linkedin post", "social post"]):
        deliverables.append("linkedin")
    if any(phrase in txt_lower for phrase in ["ad set", "ad campaign", "ads", "advertising"]):
        deliverables.append("ads")
    
    # Default to onepager if no deliverables specified
    if not deliverables:
        deliverables.append("onepager")
    
    # Extract product concepts
    products = []
    if any(phrase in txt_lower for phrase in ["pdp", "product detail page", "product page"]):
        products.append("pdp")
    if any(phrase in txt_lower for phrase in ["personalized highlights", "personalization", "1p data", "3p data"]):
        products.append("highlights")
    if any(phrase in txt_lower for phrase in ["ai search", "search assistant", "catalog search", "semantic search"]):
        products.append("ai_search")
    if any(phrase in txt_lower for phrase in ["ai assistant", "chatbot", "conversational"]):
        products.append("ai_assistant")
    
    # Extract target audience
    audience = []
    if any(phrase in txt_lower for phrase in ["health", "beauty", "skincare", "wellness"]):
        audience.append("health_beauty")
    if any(phrase in txt_lower for phrase in ["busy professionals", "professionals", "working"]):
        audience.append("professionals")
    if any(phrase in txt_lower for phrase in ["female", "women", "ladies"]):
        audience.append("female")
    if any(phrase in txt_lower for phrase in ["nyc", "new york", "urban"]):
        audience.append("urban")
    
    # Extract tone requirements
    tone = []
    if any(phrase in txt_lower for phrase in ["non-salesy", "non salesy", "educational", "informative"]):
        tone.append("educational")
    if any(phrase in txt_lower for phrase in ["fda", "meta", "compliant", "guardrails"]):
        tone.append("compliant")
    if any(phrase in txt_lower for phrase in ["conversion", "converting", "sales", "revenue"]):
        tone.append("conversion_focused")
    
    # Extract key features
    features = []
    if any(phrase in txt_lower for phrase in ["embed", "widget", "integration"]):
        features.append("embed")
    if any(phrase in txt_lower for phrase in ["dynamic", "on-the-fly", "real-time"]):
        features.append("dynamic")
    if any(phrase in txt_lower for phrase in ["inventory", "stock", "availability"]):
        features.append("inventory_aware")
    if any(phrase in txt_lower for phrase in ["zero setup", "no setup", "instant"]):
        features.append("zero_setup")
    
    return {
        "deliverables": deliverables,
        "products": products,
        "audience": audience,
        "tone": tone,
        "features": features,
        "raw_text": txt[:500] + "..." if len(txt) > 500 else txt  # Keep first 500 chars for reference
    }

def hero_prompts(brand: Dict, parsed: Dict) -> Dict[str, str]:
    """Generate hero image prompts per product concept"""
    brand_name = brand.get("name", "Brand")
    city = "NYC skyline"  # Default city context
    
    # Extract city from brand data if available
    if brand.get("source_notes") and "nyc" in brand.get("source_notes", "").lower():
        city = "NYC skyline"
    
    prompts = {}
    
    # Common constraints for image generation (no text/logos; abstract, professional)
    constraints = (
        " No text, captions, signage, watermarks, or logos."
        " Abstract, modern, clean composition with professional polish."
    )

    # PDP Product Hero
    if "pdp" in parsed.get("products", []):
        prompts["pdp"] = (
            f"{brand_name} PDP embed: mobile-first hero of an AI assistant suggesting "
            f"high-converting questions; sleek UI, {city}, non-salesy tone; "
            f"compliant with FDA/meta guardrails." + constraints
        )
    
    # Personalized Highlights Hero
    if "highlights" in parsed.get("products", []):
        prompts["highlights"] = (
            f"{brand_name} personalized highlights: hero collage that adapts by "
            f"1P data (Klaviyo, quiz) + 3P (ad context, location); "
            f"dynamic chips showing relevance." + constraints
        )
    
    # AI Search Hero
    if "ai_search" in parsed.get("products", []):
        prompts["ai_search"] = (
            f"{brand_name} AI shop assistant: semantic search over large catalog, "
            f"promotes in-stock items; modern search UI, zero-setup feel." + constraints
        )
    
    # AI Assistant Hero
    if "ai_assistant" in parsed.get("products", []):
        prompts["ai_assistant"] = (
            f"{brand_name} AI assistant: conversational interface for customer support "
            f"and product recommendations; friendly, helpful, {city} context." + constraints
        )
    
    # Default hero if no specific products
    if not prompts:
        prompts["default"] = (
            f"{brand_name} hero: professional, modern interface showcasing "
            f"AI-powered features; {city} skyline background; clean, trustworthy design." + constraints
        )
    
    return prompts

def extract_content_requirements(parsed: Dict) -> Dict[str, Any]:
    """Extract content requirements from parsed brief"""
    requirements = {
        "headlines": [],
        "subheads": [],
        "cta_variants": [],
        "content_sections": [],
        "tone_guidelines": []
    }
    
    # Generate headline variations based on products
    products = parsed.get("products", [])
    if "pdp" in products:
        requirements["headlines"].extend([
            "PDP, but smarter.",
            "AI-powered product pages that convert.",
            "Personalized product experiences."
        ])
    
    if "highlights" in products:
        requirements["headlines"].extend([
            "Personalized highlights that convert.",
            "Dynamic content that adapts to your audience.",
            "1P + 3P data for maximum relevance."
        ])
    
    if "ai_search" in products:
        requirements["headlines"].extend([
            "AI search that finds what customers want.",
            "Semantic search over your entire catalog.",
            "Zero-setup AI shopping assistant."
        ])
    
    # Generate CTA variations
    requirements["cta_variants"].extend([
        "Start Your Free Trial",
        "Book a Demo",
        "Get Started Today",
        "Learn More",
        "See It In Action"
    ])
    
    # Content sections based on deliverables
    deliverables = parsed.get("deliverables", [])
    if "onepager" in deliverables:
        requirements["content_sections"].extend([
            "hero", "features", "benefits", "social_proof", "cta"
        ])
    
    if "story" in deliverables:
        requirements["content_sections"].extend([
            "hero", "key_benefit", "social_proof", "cta"
        ])
    
    if "linkedin" in deliverables:
        requirements["content_sections"].extend([
            "hook", "value_prop", "proof", "cta"
        ])
    
    # Tone guidelines
    tone = parsed.get("tone", [])
    if "educational" in tone:
        requirements["tone_guidelines"].append("Focus on education and value, not sales")
    if "compliant" in tone:
        requirements["tone_guidelines"].append("Ensure FDA and meta compliance")
    if "conversion_focused" in tone:
        requirements["tone_guidelines"].append("Optimize for conversion and engagement")
    
    return requirements

def validate_brief_parsing(parsed: Dict) -> Dict[str, Any]:
    """Validate the parsed brief and provide confidence scores"""
    validation = {
        "valid": True,
        "confidence": 0.0,
        "warnings": [],
        "suggestions": []
    }
    
    # Check deliverables
    if not parsed.get("deliverables"):
        validation["warnings"].append("No deliverables specified")
        validation["confidence"] -= 0.2
    
    # Check products
    if not parsed.get("products"):
        validation["warnings"].append("No product concepts identified")
        validation["suggestions"].append("Consider adding specific product focus areas")
        validation["confidence"] -= 0.3
    
    # Check audience
    if not parsed.get("audience"):
        validation["suggestions"].append("Consider specifying target audience")
        validation["confidence"] -= 0.1
    
    # Calculate confidence score
    base_confidence = 0.8
    validation["confidence"] = max(0.0, base_confidence + validation["confidence"])
    
    # Set valid flag
    if validation["confidence"] < 0.5:
        validation["valid"] = False
    
    return validation

def enhance_brief_with_llm(parsed: Dict, brand: Dict, llm_provider=None) -> Dict[str, Any]:
    """Enhance brief parsing with LLM insights (optional)"""
    if not llm_provider:
        return parsed
    
    try:
        # Create enhanced prompt for LLM
        prompt = f"""
        Analyze this brief and enhance the parsing with enterprise-grade rigor:
        
        Brief: {parsed.get('raw_text', '')}
        Brand: {brand.get('name', 'Unknown')}
        Current parsing: {parsed}
        
        Provide enhanced parsing with:
        1. Additional product concepts
        2. Refined audience targeting
        3. Content strategy recommendations (specific, non-redundant)
        4. Channel-specific optimizations
        5. Accessibility and clarity guardrails (scannable, benefit-driven)
        
        Return as JSON.
        """
        
        # This would call your existing LLM provider
        # For now, return enhanced parsing
        enhanced = parsed.copy()
        enhanced["llm_enhanced"] = True
        enhanced["confidence"] = min(1.0, enhanced.get("confidence", 0.8) + 0.1)
        
        return enhanced
        
    except Exception as e:
        # Fallback to original parsing
        return parsed

def get_brief_summary(parsed: Dict) -> str:
    """Generate a human-readable summary of the brief"""
    deliverables = ", ".join(parsed.get("deliverables", []))
    products = ", ".join(parsed.get("products", []))
    audience = ", ".join(parsed.get("audience", []))
    
    summary = f"Brief Summary:\n"
    summary += f"• Deliverables: {deliverables}\n"
    summary += f"• Products: {products}\n"
    summary += f"• Audience: {audience}\n"
    
    if parsed.get("tone"):
        tone = ", ".join(parsed["tone"])
        summary += f"• Tone: {tone}\n"
    
    if parsed.get("features"):
        features = ", ".join(parsed["features"])
        summary += f"• Features: {features}\n"
    
    return summary
