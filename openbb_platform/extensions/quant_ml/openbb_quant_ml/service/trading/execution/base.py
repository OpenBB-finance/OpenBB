"""Execution engine contracts for the trading runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExecutionEngine(ABC):
    """Base execution engine interface."""

    @abstractmethod
    def submit_order(self, order: dict[str, Any], latest_bar: dict[str, Any]) -> dict[str, Any]:
        """Submit one order and return order/fill payload."""

    @abstractmethod
    def cancel_order(self, order: dict[str, Any]) -> dict[str, Any]:
        """Cancel one order."""

    @abstractmethod
    def get_order_status(self, order: dict[str, Any]) -> dict[str, Any]:
        """Return order status snapshot."""

    @abstractmethod
    def get_positions(self) -> list[dict[str, Any]]:
        """Return current execution-layer positions."""

    @abstractmethod
    def get_account_state(self) -> dict[str, Any]:
        """Return current account state."""
