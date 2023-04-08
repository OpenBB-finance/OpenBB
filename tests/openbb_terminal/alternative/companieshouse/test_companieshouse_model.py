import ssl

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.companieshouse import companieshouse_model

ssl._create_default_https_context = (  # pylint: disable=protected-access
    ssl._create_unverified_context  # pylint: disable=protected-access
)


@pytest.mark.record_http
def test_get_search_results():
    assert len(companieshouse_model.get_search_results("shell oil", 10)) > 0


@pytest.mark.record_http
def test_get_company_info():
    assert len(companieshouse_model.get_company_info("03625633")) > 0


@pytest.mark.record_http
def test_get_officers():
    assert len(companieshouse_model.get_officers("03625633")) > 0


@pytest.mark.record_http
def test_get_persons_with_significant_control():
    assert len(companieshouse_model.get_persons_with_significant_control("03625633")) > 0


@pytest.mark.record_http
def test_get_filings():
    assert len(companieshouse_model.get_filings("03625633")) > 0