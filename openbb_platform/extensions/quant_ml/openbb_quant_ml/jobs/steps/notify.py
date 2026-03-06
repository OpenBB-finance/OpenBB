"""Step: notification dispatch compatibility wrapper."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.notification_center import dispatch_job_notification


def run(config: dict[str, Any]) -> dict[str, Any]:
    """Dispatch job notifications through the central outbox service."""
    return dispatch_job_notification(config)
