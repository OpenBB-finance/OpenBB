"""Tests for the Deribit options valuation and ranking."""

import pytest

from openbb_deribit.utils.options import chain, legs, optimizer, strategies


class TestValuation:
    """The valuation core prices a contract and inverts its own prices."""

    def test_intrinsic(self):
        """A contract is worth what exercising it would pay."""
        assert legs.intrinsic(110, 100, "call") == 10
        assert legs.intrinsic(90, 100, "call") == 0
        assert legs.intrinsic(90, 100, "put") == 10
        assert legs.intrinsic(110, 100, "put") == 0

    def test_put_call_parity(self):
        """A call less a put is the forward less the strike."""
        call = legs.option_value(100, 95, 0.5, 0.6, 1.0, "call")
        put = legs.option_value(100, 95, 0.5, 0.6, 1.0, "put")

        assert call - put == pytest.approx(100 - 95)

    def test_value_without_time_is_intrinsic(self):
        """A contract at expiration is worth exactly its exercise value."""
        assert legs.option_value(110, 100, 0, 0.6, 1.0, "call") == 10

    def test_implied_volatility_round_trips(self):
        """A price made at one volatility implies that volatility back."""
        price = legs.option_value(100, 100, 0.25, 0.42, 1.0, "call")

        assert legs.implied_vol(price, 100, 100, 0.25, 1.0, "call") == pytest.approx(
            0.42, abs=1e-4
        )

    @pytest.mark.parametrize(
        "price,forward,years",
        [(0, 100, 0.25), (5, 100, 0), (5, 0, 0.25)],
    )
    def test_implied_volatility_needs_a_real_quote(self, price, forward, years):
        """A quote that cannot come from any volatility implies none."""
        assert legs.implied_vol(price, forward, 100, years, 1.0, "call") is None

    def test_a_price_below_intrinsic_implies_nothing(self):
        """No volatility prices a contract under its exercise value."""
        assert legs.implied_vol(1.0, 120, 100, 0.25, 1.0, "call") is None

    def test_a_price_above_the_search_implies_nothing(self):
        """A quote beyond the highest volatility searched implies none."""
        assert legs.implied_vol(99.0, 100, 100, 0.25, 1.0, "call") is None


class TestPayoff:
    """A position's profit is measured in what it settles in."""

    @staticmethod
    def _call(price=5.0, dte=0):
        """Return one long call leg."""
        return [
            {
                "strike": 100.0,
                "option_type": "call",
                "quantity": 1,
                "size": 1,
                "price": price,
                "dte": dte,
                "implied_volatility": None,
            }
        ]

    def test_linear_payoff(self):
        """A linear contract pays the exercise value less the premium."""
        assert legs.payoff(self._call(), [90, 100, 110]) == [-5.0, -5.0, 5.0]

    def test_an_inverse_premium_costs_what_the_coin_is_worth(self):
        """The premium is coin, so holding through a rise costs more.

        Below the price it was opened at the coin paid is worth less, above it
        more, which is why an inverse loss is not flat.
        """
        below, entry, above = legs.payoff(
            self._call(), [50, 100, 200], inverse=True, entry_price=100
        )

        assert entry == pytest.approx(-5.0)
        assert below == pytest.approx(-2.5)
        assert above == pytest.approx(100 - 10.0)

    def test_an_inverse_payout_is_already_quoted(self):
        """Only the premium is carried; what the contract pays is not."""
        value = legs.payoff(self._call(), [150], inverse=True, entry_price=100)[0]

        assert value == pytest.approx(50 - 5.0 * 1.5)

    def test_an_inverse_position_needs_its_entry_price(self):
        """Valuing an inverse position without its entry is refused."""
        with pytest.raises(ValueError, match="paid in the coin"):
            legs.payoff(self._call(), [100], inverse=True)

    def test_a_worthless_underlying_costs_nothing_to_have_paid(self):
        """The coin the premium was paid in is itself worth nothing there."""
        assert legs.payoff(self._call(), [0], inverse=True, entry_price=100) == [0.0]

    def test_time_left_is_valued_not_exercised(self):
        """A leg outliving the valuation date keeps its time value."""
        held = self._call(dte=30)
        held[0]["implied_volatility"] = 0.6

        assert legs.payoff(held, [100], elapsed=0)[0] > -5.0

    def test_net_cost_of_a_credit_is_negative(self):
        """A position taken in is a credit."""
        sold = self._call()
        sold[0]["quantity"] = -1

        assert legs.net_cost(sold) == -5.0

    def test_breakevens(self):
        """Every crossing of zero is reported."""
        crossings = legs.breakevens([0, 1, 2, 3], [-1.0, 1.0, 1.0, -1.0])

        assert crossings == pytest.approx([0.5, 2.5])

    def test_no_crossing_is_no_breakeven(self):
        """A payoff that never crosses zero has no breakeven."""
        assert legs.breakevens([0, 1], [1.0, 2.0]) == []


