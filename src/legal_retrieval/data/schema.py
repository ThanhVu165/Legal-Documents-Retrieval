"""Configuration and lossless source-ID validation for W01."""

import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml


def normalize_id(value: Any) -> str | None:
    """Preserve strings verbatim; allow integers, never floats/bools or trimming."""
    if type(value) is int:
        return str(value)
    if isinstance(value, str) and value and value.strip() == value:
        if any(unicodedata.category(c).startswith("C") for c in value):
            return None
        return value
    return None


def load_config(path: str | Path) -> dict[str, Any]:
    """Read YAML and reject malformed dataset identifiers or unpinned revisions."""
    config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("dataset"), dict):
        raise ValueError("Expected dataset mapping in config")
    dataset = config["dataset"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", str(dataset.get("id", ""))):
        raise ValueError("Invalid dataset ID")
    revision = dataset.get("revision")
    if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", str(revision)):
        raise ValueError("revision must be null or a 40-character commit SHA")
    if type(config.get("seed", 42)) is not int:
        raise ValueError("seed must be an integer")
    return config
