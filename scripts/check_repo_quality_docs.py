"""Check that repository quality docs exist."""

from pathlib import Path

REQUIRED_DOCS = [
        "docs/design-decisions.md",
        "docs/tradeoffs-and-simplifications.md",
        "docs/validation-log.md",
        "docs/lessons-learned.md",
        "docs/production-roadmap.md",
        "docs/repo-review-guide.md",
        "docs/screenshot-capture-checklist.md",
        "docs/interview-guide.md",
]


def main() -> int:
    """Validate required documentation files."""
    missing = [path for path in REQUIRED_DOCS if not Path(path).exists()]
    if missing:
        print("Missing required docs:")
        for path in missing:
            print(f"- {path}")
        return 1
    print(f"Repository quality docs present: {len(REQUIRED_DOCS)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
