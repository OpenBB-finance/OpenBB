"""Test the router system module."""

import asyncio
from unittest.mock import Mock, patch

from openbb_core.api.router.system import get_system_model
from openbb_core.app.model.system_settings import SystemSettings


@patch("openbb_core.api.router.system.get_system_settings")
def test_get_system_model(mock_get_system_settings):
    """Test get system model."""
    mock_system_settings = Mock(spec=SystemSettings)
    mock_get_system_settings.return_value = mock_system_settings

    response = asyncio.run(get_system_model(system_settings=mock_system_settings))

    assert response == mock_system_settings
