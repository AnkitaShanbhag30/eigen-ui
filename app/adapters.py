# app/adapters.py
from typing import Any, Dict, List
try:
    from pydantic import BaseModel  # v2
except Exception:
    from pydantic.v1 import BaseModel  # just in case

def _to_dict(x):
    if isinstance(x, BaseModel):
        # v2: model_dump; v1: dict()
        return x.model_dump() if hasattr(x, "model_dump") else x.dict()
    return x

def coerce_ui_layout(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Ensure BrandIdentity.ui_layout matches the UILayoutData schema in brand.py:
      - design_patterns: List[DesignPattern]  --> list of dicts with normalized keys
      - interaction_patterns: InteractionPatterns --> dict, never a list
      - ensure nested models are dicts (avoid cross-module/v1-v2 BaseModel instances)
    """
    if not raw:
        return {
            "page_structure": {},
            "design_patterns": [],
            "spacing_system": {},
            "layout_grid": {},
            "component_patterns": {},
            "visual_hierarchy": {},
            "responsive_breakpoints": [],
            "interaction_patterns": {},  # dict for the model
            "css_structure": {},
            "screenshot_path": None,
            "layout_analysis": {}
        }

    out: Dict[str, Any] = {**raw}

    # Design patterns -> list of dicts with safe keys
    dps = []
    for item in (raw.get("design_patterns") or []):
        item = _to_dict(item)
        dps.append({
            "type": item.get("type", "grid"),
            "elements": [_to_dict(e) for e in (item.get("elements") or [])],
            "layout_type": item.get("layout_type", "block"),
            "spacing": item.get("spacing", {}) or {},
            "alignment": item.get("alignment", "left"),
        })
    out["design_patterns"] = dps

    # Interaction patterns must be a dict (your error shows a list)
    inter = raw.get("interaction_patterns") or {}
    if isinstance(inter, list):
        inter = {}  # or map into {"forms": [...]} if you have structure
    out["interaction_patterns"] = inter

    # Basic coercion for other nested models that might be BaseModel
    for k in ["page_structure", "spacing_system", "layout_grid",
              "component_patterns", "visual_hierarchy",
              "css_structure", "layout_analysis"]:
        if k in out:
            out[k] = _to_dict(out.get(k)) or {}

    return out
