"""Tests for the Nasdaq options models."""

import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.options_chains import (
    NasdaqOptionsChainsFetcher,
    _contract_symbol,
    _expiration,
    _front_expiration,
    _greeks_by_contract,
    _strikes_for,
    _underlying_price,
)

from .conftest import patch_asset_class, patch_data

DRILL_URL = (
    "/market-activity/stocks/aapl/option-chain/call-put-options/aapl--260807c00187500"
)
LATER_DRILL_URL = (
    "/market-activity/stocks/aapl/option-chain/call-put-options/aapl--260814c00200000"
)

EXPIRATION = date(2026, 8, 7)
LATER_EXPIRATION = date(2026, 8, 14)


def chain_payload():
    """Return a one-strike chain payload."""
    return {
        "lastTrade": "AAPL $333.02 +11.36 (+3.53%)",
        "table": {
            "rows": [
                {
                    "strike": "187.50",
                    "drillDownURL": DRILL_URL,
                    "c_Last": "150.00",
                    "c_Change": "1.00",
                    "c_Bid": "149.00",
                    "c_Ask": "151.00",
                    "c_Volume": "10",
                    "c_Openinterest": "100",
                    "p_Last": "1.00",
                    "p_Bid": "0.90",
                    "p_Ask": "1.10",
                    "p_Volume": "5",
                    "p_Openinterest": "50",
                },
                {"strike": "N/A", "drillDownURL": DRILL_URL},
            ]
        },
    }


def two_expiration_chain_payload():
    """Return a chain payload spanning a front and a later expiration."""
    payload = chain_payload()
    payload["table"]["rows"].append(
        {
            "strike": "200.00",
            "drillDownURL": LATER_DRILL_URL,
            "c_Last": "160.00",
            "c_Bid": "159.00",
            "c_Ask": "161.00",
            "c_Volume": "3",
            "c_Openinterest": "40",
            "p_Last": "2.00",
            "p_Bid": "1.90",
            "p_Ask": "2.10",
            "p_Volume": "2",
            "p_Openinterest": "20",
        }
    )

    return payload


