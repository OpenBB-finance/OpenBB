"""Unit tests for ``openbb_ecb.utils.series_keys``."""

from openbb_ecb.utils import series_keys


def test_frequency_map():
    """The frequency map exposes the SDMX codes."""
    assert series_keys.FREQUENCY_MAP["daily"] == "D"
    assert series_keys.FREQUENCY_MAP["annual"] == "A"
    assert series_keys.FREQUENCY_MAP["monthly"] == "M"


def test_exr_key():
    """EXR keys are built vs EUR (spot, average)."""
    assert series_keys.exr_key("usd", "D") == "D.USD.EUR.SP00.A"
    assert series_keys.exr_key("JPY", "M") == "M.JPY.EUR.SP00.A"


def test_fm_key():
    """FM key-rate codes map to the LEV level series."""
    assert series_keys.fm_key("DFR") == "B.U2.EUR.4F.KR.DFR.LEV"
    assert series_keys.FM_RATE_CODES == {
        "deposit": "DFR",
        "lending": "MLFR",
        "refinancing": "MRR_FR",
    }


def test_est_key():
    """The €STR key OR-joins every data type for one request."""
    key = series_keys.est_key()
    assert key.startswith("B.EU000A2X2A25.WT+")
    for code in series_keys.EST_DATA_TYPES:
        assert code in key


def test_mir_key():
    """Curated MIR series resolve to full keys."""
    assert series_keys.mir_key("corporate_loans") == "M.U2.B.A2A.A.R.A.2240.EUR.N"
    assert (
        series_keys.mir_key("household_loans_for_house_purchase", ref_area="DE")
        == "M.DE.B.A2C.A.R.A.2250.EUR.N"
    )
    assert len(series_keys.MIR_SERIES) == 14
