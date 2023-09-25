"""Test news extension."""

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
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "updated_since": 900000,
                "published_since": 900000,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "car",
                "authors": "Benzinga Insights",
                "content_types": "Car",
                "provider": "benzinga",
                "limit": 20,
            }
        ),
    ],
)
def test_news_globalnews(params):
    result = obb.news.globalnews(**params)
    assert result
    assert isinstance(result, OBBject)
