import pytest

from generate_sdk import generate_sdk


@pytest.mark.timeout(120)
def test_sdk_generation():
    """Test the sdk markdown generator"""
    assert generate_sdk() is True
