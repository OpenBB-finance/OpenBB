"""Tests for the MCP server extension."""

import sys

import pytest

# Skip all tests if Python version < 3.10
if sys.version_info < (3, 10):
    pytest.skip("MCP server requires Python 3.10+", allow_module_level=True)
