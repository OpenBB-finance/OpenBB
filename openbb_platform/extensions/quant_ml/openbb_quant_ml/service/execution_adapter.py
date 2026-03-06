"""Broker-ready execution adapter interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BrokerExecutionAdapter(ABC):
    """Abstract live execution adapter."""

    @abstractmethod
    def submit_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Submit one batch of normalized orders to a broker."""


class DisabledLiveAdapter(BrokerExecutionAdapter):
    """Default live adapter that intentionally blocks execution."""

    def submit_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        raise RuntimeError(
            "Live adapter is disabled in this environment. Orders were not routed."
        )
