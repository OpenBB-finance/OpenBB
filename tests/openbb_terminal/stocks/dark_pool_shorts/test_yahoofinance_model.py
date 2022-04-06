# IMPORTATION STANDARD
import gzip

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import yahoofinance_model


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
def test_get_most_shorted(recorder):
    data_df = yahoofinance_model.get_most_shorted()
    recorder.capture(data_df)
