# IMPORTATION STANDARD
import gzip

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_view


def filter_table_only(response):
    """To reduce cassette size."""

    content_html = gzip.decompress(response["body"]["string"]).decode()
    if content_html.startswith("<table"):
        pass
    else:
        df = pd.read_html(content_html)[0]
        response["body"]["string"] = gzip.compress(df.to_html(index=False).encode())
    return response


@pytest.mark.vcr(before_record_response=filter_table_only)
@pytest.mark.record_stdout
def test_display_most_shorted():
    yahoofinance_view.display_most_shorted(num_stocks=2, export="")
