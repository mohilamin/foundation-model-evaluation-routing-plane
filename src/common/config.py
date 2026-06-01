"""Configuration loading helpers."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
