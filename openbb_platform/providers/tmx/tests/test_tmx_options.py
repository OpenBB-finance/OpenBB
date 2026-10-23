"""Tests for the options chain transform."""

from openbb_tmx.models.options_chains import TICK_MAP, _flatten_chain

RESULTS = {
    "expiryGroup": [
        {
            "expirydate": "2026-07-31",
            "callputgroup": [
                {
                    "quote": [
                        {
                            "contract": {
                                "expirydate": "2026-07-31",
                                "callput": "Put",
                                "strike": 18.5,
                                "type": "WEEK",
                                "openinterest": 43,
                            },
                            "pricedata": {
                                "last": 0.05,
                                "bid": 0.01,
                                "ask": 0.05,
                                "bidsize": 0,
                                "asksize": 22,
                                "contractvolume": 2,
                                "tick": -1,
                            },
                            "greeks": {
                                "impvol": 0.885,
                                "delta": -0.026,
                                "gamma": 0.021,
                                "theta": -0.012,
                                "vega": 0.002,
                                "rho": -0.0001,
                            },
                            "key": {"symbol": ["@AC    260731P00018500:CA"]},
                        }
                    ]
                }
            ],
        }
    ]
}


class TestFlattenChain:
    """Flattening the vendor chain into columnar lists."""

    def test_returns_columnar_lists(self):
        flat = _flatten_chain(RESULTS, "AC")
        assert len(flat["contract_symbol"]) == 1
        assert flat["strike"] == [18.5]

    def test_greeks_are_carried(self):
        flat = _flatten_chain(RESULTS, "AC")
        for field in ("implied_volatility", "delta", "gamma", "theta", "vega", "rho"):
            assert flat[field][0] is not None

    def test_option_type_is_lowercased(self):
        assert _flatten_chain(RESULTS, "AC")["option_type"] == ["put"]

    def test_tick_is_mapped_to_a_word(self):
        assert _flatten_chain(RESULTS, "AC")["tick"] == ["down"]

    def test_dte_is_computed(self):
        assert isinstance(_flatten_chain(RESULTS, "AC")["dte"][0], int)

    def test_underlying_symbol_is_suffixed(self):
        assert _flatten_chain(RESULTS, "AC")["underlying_symbol"] == ["AC:CA"]

    def test_empty_chain(self):
        assert _flatten_chain({"expiryGroup": []}, "AC") == {}

    def test_contract_without_expiry_is_skipped(self):
        broken = {"expiryGroup": [{"callputgroup": [{"quote": [{"contract": {}}]}]}]}
        assert _flatten_chain(broken, "AC") == {}

    def test_tick_map(self):
        assert TICK_MAP == {1: "up", -1: "down", 0: "unchanged"}