class TestChainHelpers:
    """Cover the chain parsing helpers."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("AAPL $333.02 +11.36", 333.02),
            ("AAPL $1,234.50", 1234.5),
            ("no price", None),
            ("", None),
        ],
    )
    def test_underlying_price(self, value, expected):
        """The banner price is parsed when present."""
        assert _underlying_price(value) == expected

    def test_contract_symbol(self):
        """The drill-down URL becomes an OCC symbol for either side."""
        assert _contract_symbol(DRILL_URL, "call") == "AAPL260807C00187500"
        assert _contract_symbol(DRILL_URL, "put") == "AAPL260807P00187500"

    @pytest.mark.parametrize("url", [None, 42, "/no-separator", "/a--short"])
    def test_contract_symbol_rejects_bad_urls(self, url):
        """Anything that is not a contract URL yields nothing."""
        assert _contract_symbol(url, "call") is None

    def test_expiration(self):
        """The expiration is read out of the contract symbol."""
        assert _expiration("AAPL260807C00187500") == EXPIRATION

    @pytest.mark.parametrize(
        "contract",
        [
            None,
            "SHORT",
            "AAPLXXXXXXC00187500",
            "AAPL999999C00187500",
            "AAPLXXXXXXXXXXX",
        ],
    )
    def test_expiration_rejects_bad_symbols(self, contract):
        """An unparseable symbol yields no expiration."""
        assert _expiration(contract) is None

    def test_greeks_by_contract(self):
        """The greeks table is indexed by expiration, strike, and side."""
        indexed = _greeks_by_contract(
            {
                "table": {
                    "rows": [
                        {
                            "strike": "187.50",
                            "url": DRILL_URL,
                            "cDelta": "0.55",
                            "cGamma": "0.01",
                            "cIV": "0.30",
                            "pDelta": "-0.45",
                        },
                        {"strike": "N/A", "url": DRILL_URL},
                        {"strike": "1", "url": "no-contract"},
                    ]
                }
            }
        )

        assert indexed[(EXPIRATION, 187.5, "call")]["delta"] == pytest.approx(0.55)
        assert indexed[(EXPIRATION, 187.5, "put")]["delta"] == pytest.approx(-0.45)
        assert len(indexed) == 2

    def test_greeks_accepts_the_capitalised_column(self):
        """Either strike column naming is read."""
        indexed = _greeks_by_contract(
            {"table": {"rows": [{"Strike": "187.50", "url": DRILL_URL}]}}
        )

        assert (EXPIRATION, 187.5, "call") in indexed

    def test_strikes_for(self):
        """Every unique expiration and strike pair is listed."""
        pairs = _strikes_for(chain_payload(), set())

        assert pairs == [(EXPIRATION, 187.5)]

    def test_strikes_for_filters_expirations(self):
        """A requested expiration narrows the fan-out."""
        assert _strikes_for(chain_payload(), {date(2030, 1, 1)}) == []

    def test_front_expiration(self):
        """The nearest expiration in the chain is returned."""
        assert _front_expiration(two_expiration_chain_payload()) == EXPIRATION

    def test_front_expiration_with_no_parseable_rows(self):
        """A chain with no readable contracts has no front expiration."""
        assert _front_expiration({"table": {"rows": [{"drillDownURL": None}]}}) is None


class TestOptionsChains:
    """Cover the options chain model."""

    def test_merges_chain_greeks_and_detail(self, monkeypatch):
        """The chain, greeks, and per-strike detail are merged per contract."""
        patch_asset_class(monkeypatch, "stocks")

        async def _data(path, **kwargs):
            if "greeks" in path:
                return {
                    "table": {
                        "rows": [
                            {"strike": "187.50", "url": DRILL_URL, "cDelta": "0.55"}
                        ]
                    }
                }

            return chain_payload()

        async def _detail(symbol, expiration, strike, asset_class):
            return {"call": {"open": 149.5, "tick": "up"}}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "aapl"})
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))
        annotated = NasdaqOptionsChainsFetcher.transform_data(query, raw)
        result = annotated.result

        assert annotated.metadata["underlying_price"] == pytest.approx(333.02)
        assert result.contract_symbol == [
            "AAPL260807C00187500",
            "AAPL260807P00187500",
        ]
        assert result.delta[0] == pytest.approx(0.55)
        assert result.open[0] == pytest.approx(149.5)
        assert result.tick[0] == "up"
        assert result.open[1] is None

    def test_requested_expiration_narrows_the_window(self, monkeypatch):
        """A requested expiration bounds the chain request."""
        seen: list[str] = []
        patch_asset_class(monkeypatch, "stocks")
        patch_data(monkeypatch, chain_payload(), seen)

        async def _detail(symbol, expiration, strike, asset_class):
            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        query = NasdaqOptionsChainsFetcher.transform_query(
            {"symbol": "AAPL", "expiration": "2026-08-07"}
        )
        asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert "fromdate=2026-08-07" in seen[0]
        assert "todate=2026-08-07" in seen[0]

    def test_unnarrowed_fanout_is_bound_to_the_front_expiration(self, monkeypatch):
        """Without a requested expiration, only the nearest one is fanned out."""
        patch_asset_class(monkeypatch, "stocks")
        patch_data(monkeypatch, two_expiration_chain_payload())
        detailed: list = []

        async def _detail(symbol, expiration, strike, asset_class):
            detailed.append((expiration, strike))

            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert detailed == [(EXPIRATION, 187.5)]
        annotated = NasdaqOptionsChainsFetcher.transform_data(query, raw)

        assert sorted(set(annotated.result.expiration)) == [
            EXPIRATION,
            LATER_EXPIRATION,
        ]

    def test_greeks_are_fetched_for_a_narrowed_non_front_expiration(self, monkeypatch):
        """Greeks are readable for whichever expiration is actually requested."""
        patch_asset_class(monkeypatch, "stocks")
        seen: list[str] = []

        async def _data(path, **kwargs):
            seen.append(path)

            if "greeks" in path:
                return {
                    "table": {
                        "rows": [
                            {
                                "strike": "200.00",
                                "url": LATER_DRILL_URL,
                                "cDelta": "0.40",
                            }
                        ]
                    }
                }

            return two_expiration_chain_payload()

        async def _detail(symbol, expiration, strike, asset_class):
            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        query = NasdaqOptionsChainsFetcher.transform_query(
            {"symbol": "AAPL", "expiration": "2026-08-14"}
        )
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert any(f"date={LATER_EXPIRATION}" in path for path in seen)
        assert raw["greeks"][(LATER_EXPIRATION, 200.0, "call")][
            "delta"
        ] == pytest.approx(0.4)

    def test_retries_a_refused_strike(self, monkeypatch):
        """A refused strike is retried before it is given up on."""
        patch_asset_class(monkeypatch, "stocks")
        patch_data(monkeypatch, chain_payload())
        attempts: list[int] = []

        async def _detail(symbol, expiration, strike, asset_class):
            attempts.append(1)

            if len(attempts) < 2:
                raise OSError("refused")

            return {"call": {"open": 1.0}}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        monkeypatch.setattr("openbb_nasdaq.models.options_chains._RETRY_BACKOFF", 0)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert len(attempts) == 2
        assert raw["detail"][(EXPIRATION, 187.5, "call")]["open"] == 1.0

    def test_gives_up_after_the_attempt_limit(self, monkeypatch):
        """A strike that never answers is dropped rather than retried forever."""
        patch_asset_class(monkeypatch, "stocks")
        patch_data(monkeypatch, chain_payload())

        async def _detail(symbol, expiration, strike, asset_class):
            raise OSError("refused")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        monkeypatch.setattr("openbb_nasdaq.models.options_chains._RETRY_BACKOFF", 0)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert raw["detail"] == {}

    def test_missing_chain_raises(self, monkeypatch):
        """A symbol with no chain is reported."""
        patch_asset_class(monkeypatch, "stocks")
        patch_data(monkeypatch, None)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "NOPE"})

        with pytest.raises(EmptyDataError, match="No options chain"):
            asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

    def test_tolerates_a_failing_greeks_call(self, monkeypatch):
        """The chain is still returned when the greeks call fails."""
        patch_asset_class(monkeypatch, "stocks")

        async def _data(path, **kwargs):
            if "greeks" in path:
                raise OSError("refused")

            return chain_payload()

        async def _detail(symbol, expiration, strike, asset_class):
            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_contract_detail", _detail)
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})
        raw = asyncio.run(NasdaqOptionsChainsFetcher.aextract_data(query, None))

        assert raw["greeks"] == {}

    def test_no_priced_contracts_raises(self):
        """A chain whose rows carry no contracts is reported."""
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})

        with pytest.raises(EmptyDataError, match="No option contracts"):
            NasdaqOptionsChainsFetcher.transform_data(
                query,
                {
                    "symbol": "AAPL",
                    "chain": {"table": {"rows": []}},
                    "greeks": {},
                    "detail": {},
                    "expirations": set(),
                },
            )


class TestChainContractGuards:
    """Cover the guards the chain applies to unparseable rows."""

    def test_rows_without_a_contract_are_skipped(self):
        """A row whose drill-down URL carries no contract is dropped."""
        query = NasdaqOptionsChainsFetcher.transform_query({"symbol": "AAPL"})

        with pytest.raises(EmptyDataError, match="No option contracts"):
            NasdaqOptionsChainsFetcher.transform_data(
                query,
                {
                    "symbol": "AAPL",
                    "chain": {
                        "table": {"rows": [{"strike": "1.0", "drillDownURL": None}]}
                    },
                    "greeks": {},
                    "detail": {},
                    "expirations": set(),
                },
            )
