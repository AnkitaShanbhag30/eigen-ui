#!/usr/bin/env python3
"""
Unit tests for multi-step prompting flow in app.generate
Ensures planning → per-section generation → summary assembly works and is brand-agnostic.
"""

import json
import pytest
from unittest.mock import patch


def _minimal_brand():
    return {
        "name": "Example Brand",
        "website": "https://example.com",
        "tagline": "Example tagline",
        "description": "Example description",
        "colors": {"primary": "#3366FF", "secondary": "#111111", "accent": "#FF9900", "muted": "#CCCCCC"},
        "typography": {"heading": "Inter", "body": "Inter"},
        "tone": "professional",
        "keywords": ["innovative", "reliable", "scalable"],
    }


@patch("app.generate.generate_json")
def test_multistep_outline_flow(mock_gen):
    """Validate that outline_for orchestrates plan → section → summary and assembles the outline."""
    def side_effect(system: str, user: str):
        if "PHASE: PLAN" in system:
            return {
                "layout": {
                    "variant": "feature-rail-3up",
                    "has_hero": True,
                    "grid": {"columns": 2},
                    "density": "balanced",
                    "order": ["hero", "about", "features"]
                },
                "sections": [
                    {"content_type": "hero", "title_hint": "Hero", "theme": "Big brand headline", "layout_style": "hero"},
                    {"content_type": "about", "title_hint": "About", "theme": "What and why", "layout_style": "text"},
                    {"content_type": "features", "title_hint": "Features", "theme": "Key value props", "layout_style": "grid"},
                ]
            }
        if "PHASE: SECTION" in system:
            data = json.loads(user)
            ct = data["section_request"]["content_type"]
            # Ensure theme and title_hint are passed through
            assert "title_hint" in data["section_request"]
            assert "theme" in data["section_request"]
            if ct == "about":
                return {
                    "title": "About Our Platform",
                    "description": "What we do and why it matters.",
                    "bullets": ["Trusted by teams", "Built for speed"],
                    "content_type": "about",
                    "layout_style": "text",
                }
            if ct == "features":
                return {
                    "title": "Key Capabilities",
                    "description": "Highlights of the product.",
                    "bullets": ["Automation", "Analytics", "APIs"],
                    "content_type": "features",
                    "layout_style": "grid",
                }
            if ct == "hero":
                return {
                    "title": "Build Better, Faster",
                    "description": "Make an impact",
                    "bullets": [],
                    "content_type": "hero",
                    "layout_style": "hero",
                }
            return {}
        if "PHASE: SUMMARY" in system:
            return {"headline": "Build Better, Faster", "subhead": "Move from idea to impact", "cta": "Try it now"}
        return {}

    mock_gen.side_effect = side_effect

    from app.generate import outline_for

    outline = outline_for(
        template="onepager",
        brand=_minimal_brand(),
        x="AI platform",
        y="accelerate delivery",
        z="developers",
        w="",
        cta="Start Free"
    )

    assert outline.get("headline") == "Build Better, Faster"
    assert outline.get("cta") == "Try it now"
    assert isinstance(outline.get("sections"), list)
    assert len(outline["sections"]) == 3
    # Order should follow plan layout.order: hero → about → features
    assert outline["sections"][0]["content_type"] == "hero"
    assert outline["sections"][1]["content_type"] == "about"
    assert outline["sections"][2]["content_type"] == "features"
    # Layout metadata captured
    assert outline.get("meta", {}).get("proposed_layout", {}).get("variant") == "feature-rail-3up"


def test_multistep_outline_fallbacks():
    """If multi-step and enhanced brand-aware flows fail, we should still return a fallback outline."""
    from app.generate import outline_for

    with patch("app.generate.build_outline_multistep", side_effect=Exception("boom")):
        with patch("app.design.DesignAdvisorService.generate_content_outline", side_effect=Exception("boom2")):
            outline = outline_for(
                template="onepager",
                brand=_minimal_brand(),
                x="Platform",
                y="solve problems",
                z="teams",
                w="",
                cta="Get Started"
            )
            assert outline.get("headline")
            assert outline.get("cta")
            assert isinstance(outline.get("sections"), list)
            assert len(outline["sections"]) >= 1


