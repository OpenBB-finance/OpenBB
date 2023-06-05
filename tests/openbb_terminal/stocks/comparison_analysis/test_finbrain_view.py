# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.comparison_analysis import finbrain_view


@pytest.mark.default_cassette("test_display_sentiment_compare")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_display_sentiment_compare(raw):
    finbrain_view.display_sentiment_compare(
        similar=["TSLA", "GM"],
        raw=raw,
        export="",
        sheet_name=None,
    )


@pytest.mark.default_cassette("test_display_sentiment_correlation")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_display_sentiment_correlation(raw):
    finbrain_view.display_sentiment_correlation(
        similar=["TSLA", "GM"],
        raw=raw,
        export="",
        sheet_name=None,
    )
