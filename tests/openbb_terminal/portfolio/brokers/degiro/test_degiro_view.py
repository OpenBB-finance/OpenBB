# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.portfolio.brokers.degiro.degiro_view import DegiroView


# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("cookie", None),
        ],
        "filter_query_parameters": [
            ("intAccount", "MOCK_INT_ACCOUNT"),
            ("sessionId", "MOCK_SESSION_ID"),
        ],
        "filter_post_data_parameters": [
            ("username", "MOCK_USERNAME"),
            ("password", "MOCK_PASSWORD"),
            ("oneTimePassword", "MOCK_ONE_TIME_PASSWORD"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_help_display():
    DegiroView.help_display()
