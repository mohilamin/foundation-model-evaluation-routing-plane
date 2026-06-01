"""Generate all demo assets."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.routing_plane_core import run_pipeline  # noqa: E402

if __name__ == "__main__":
    print(run_pipeline())