class TestGreeks:
    """A contract with nothing left to model carries no greeks."""

    def test_a_live_contract_carries_every_greek(self):
        """A contract with time and volatility is fully described."""
        from openbb_deribit.utils.options.greeks import greeks

        modelled = greeks(100.0, 100.0, 0.25, 0.5, "call")

        assert set(modelled) == {"delta", "gamma", "theta", "vega", "rho"}
        assert all(value is not None for value in modelled.values())
        assert 0 < modelled["delta"] < 1
        assert modelled["theta"] < 0
        assert modelled["vega"] > 0

    def test_a_put_is_the_mirror_of_its_call(self):
        """A call and a put on one strike differ by exactly one in delta."""
        from openbb_deribit.utils.options.greeks import greeks

        call = greeks(100.0, 95.0, 0.5, 0.4, "call")
        put = greeks(100.0, 95.0, 0.5, 0.4, "put")

        assert call["delta"] - put["delta"] == pytest.approx(1.0)
        assert call["gamma"] == pytest.approx(put["gamma"])
        assert call["vega"] == pytest.approx(put["vega"])

    @pytest.mark.parametrize(
        "forward,strike,years,sigma",
        [(100.0, 100.0, 0, 0.5), (100.0, 100.0, 0.25, 0), (0, 100.0, 0.25, 0.5)],
    )
    def test_nothing_to_model_carries_nothing(self, forward, strike, years, sigma):
        """An expired or unquoted contract reports no greeks rather than zeros."""
        from openbb_deribit.utils.options.greeks import greeks

        modelled = greeks(forward, strike, years, sigma, "call")

        assert all(value is None for value in modelled.values())


class TestChain:
    """The chain exposes what the analysis needs from it."""

    def test_reads_its_own_shape(self, chain_frame):
        """Spot, settlement, and expirations come off the frame."""
        frame = chain_frame(inverse=True, spot=100.0)

        assert chain.underlying_price(frame) == 100.0
        assert chain.is_inverse(frame) is True
        assert chain.settlement_currency(frame, "BTC") == "BTC"
        assert len(chain.expirations(frame)) == 2

    def test_a_linear_chain_settles_in_the_quote(self, chain_frame):
        """A linear contract pays out in what it is quoted in."""
        frame = chain_frame(inverse=False, spot=1.5, size=1000)

        assert chain.is_inverse(frame) is False
        assert chain.settlement_currency(frame, "XRP_USDC") == "USDC"

    def test_an_empty_spot_reads_as_zero(self, chain_frame):
        """A chain with no published spot reports none rather than guessing."""
        frame = chain_frame()
        frame["underlying_spot_price"] = None

        assert chain.underlying_price(frame) == 0.0

    def test_nearest_expiration(self, chain_frame):
        """The listed expiration closest to a date is the one chosen."""
        frame = chain_frame()
        listed = chain.expirations(frame)

        assert chain.nearest_expiration(frame, listed[0]) == listed[0]
        assert chain.nearest_expiration(frame, "2099-01-01") == listed[-1]

    def test_quotes_carry_an_entry_and_an_exit(self, chain_frame):
        """Each contract is entered at the offer and left at the bid."""
        frame = chain_frame()
        quotes = chain.quotes_at(frame, chain.expirations(frame)[0])

        assert (quotes["entry"] >= quotes["exit"]).all()
        assert (quotes["entry"] > 0).all()

    def test_unquoted_contracts_are_left_out(self, chain_frame):
        """A contract nobody priced cannot be entered."""
        frame = chain_frame()
        frame.loc[frame.index[0], ["ask", "mark"]] = 0
        quotes = chain.quotes_at(frame, chain.expirations(frame)[0])

        assert (
            len(quotes)
            == len(frame[frame["expiration"] == chain.expirations(frame)[0]]) - 1
        )


