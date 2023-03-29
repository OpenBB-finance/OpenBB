# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import finra_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_plot_dark_pools():
    finra_view.darkpool_ats_otc(
        symbol="RIVN",
        export="",
        sheet_name=None,
    )


def filter_test_darkpool_otc(response):
    content = gzip.decompress(response["body"]["string"]).decode()
    content_json = json.loads(content)
    if len(content_json) > 10:
        new_content = json.dumps(content_json[:10])
        response["body"]["string"] = gzip.compress(new_content.encode())
    return response


@pytest.mark.vcr(before_record_response=filter_test_darkpool_otc)
@pytest.mark.record_stdout
def test_darkpool_otc():
    finra_view.darkpool_otc(
        input_limit=2,
        limit=2,
        tier="T1",
        export="",
        sheet_name=None,
    )
