# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import seeking_alpha_view


@pytest.mark.vcr
# @pytest.mark.record_stdout # deactivated, because assertion doesn't make sense if data changes
def test_display_eps_estimation():
    seeking_alpha_view.display_eps_estimates(symbol="JNJ")


@pytest.mark.vcr
def test_display_rev_estimation():
    seeking_alpha_view.display_rev_estimates(symbol="JNJ")
