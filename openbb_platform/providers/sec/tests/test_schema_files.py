"""Unit tests for ``openbb_sec.models.schema_files``."""

from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models.schema_files import (
    SecSchemaFilesFetcher,
    SecSchemaFilesQueryParams,
)


def test_schema_files_query_component_requires_taxonomy():
    """schema_files.py:99 -> component without taxonomy raises ValueError."""
    with pytest.raises(ValueError) as exc:
        SecSchemaFilesQueryParams(component="StatementOfIncome")
    assert "'component' requires 'taxonomy'" in str(exc.value)


class _FakeManagerNoYears:
    """XBRLManager double whose taxonomy has no available years."""

    def get_available_years(self, taxonomy):  # noqa: ARG002
        return []


def test_schema_files_extract_no_years():
    """schema_files.py:264 -> raise OpenBBError when taxonomy has no years."""
    query = SecSchemaFilesQueryParams(taxonomy="us-gaap")
    with patch(
        "openbb_sec.utils.xbrl_taxonomy_helper.XBRLManager", _FakeManagerNoYears
    ):
        with pytest.raises(OpenBBError) as exc:
            SecSchemaFilesFetcher.extract_data(query, None)
    assert "No years found" in str(exc.value)


class _FakeManagerYearMismatch:
    """XBRLManager double where the requested year isn't available."""

    def get_available_years(self, taxonomy):  # noqa: ARG002
        return [2020, 2021]


def test_schema_files_extract_year_not_available():
    """schema_files.py:270 -> raise OpenBBError when year not in available years."""
    query = SecSchemaFilesQueryParams(taxonomy="us-gaap", year=1999)
    with patch(
        "openbb_sec.utils.xbrl_taxonomy_helper.XBRLManager", _FakeManagerYearMismatch
    ):
        with pytest.raises(OpenBBError) as exc:
            SecSchemaFilesFetcher.extract_data(query, None)
    assert "not available for taxonomy" in str(exc.value)


class _FakeManagerNoComponents:
    """XBRLManager double with a valid year but no components."""

    def get_available_years(self, taxonomy):  # noqa: ARG002
        return [2021]

    def list_available_components(self, taxonomy, year):  # noqa: ARG002
        return []


def test_schema_files_extract_no_components():
    """schema_files.py:281 -> raise OpenBBError when no components found."""
    query = SecSchemaFilesQueryParams(taxonomy="us-gaap")
    with patch(
        "openbb_sec.utils.xbrl_taxonomy_helper.XBRLManager", _FakeManagerNoComponents
    ):
        with pytest.raises(OpenBBError) as exc:
            SecSchemaFilesFetcher.extract_data(query, None)
    assert "No components found" in str(exc.value)
