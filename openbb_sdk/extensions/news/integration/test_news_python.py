"""Test news extension."""
import datetime

import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "params",
    [
        ({"limit": 20}),
        (
            {
                "display": "full",
                "date": datetime.date(2023, 1, 1),
                "start_date": datetime.date(2023, 1, 1),
                "end_date": datetime.date(2023, 6, 6),
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "Elon Musk",
                "authors": "Benzinga Insights",
                "content_types": "Car",
                "provider": "benzinga",
                "limit": 20,
            }
        ),
    ],
)
def test_news_globalnews(params):
    result = obb.news.globalnews(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
