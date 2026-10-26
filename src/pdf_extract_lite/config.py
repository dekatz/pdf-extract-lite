"""Load and check a site YAML config. No network, no PDF text."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED = ("name", "source", "download", "extract")
SOURCE_TYPES = {"html_archive", "url_template", "link_list"}
AUTH_TYPES = {"none", "bearer_env", "cookie_env"}


def load_config(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be a YAML mapping")
    missing = [key for key in REQUIRED if key not in raw]
    if missing:
        raise ValueError(f"{path} missing keys: {', '.join(missing)}")
    source = raw["source"]
    if source.get("type") not in SOURCE_TYPES:
        raise ValueError(f"source.type must be one of {sorted(SOURCE_TYPES)}")
    auth = raw.get("auth") or {"type": "none"}
    if auth.get("type") not in AUTH_TYPES:
        raise ValueError(f"auth.type must be one of {sorted(AUTH_TYPES)}")
    raw["auth"] = auth
    raw["download"].setdefault("rate_limit_seconds", 0.2)
    raw["download"].setdefault("retries", 3)
    raw["download"].setdefault("min_bytes", 10_000)
    raw["download"].setdefault("timeout_seconds", 60)
    raw["extract"].setdefault("series", [])
    raw["extract"].setdefault("section_markers", [])
    raw["extract"].setdefault("section_end_markers", [])
    raw["_config_path"] = str(path)
    return raw


def project_root(config: dict[str, Any]) -> Path:
    return Path(config["_config_path"]).resolve().parents[1]
