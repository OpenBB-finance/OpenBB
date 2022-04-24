# IMPORTATION STANDARD
# import gzip

# IMPORTATION THIRDPARTY
# import pandas as pd

# import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import investingcom_view


# @pytest.mark.vcr
# @pytest.mark.record_stdout
def test_display_yieldcurve():
    investingcom_view.display_yieldcurve(country="portugal", export="")