def _leg(kind, strike, quantity, dte=30, price=1.0):
    """Return one unit leg of a position."""
    return {
        "symbol": f"TEST-{dte}-{strike:g}-{kind[0].upper()}",
        "expiration": str(dte),
        "strike": float(strike),
        "option_type": "call" if kind == "c" else "put",
        "quantity": quantity,
        "size": 1.0,
        "price": price,
        "dte": dte,
        "implied_volatility": 0.5,
    }


class TestClassify:
    """A position reads back as the Deribit combo it is, and the side taken."""

    @pytest.mark.parametrize(
        "legs,expected",
        [
            ([("c", 100, 1)], ("C", 1)),
            ([("p", 100, -1)], ("P", -1)),
            ([("c", 100, 1), ("c", 104, -1)], ("CS", 1)),
            ([("c", 100, -1), ("c", 104, 1)], ("CS", -1)),
            ([("p", 104, 1), ("p", 100, -1)], ("PS", 1)),
            ([("p", 104, -1), ("p", 100, 1)], ("PS", -1)),
            ([("c", 100, 1), ("c", 104, -2)], ("CSR12", 1)),
            ([("c", 100, -1), ("c", 104, 2)], ("CSR12", -1)),
            ([("p", 104, 1), ("p", 100, -2)], ("PSR12", 1)),
            ([("p", 104, -1), ("p", 100, 2)], ("PSR12", -1)),
            ([("c", 100, 1), ("c", 104, 1)], ("", 1)),
            ([("c", 100, 1), ("c", 100, -1)], ("", 1)),
            ([("c", 100, 1), ("c", 104, -3)], ("", 1)),
            ([("c", 100, 1), ("p", 100, 1)], ("STRD", 1)),
            ([("c", 100, -1), ("p", 100, -1)], ("STRD", -1)),
            ([("c", 100, 1), ("p", 100, -1)], ("REV", 1)),
            ([("c", 100, -1), ("p", 100, 1)], ("REV", -1)),
            ([("p", 96, 1), ("c", 104, 1)], ("STRG", 1)),
            ([("p", 96, -1), ("c", 104, -1)], ("STRG", -1)),
            ([("p", 96, 1), ("c", 104, -1)], ("RR", 1)),
            ([("p", 96, -1), ("c", 104, 1)], ("RR", -1)),
            ([("p", 104, 1), ("c", 96, 1)], ("", 1)),
            ([("c", 100, 2), ("p", 100, 1)], ("", 1)),
            ([("c", 96, 1), ("c", 100, -2), ("c", 104, 1)], ("CBUT", 1)),
            ([("c", 96, -1), ("c", 100, 2), ("c", 104, -1)], ("CBUT", -1)),
            ([("p", 96, 1), ("p", 100, -2), ("p", 104, 1)], ("PBUT", 1)),
            ([("c", 96, 1), ("c", 100, -2), ("c", 106, 1)], ("", 1)),
            ([("c", 96, 1), ("p", 100, -2), ("c", 104, 1)], ("", 1)),
            (
                [("c", 96, 1), ("c", 100, -1), ("c", 104, -1), ("c", 108, 1)],
                ("CCOND", 1),
            ),
            (
                [("p", 96, -1), ("p", 100, 1), ("p", 104, 1), ("p", 108, -1)],
                ("PCOND", -1),
            ),
            (
                [("c", 96, 1), ("c", 100, -1), ("c", 104, 1), ("c", 108, -1)],
                ("", 1),
            ),
            (
                [("p", 96, 1), ("p", 100, -1), ("c", 104, -1), ("c", 108, 1)],
                ("ICOND", 1),
            ),
            (
                [("p", 96, -1), ("p", 100, 1), ("c", 104, 1), ("c", 108, -1)],
                ("ICOND", -1),
            ),
            (
                [("p", 96, 1), ("p", 100, -1), ("c", 100, -1), ("c", 104, 1)],
                ("IBUT", 1),
            ),
            (
                [("p", 96, 1), ("p", 100, 1), ("c", 104, -1), ("c", 108, 1)],
                ("", 1),
            ),
            (
                [("p", 96, 1), ("p", 104, -1), ("c", 100, -1), ("c", 108, 1)],
                ("", 1),
            ),
            (
                [("p", 92, 1), ("p", 96, 1), ("p", 100, -1), ("c", 108, 1)],
                ("", 1),
            ),
            (
                [
                    ("c", 92, 1),
                    ("c", 96, 1),
                    ("c", 100, -1),
                    ("c", 104, 1),
                    ("c", 108, 1),
                ],
                ("", 1),
            ),
        ],
    )
    def test_one_expiration(self, legs, expected):
        """Every single-expiration structure is named by its combo code."""
        assert optimizer.classify([_leg(*leg) for leg in legs]) == expected

    @pytest.mark.parametrize(
        "legs,expected",
        [
            ([("c", 100, -1, 30), ("c", 100, 1, 60)], ("CCAL", 1)),
            ([("c", 100, 1, 30), ("c", 100, -1, 60)], ("CCAL", -1)),
            ([("p", 100, -1, 30), ("p", 104, 1, 60)], ("PDIAG", 1)),
            ([("p", 100, -1, 30), ("p", 104, 2, 60)], ("", 1)),
            ([("c", 100, -1, 30), ("p", 100, 1, 60)], ("", 1)),
            ([("c", 96, 1, 30), ("c", 100, -1, 60), ("c", 104, 1, 60)], ("", 1)),
        ],
    )
    def test_two_expirations(self, legs, expected):
        """A calendar shares a strike across terms; a diagonal does not."""
        assert optimizer.classify([_leg(*leg) for leg in legs]) == expected


