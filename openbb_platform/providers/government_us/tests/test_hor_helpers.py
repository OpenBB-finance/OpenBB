"""Government US Fetchers tests."""

import datetime

import pytest

from openbb_government_us.utils import hor_helpers
from PyPDF2 import PdfReader
import os
import pandas as pd

@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }

@pytest.mark.asyncio
@pytest.mark.record_http
async def test_get_transactions(mocker):
    """Test GovernmentUSTreasuryAuctionsFetcher."""
    def patched_docids(content):
        return [dict(doc_id = '20024277',
                            membername='Allen Richard W.',
                            state = 'GA12',
                            filing_date = '5/13/2024')]

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
    result = await hor_helpers.get_transactions(2024)
    print(result)
    assert result is not  None


