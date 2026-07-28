"""Tests for ``openbb_quantitative.helpers``."""

import io
import zipfile

import pandas as pd
import pytest

from openbb_quantitative.helpers import get_fama_raw, validate_window

_FAMA_CSV = (
    "Fama/French factors -- test fixture\n"
    "second descriptive line\n"
    "third descriptive line\n"
    ",Mkt-RF,SMB,HML,RF\n"
    "202201,1.00,0.50,0.30,0.01\n"
    "202202,-0.50,0.20,0.10,0.01\n"
    "202203,0.75,-0.10,0.05,0.01\n"
    "\n"
    " Annual Factors: January-December \n"
    "2022,5.00,2.00,1.00,0.12\n"
)


def _fama_zip_bytes() -> bytes:
    """Build an in-memory Fama-French factors zip archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("F-F_Research_Data_Factors.csv", _FAMA_CSV)
    return buffer.getvalue()


class _FakeResponse:
    """Minimal stand-in for the urlopen response context manager."""

    def __init__(self, payload: bytes):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self._payload


@pytest.fixture
def mock_fama(monkeypatch):
    """Patch urlopen so get_fama_raw reads the in-memory archive, not the web."""
    payload = _fama_zip_bytes()
    monkeypatch.setattr("urllib.request.urlopen", lambda url: _FakeResponse(payload))


def test_get_fama_raw(mock_fama):
    """get_fama_raw parses the factor archive into a date-indexed DataFrame."""
    df = get_fama_raw("2022-01-01", "2022-12-31")
    assert list(df.columns) == ["mkt_rf", "smb", "hml", "rf"]
    assert df.index.name == "date"
    # Only the three monthly rows survive the six-character-date filter.
    assert len(df) == 3
    # Percent figures are converted to decimal fractions.
    assert df["mkt_rf"].iloc[0] == pytest.approx(0.01)


def test_get_fama_raw_start_date_too_late(mock_fama):
    """A start date after the last observation raises a ValueError."""
    with pytest.raises(ValueError, match="after the last available"):
        get_fama_raw("2099-01-01", "2099-12-31")


def test_validate_window_within_bounds():
    """validate_window accepts a window no larger than the data."""
    validate_window(pd.Series(range(100)), 20)


def test_validate_window_too_large():
    """validate_window raises when the window exceeds the data length."""
    with pytest.raises(ValueError, match="larger than the data length"):
        validate_window(pd.Series(range(10)), 50)