class TestOptimizer:
    """Every combo structure is built, sized to what it risks, and ranked."""

    @staticmethod
    def _near(frame):
        """Return the nearer of the two expirations."""
        return chain.expirations(frame)[0]

    def test_builds_every_structure(self, chain_frame):
        """Every Deribit combo structure is offered, bought and sold."""
        frame = chain_frame()
        built = optimizer.candidates(frame, self._near(frame), 100.0, (), True)

        assert {item["strategy"] for item in built} == set(optimizer.NAMES.values())
        assert all(item["code"] for item in built)

    def test_a_position_is_offered_once(self, chain_frame):
        """No two candidates trade the same contracts in the same amounts."""
        frame = chain_frame()
        built = optimizer.candidates(frame, self._near(frame), 100.0, (), True)
        keys = [optimizer._key(item["legs"]) for item in built]

        assert len(keys) == len(set(keys))

    def test_the_last_expiration_has_no_calendar(self, chain_frame):
        """With nothing later to trade against, no calendar is built."""
        frame = chain_frame()
        last = chain.expirations(frame)[-1]
        built = optimizer.candidates(frame, last, 100.0, (), True)

        assert not {item["code"] for item in built} & {"CCAL", "PCAL", "CDIAG", "PDIAG"}

    def test_a_far_expiration_missing_one_side_builds_no_calendar_on_it(
        self, chain_frame
    ):
        """A far expiration without puts offers no put calendar."""
        frame = chain_frame()
        far = chain.expirations(frame)[-1]
        frame = frame[~((frame["expiration"] == far) & (frame["option_type"] == "put"))]
        built = optimizer.candidates(frame, self._near(frame), 100.0, (), True)
        codes = {item["code"] for item in built}

        assert "CCAL" in codes
        assert not codes & {"PCAL", "PDIAG"}

    def test_ranks_the_best_of_each_structure(self, chain_frame):
        """Each structure appears once, the most profitable first."""
        frame = chain_frame()
        ranked = optimizer.rank(frame, self._near(frame), 100.0, 104.0, 1.0, True)
        names = [item["strategy"] for item in ranked]
        profits = [item["expected_profit"] for item in ranked]

        assert len(names) == len(set(names)) == len(optimizer.NAMES)
        assert profits == sorted(profits, reverse=True)

    def test_the_limit_caps_the_structures(self, chain_frame):
        """Asking for fewer structures returns the best of them."""
        frame = chain_frame()
        ranked = optimizer.rank(frame, self._near(frame), 100.0, 104.0, 1.0, True, 3)

        assert len(ranked) == 3

    @pytest.mark.parametrize("inverse", [True, False])
    def test_every_position_risks_the_budget(self, chain_frame, inverse):
        """The worst loss across a threefold move either way is the budget."""
        from openbb_deribit.utils.options.legs import payoff

        frame = chain_frame(inverse=inverse)

        for item in optimizer.rank(
            frame, self._near(frame), 100.0, 104.0, 5000.0, inverse
        ):
            points = optimizer._stress(item["position"], 100.0, item["elapsed"])
            losses = payoff(
                item["position"], points, item["elapsed"], inverse, 100.0, item["cost"]
            )

            if inverse:
                losses = [
                    loss / price * 100.0
                    for loss, price in zip(losses, points, strict=True)
                ]

            assert min(losses) == pytest.approx(-5000.0), item["strategy"]

    def test_a_credit_is_sized_by_what_it_risks(self):
        """A position taken in for a credit is ranked, not dropped."""
        sold = {"strategy": "Short Call", "legs": [_leg("c", 100, -1, 1, 5.0)]}
        scored = optimizer.score(sold, 100.0, 90.0, False)

        assert scored["cost"] < 0
        assert scored["expected"] > 0

    def test_a_position_with_nothing_at_risk_is_not_ranked(self):
        """A position that cannot lose has no capital at risk to size against."""
        free = {"strategy": "Long Call", "legs": [_leg("c", 100, 1, 1, 0.0)]}

        assert optimizer.score(free, 100.0, 120.0, False) is None

    def test_a_calendar_is_stressed_across_its_remaining_life(self):
        """A leg still alive at the valuation date is sought across a grid."""
        legs = [_leg("c", 100, -1, 30), _leg("c", 100, 1, 60)]

        assert len(optimizer._stress(legs, 100.0, 30)) > optimizer.STRESS_STEPS
        assert optimizer._stress(legs[:1], 100.0, 30) == [100.0 / 3, 100.0, 300.0]

    def test_the_budget_scales_the_result(self, chain_frame):
        """Doubling the budget doubles the profit and the contracts."""
        frame = chain_frame()
        one = optimizer.rank(frame, self._near(frame), 100.0, 104.0, 1000.0, True, 1)
        two = optimizer.rank(frame, self._near(frame), 100.0, 104.0, 2000.0, True, 1)

        assert two[0]["expected_profit"] == pytest.approx(one[0]["expected_profit"] * 2)
        assert two[0]["contracts"] == pytest.approx(one[0]["contracts"] * 2)

    def test_a_linear_chain_is_ranked_in_its_quote(self, chain_frame):
        """A linear chain ranks without the coin conversion."""
        frame = chain_frame(inverse=False, spot=1.5, size=1000)

        assert optimizer.rank(frame, self._near(frame), 1.5, 2.0, 1000.0, False, 3)

    def test_strikes_far_from_the_money_are_left_out(self, chain_frame):
        """A strike well outside the window is not offered."""
        frame = chain_frame()
        built = optimizer.candidates(frame, self._near(frame), 100.0, (), True)
        offered = {leg["strike"] for item in built for leg in item["legs"]}

        assert max(offered) <= 100.0 * (1 + optimizer.STRIKE_WINDOW)


