"""Generate a future enhancement readiness scorecard.

The scorecard converts the production roadmap into a small runnable check. It
is intentionally local and deterministic: no cloud account, API key, or network
service is required.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "future_enhancements.json"
OUT_DIR = ROOT / "data" / "scorecards"


def exists(path: str) -> bool:
    """Return whether a repo-relative path exists."""
    return (ROOT / path).exists()


def main() -> int:
    """Write future enhancement readiness JSON and CSV outputs."""
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    checks = {
        "production_roadmap_doc": exists("docs/production-roadmap.md"),
        "design_decisions_doc": exists("docs/design-decisions.md"),
        "tradeoffs_doc": exists("docs/tradeoffs-and-simplifications.md"),
        "validation_log_doc": exists("docs/validation-log.md"),
        "repo_review_guide": exists("docs/repo-review-guide.md"),
        "readme_exists": exists("README.md"),
        "ci_workflow_present": (
            exists(".github/workflows/ci.yml")
            or exists(".github/workflows/docs-check.yml")
        ),
        "dockerfile_present": exists("Dockerfile"),
        "api_entrypoint_present": exists("src/api/main.py"),
        "dashboard_entrypoint_present": (
            exists("src/dashboard/app.py") or exists("app.py")
        ),
    }
    implemented = sum(
        1
        for item in config["future_enhancements"]
        if item.get("status") == "implemented"
    )
    planned = len(config["future_enhancements"])
    documentation_score = sum(checks.values()) / len(checks)
    implementation_score = implemented / max(planned, 1)
    readiness_score = round(documentation_score * 80 + implementation_score * 20, 2)
    payload = {
        "project_name": config["project_name"],
        "enhancement_theme": config["enhancement_theme"],
        "future_enhancement_count": planned,
        "implemented_enhancement_count": implemented,
        "readiness_checks": checks,
        "future_enhancements": config["future_enhancements"],
        "readiness_score": readiness_score,
        "interpretation": (
            "Local roadmap readiness score. "
            "This does not claim production readiness."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "future_enhancement_readiness.json"
    csv_path = OUT_DIR / "future_enhancement_readiness.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerow({"metric": "future_enhancement_count", "value": planned})
        writer.writerow({"metric": "implemented_enhancement_count", "value": implemented})
        writer.writerow({"metric": "readiness_score", "value": readiness_score})
        for key, value in checks.items():
            writer.writerow({"metric": key, "value": value})
    print(json.dumps({"scorecard": str(json_path), "readiness_score": readiness_score}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
