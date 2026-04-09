from __future__ import annotations

import logging
import os
from pathlib import Path

from helpers.runtime import configure_logging


configure_logging()
LOGGER = logging.getLogger(__name__)


def ensure_automorph_data() -> Path | None:
    data_path = os.getenv("AUTOMORPH_DATA")
    if not data_path:
        return None

    root = Path(data_path)
    LOGGER.info("Set %s as AutoMorph output directory", root)
    (root / "images").mkdir(parents=True, exist_ok=True)
    (root / "Results").mkdir(exist_ok=True)
    return root


def main() -> int:
    ensure_automorph_data()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