class TestComboBooks:
    """A position Deribit lists as a combo is priced from that combo's book."""

    @staticmethod
    def _book(frame, bid=0.4, ask=0.5):
        """List a call spread on the far expiration of the synthetic chain."""
        far = chain.expirations(frame)[-1]
        calls = frame[(frame["expiration"] == far) & (frame["option_type"] == "call")]
        low, high = sorted(
            calls["contract_symbol"], key=lambda name: float(name.split("-")[2])
        )[3:5]

        return far, {
            "name": "TEST-CS-FAR",
            "legs": [(low, 1), (high, -1)],
            "bid": bid,
            "ask": ask,
        }

    def test_buying_pays_the_offer_and_selling_takes_the_bid(self, chain_frame):
        """The combo is bought at its ask and sold at its bid, carried to USD."""
        frame = chain_frame()
        far, book = self._book(frame)
        built = optimizer.candidates(frame, far, 100.0, [book], True)
        listed = {
            item["strategy"]: item for item in built if item["combo"] == "TEST-CS-FAR"
        }

        assert listed["Bull Call Spread"]["premium"] == pytest.approx(50.0)
        assert listed["Bear Call Spread"]["premium"] == pytest.approx(-40.0)

    def test_a_linear_combo_is_not_carried(self):
        """A combo quoted in the quote currency is taken as quoted."""
        book = {"name": "X", "legs": [("A", 1), ("B", -1)], "bid": 0.4, "ask": 0.5}

        assert optimizer.combo_book([book], 100.0, False)[
            frozenset([("A", 1), ("B", -1)])
        ] == ("X", 0.5)

    def test_an_unquoted_side_prices_nothing(self):
        """A combo with no bid or offer leaves that side to its legs."""
        book = {"name": "X", "legs": [("A", 1), ("B", -1)], "bid": None, "ask": None}

        assert optimizer.combo_book([book], 100.0, True) == {}

    def test_a_listed_combo_outside_the_window_is_still_offered(self, chain_frame):
        """A combo someone listed is ranked even where the builder does not reach."""
        frame = chain_frame()
        far, book = self._book(frame)
        built = optimizer.candidates(frame, far, 1000.0, [book], True)

        assert {item["combo"] for item in built} == {"TEST-CS-FAR"}

    def test_a_combo_on_another_expiration_is_left_out(self, chain_frame):
        """Only combos held to the expiration being ranked are offered."""
        frame = chain_frame()
        _far, book = self._book(frame)
        built = optimizer.candidates(frame, self._near(frame), 1000.0, [book], True)

        assert not any(item["combo"] for item in built)

    def test_a_combo_on_an_unquoted_contract_is_left_out(self, chain_frame):
        """A combo naming a contract nobody quotes cannot be priced leg by leg."""
        frame = chain_frame()
        far, book = self._book(frame)
        book["legs"] = [("NOPE-1-1-C", 1), *book["legs"][1:]]
        built = optimizer.candidates(frame, far, 1000.0, [book], True)

        assert built == []

    @staticmethod
    def _near(frame):
        """Return the nearer of the two expirations."""
        return chain.expirations(frame)[0]


