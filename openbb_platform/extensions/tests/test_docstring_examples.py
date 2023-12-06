"""Test utils."""
import pytest

from extensions.tests.utils.helpers import check_docstring_examples


@pytest.mark.integration
def test_docstring_examples():
    """Test that the docstring examples execute without errors."""
    errors = check_docstring_examples()
    assert not errors, "\n".join(errors)
