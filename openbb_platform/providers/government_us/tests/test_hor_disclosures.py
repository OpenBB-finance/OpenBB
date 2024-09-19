"""Government US Fetchers tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_government_us.models.hor_disclosures import USHoRDisclosuresData, USHoRDisclosuresQueryParams, USHoRDisclosuresFetcher
import pandas as pd
test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }

@pytest.mark.record_http
def test_hor_disclosures_fetcher(mocker, credentials=test_credentials):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    params = {
        "year": 2024
    }

    def patched_docids(content):
        return [dict(doc_id='20024277',
                     membername='Allen Richard W.',
                     state='GA12',
                     filing_date='5/13/2024')]

    async def patched_transactions(client, year, discl_dict):
        return pd.DataFrame(data=[{'company': 'SP Albemarle Corporation ',
                                   'ticker': 'ALB',
                                   'action': ' S',
                                   'purchase_price': '$1,001 - $15,000',
                                   'transaction_date': '12/21/2023',
                                   'report_date': '01/08/2024',
                                   'doc_id': '20024277',
                                   'membername': 'Allen Richard W.',
                                   'state': 'GA12',
                                   'filing_date': '5/13/2024'}])

    mocker.patch('openbb_government_us.utils.hor_helpers.get_all_docids', patched_docids)
    mocker.patch('openbb_government_us.utils.hor_helpers.aread_pdf_from_url', patched_transactions)

    fetcher = USHoRDisclosuresFetcher()
    result = fetcher.test(params, credentials)

    assert result is None


