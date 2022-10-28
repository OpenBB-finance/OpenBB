# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.feedparser_model import get_news


@pytest.mark.vcr
@pytest.mark.parametrize(
    "term, sources",
    [
        ("", ""),
        ("Apple", ""),
        ("TSLA", "bloomberg"),
        ("Apple", "bloomberg,Reuters"),
        ("asdf$#", ""),
    ],
)
def test_get_news(term, sources, recorder):
    df = get_news(term=term, sources=sources)
    recorder.capture(df)