class TestRebuild:
    """A description of legs reads back as the position it names."""

    def test_counts_are_read(self, chain_frame):
        """'Sell 2 SYMBOL' sells two contracts."""
        frame = chain_frame()
        quotes = chain.quotes_at(frame)
        names = sorted(
            quotes[(quotes["dte"] == 30) & (quotes["option_type"] == "call")][
                "contract_symbol"
            ],
            key=lambda name: float(name.split("-")[2]),
        )
        built = optimizer.rebuild(f"Buy {names[3]} / Sell 2 {names[5]}", quotes)

        assert built["code"] == "CSR12"
        assert [leg["quantity"] for leg in built["legs"]] == [1, -2]
        assert optimizer._describe(built["legs"]) == (
            f"Buy {names[3]} / Sell 2 {names[5]}"
        )

    @pytest.mark.parametrize(
        "written", ["garbage", "Buy", "Hold X", "Buy two X", "Sell 0 X", "Buy 1 2 X"]
    )
    def test_something_that_is_not_a_leg_says_so(self, chain_frame, written):
        """Text that names no leg is refused with what the format is."""
        with pytest.raises(ValueError, match="Buy SYMBOL / Sell SYMBOL"):
            optimizer.rebuild(written, chain.quotes_at(chain_frame()))

    def test_an_unlisted_contract_says_so(self, chain_frame):
        """A contract the chain does not list cannot be priced."""
        with pytest.raises(ValueError, match="not a listed contract"):
            optimizer.rebuild("Buy NOPE-1-1-C", chain.quotes_at(chain_frame()))

    def test_an_unrecognised_shape_is_custom(self, chain_frame):
        """Contracts that make no combo are still priced, as a custom position."""
        quotes = chain.quotes_at(chain_frame())
        calls = quotes[(quotes["dte"] == 30) & (quotes["option_type"] == "call")]
        low, high = list(calls["contract_symbol"])[:2]
        built = optimizer.rebuild(f"Buy {low} / Buy {high}", quotes)

        assert (built["strategy"], built["code"]) == ("Custom", None)


