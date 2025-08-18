import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

from typing import Optional

def public_url(local_path: str) -> Optional[str]:
    # Expose files under data/ via /static/ routes; return PUBLIC_BASE_URL + /static/...
    if not PUBLIC_BASE_URL:
        return None
    local_path = local_path.replace("\\", "/")
    if "/data/" in local_path:
        rel = local_path.split("/data/", 1)[1]
        return f"{PUBLIC_BASE_URL}/static/{quote(rel)}"
    # allow paths already under /static
    if "/static/" in local_path:
        rel = local_path.split("/static/", 1)[1]
        return f"{PUBLIC_BASE_URL}/static/{quote(rel)}"
    return None
