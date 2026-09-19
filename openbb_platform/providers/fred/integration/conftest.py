"""Shared configuration for the FRED integration tests."""

import pytest


def pytest_collection_modifyitems(items):
    """Let the integration tests reach the network the unit suite forbids."""
    for item in items:
        item.add_marker(pytest.mark.enable_socket)