class TestStrategies:
    """The standard structures are priced at every expiration."""

    def test_straddles(self, chain_frame):
        """A straddle costs both legs and breaks even either side of them."""
        frame = chain_frame()
        priced = strategies.straddles(frame, 100.0)

        assert len(priced) == 2

        for row in priced:
            assert row["cost"] == pytest.approx(
                row["call_premium"] + row["put_premium"]
            )
            assert row["breakeven_lower"] < row["strike"] < row["breakeven_upper"]
            assert row["max_loss"] == -row["cost"]

    def test_strangles_straddle_the_money(self, chain_frame):
        """A strangle's call sits above its put."""
        frame = chain_frame()

        for row in strategies.strangles(frame, 100.0, 0.04):
            assert row["put_strike"] < row["call_strike"]
            assert row["cost"] > 0

    def test_verticals_are_capped_both_ways(self, chain_frame):
        """A vertical's profit and loss are both bounded."""
        frame = chain_frame()
        priced = strategies.verticals(frame, 100.0, 0.04)

        assert priced

        for row in priced:
            assert row["max_profit"] > 0
            assert row["max_loss"] == -row["cost"]
            assert row["strategy"] in ("Bull Call Spread", "Bear Put Spread")

    def test_a_chain_with_no_pair_prices_nothing(self, chain_frame):
        """An expiration missing one side prices no two-legged structure."""
        frame = chain_frame()
        frame = frame[frame["option_type"] == "call"]

        assert strategies.straddles(frame, 100.0) == []
        assert strategies.strangles(frame, 100.0, 0.04) == []
        assert all(
            row["strategy"] == "Bull Call Spread"
            for row in strategies.verticals(frame, 100.0, 0.04)
        )

    def test_a_straddle_needs_both_legs_on_one_strike(self, chain_frame):
        """Sides that share no strike make no straddle."""
        frame = chain_frame()
        frame = frame[
            ((frame["option_type"] == "call") & (frame["strike"] < 100.0))
            | ((frame["option_type"] == "put") & (frame["strike"] > 100.0))
        ]

        assert strategies.straddles(frame, 100.0) == []

    def test_a_strangle_needs_its_legs_apart(self, chain_frame):
        """Both legs landing on one strike makes no strangle."""
        frame = chain_frame()
        frame = frame[frame["strike"] == 100.0]

        assert strategies.strangles(frame, 100.0, 0.04) == []

    def test_a_zero_width_spread_is_skipped(self, chain_frame):
        """A spread whose legs share a strike is not priced."""
        frame = chain_frame()

        assert strategies.verticals(frame, 100.0, 0.0) == []


