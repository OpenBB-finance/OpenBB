# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import finbrain_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_technical_summary_report():
    finbrain_view.technical_summary_report(ticker="PM")
