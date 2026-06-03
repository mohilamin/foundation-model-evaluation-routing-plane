"""Tests for future enhancement readiness scorecard."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_future_enhancement_scorecard_runs() -> None:
    """The future enhancement readiness script should create JSON and CSV outputs."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_future_enhancement_scorecard.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    json_path = Path("data/scorecards/future_enhancement_readiness.json")
    csv_path = Path("data/scorecards/future_enhancement_readiness.csv")
    assert json_path.exists()
    assert csv_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["future_enhancement_count"] >= 5
    assert 0 <= payload["readiness_score"] <= 100
    assert payload["interpretation"].startswith("Local roadmap readiness")