class TestPayoffWindow:
    """A payoff is drawn over the prices that matter to the position.

    Drawn over a fixed span either side of spot, the strikes and the profitable
    side collapse into a sliver and most of the width shows a flat line.
    """

    @staticmethod
    def _drawn(chain_frame, target, inverse=True, spot=100.0):
        """Rank one strategy and return the range its payoff was drawn over."""
        frame = chain_frame(inverse=inverse, spot=spot)
        item = optimizer.rank(
            frame, chain.expirations(frame)[0], spot, target, 5000.0, inverse, 1
        )[0]

        return item, min(item["prices"]), max(item["prices"])

    def test_the_window_holds_the_position(self, chain_frame):
        """Every strike and every breakeven is inside the drawn range."""
        item, low, high = self._drawn(chain_frame, 120.0)
        strikes = [leg["strike"] for leg in item["position"]]

        for price in [*strikes, *item["breakevens"]]:
            assert low <= price <= high, f"{price} falls outside {low}-{high}"

    @staticmethod
    def _spread():
        """Return a capped position: one call bought, a higher one sold."""
        return [
            {
                "strike": strike,
                "option_type": "call",
                "quantity": quantity,
                "size": 1,
                "price": price,
                "dte": 0,
                "implied_volatility": None,
            }
            for strike, quantity, price in ((100.0, 1, 5.0), (110.0, -1, 1.0))
        ]

    def test_a_distant_view_does_not_stretch_a_capped_position(self):
        """A target far past where a position stops paying is not drawn to.

        A capped structure earns nothing more above its own ceiling, so drawing
        out to a remote target would add only a straight line.
        """
        _low, high = optimizer._window(self._spread(), 100.0, 1000.0, 0, False)

        assert high < 200.0

    def test_a_position_that_never_pays_is_drawn_around_spot(self):
        """A payout flat across the whole scan has nowhere in particular to look."""
        unreachable = [
            {
                "strike": 1e6,
                "option_type": "call",
                "quantity": 1,
                "size": 1,
                "price": 1.0,
                "dte": 0,
                "implied_volatility": None,
            }
        ]
        low, high = optimizer._window(unreachable, 100.0, 100.0, 0, False)

        assert low < 100.0 < high
        assert high - low == pytest.approx(2 * 100.0 * optimizer.MIN_PAD)

    def test_an_uncapped_view_is_drawn_out_to_the_target(self):
        """A position that keeps paying has no ceiling, so the view is the edge."""
        bought = [self._spread()[0]]
        _low, high = optimizer._window(bought, 100.0, 200.0, 0, False)

        assert high >= 200.0

    def test_the_window_is_far_tighter_than_the_scan(self, chain_frame):
        """The drawn range is a fraction of the range that was searched."""
        _item, low, high = self._drawn(chain_frame, 120.0)
        searched = 100.0 * optimizer.PROBE_SPREAD * 2

        assert high - low < searched / 2

    def test_a_far_crossing_does_not_widen_the_window(self, chain_frame):
        """An inverse position crosses zero far above its strikes.

        That crossing is real but it is nowhere near the trade, so letting it
        set the range would flatten everything worth looking at.
        """
        from openbb_deribit.utils.options.legs import breakevens, payoff
        from openbb_deribit.utils.options.optimizer import _grid, _window

        def leg(strike, quantity, price):
            return {
                "strike": strike,
                "option_type": "call",
                "quantity": quantity,
                "size": 1,
                "price": price,
                "dte": 0,
                "implied_volatility": None,
            }

        legs = [leg(100.0, 1, 8.0), leg(110.0, -1, 1.34)]
        low, high = _window(legs, 100.0, 100.0, 0, True)
        scanned = _grid(
            100.0 * (1 - optimizer.PROBE_SPREAD),
            100.0 * (1 + optimizer.PROBE_SPREAD),
            optimizer.SCOUT_STEPS,
        )
        crossings = breakevens(scanned, payoff(legs, scanned, 0, True, 100.0))

        assert len(crossings) > 1, "this position should cross zero twice"
        assert high < max(crossings), "the far crossing set the range"
        assert low <= 100.0 <= high

    def test_the_window_never_starts_below_nothing(self, chain_frame):
        """A position around a low price is not drawn at a negative one."""
        _item, low, _high = self._drawn(chain_frame, 1.5, inverse=False, spot=1.5)

        assert low >= 0.0

    def test_the_profitable_side_is_a_real_share_of_the_width(self, chain_frame):
        """The reader can see where the position makes money."""
        item, _low, _high = self._drawn(chain_frame, 120.0)
        profitable = sum(1 for value in item["payoff"] if value > 0)

        assert profitable / len(item["payoff"]) > 0.1
