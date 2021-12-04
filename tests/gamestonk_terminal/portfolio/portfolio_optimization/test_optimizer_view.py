from unittest import TestCase  # , mock

# import vcr

# from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_view
# from tests.helpers import check_print


class TestOptimizerView(TestCase):
    pass
    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/test_equal_weights.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_equal_weights(self):
    #    optimizer_view.display_equal_weight(["TSLA", "GME"], [])

    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/test_property_weights.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_property_weighting(self):
    #    optimizer_view.display_property_weighting(
    #        ["TSLA", "GME"], ["-p", "previousClose"]
    #    )

    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/general1.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_max_sharpe(self):
    #    optimizer_view.max_sharpe(["TSLA", "GME"], [])

    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/general1.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_min_volatility(self):
    #    optimizer_view.min_volatility(["TSLA", "GME"], [])

    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/general1.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_max_quadratic_utility(self):
    #    optimizer_view.max_quadratic_utility(["TSLA", "GME"], [])

    # @check_print(assert_in="The minimum volatility")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/general1.yaml",
    #    record_mode="new_episodes",
    # )
    # def test_efficient_risk(self):
    #    optimizer_view.efficient_risk(["TSLA", "GME"], [])

    # @check_print(assert_in="TSLA")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/general1.yaml",
    #     record_mode="new_episodes",
    # )
    # def test_efficiet_return(self):
    #     optimizer_view.efficient_return(["TSLA", "GME"], [])

    # @check_print(assert_in="\n")
    # @vcr.use_cassette(
    #    "tests/gamestonk_terminal/portfolio/portfolio_optimization/cassettes/test_optimizer_view/test_show_eff.yaml",
    #     record_mode="new_episodes",
    # )
    # @mock.patch("matplotlib.pyplot.show")
    # def test_show_ef(self, mock_mlp):
    #     # pylint: disable=unused-argument
    #     optimizer_view.show_ef(["TSLA", "GME"], [])
