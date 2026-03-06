"""OpenBB Quant ML Extension."""

from __future__ import annotations

import logging
import os

from openbb_quant_ml.config import validate_env


def _configure_structured_logging() -> None:
    """Configure structlog if available, otherwise keep stdlib logging."""
    try:
        import structlog
    except Exception:  # noqa: BLE001
        logging.basicConfig(level=logging.INFO)
        return

    is_dev = str(os.getenv("OPENBB_ENV", "dev")).strip().lower() in {
        "dev",
        "development",
        "local",
        "test",
    }
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            (
                structlog.dev.ConsoleRenderer()
                if is_dev
                else structlog.processors.JSONRenderer()
            ),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


validate_env()
_configure_structured_logging()

from openbb_quant_ml.quant_ml_router import router  # noqa: E402

__all__ = ["router"]
