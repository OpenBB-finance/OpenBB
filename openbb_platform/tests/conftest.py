"""Configuration for pytest."""

# TODO: See if we can dynamically import the test modules under the openbb_platform

# TODO: Add global fixture for headers here

import os


def pytest_configure():
    """Set environment variables for testing."""
    os.environ["OPENBB_AUTO_BUILD"] = "false"
