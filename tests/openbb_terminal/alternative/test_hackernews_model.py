# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.hackernews_model import get_stories


@pytest.mark.vcr
@pytest.mark.parametrize(
    "limit",
    [(5), (10)],
)
def test_get_stories(limit, recorder):
    df = get_stories(
        limit=limit,
    )
    recorder.capture(df)
