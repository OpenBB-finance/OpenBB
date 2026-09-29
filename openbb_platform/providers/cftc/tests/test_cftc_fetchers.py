from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_cftc.models.cot import CftcCotFetcher
from openbb_cftc.models.cot_search import CftcCotSearchFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.mark.record_http
def test_cftc_cot_fetcher(credentials=test_credentials):
    params = {
        "code": "239747",
        "start_date": date(2024, 8, 19),
        "end_date": date(2024, 8, 21),
    }

    fetcher = CftcCotFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_cftc_cot_sarch_fetcher(credentials=test_credentials):
    params = {"query": "S&P 500"}

    fetcher = CftcCotSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
