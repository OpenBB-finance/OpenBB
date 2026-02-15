"""Step: notification placeholder."""

from __future__ import annotations

from typing import Any


def run(config: dict[str, Any]) -> dict[str, Any]:
    # Hook for Slack/Discord/email integrations.
    return {"status": "ok", "message": "notification step completed"}
