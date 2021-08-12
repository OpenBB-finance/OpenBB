from unittest import TestCase, mock
import sys
import io

import vcr

from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_view


class TestOptimizerView(TestCase):
    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/test_equal_weights.yaml"
    )
    def test_equal_weights(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.equal_weight(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/test_property_weights.yaml",
        record_mode="new_episodes",
    )
    def test_property_weighting(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.property_weighting(["TSLA", "GME"], ["-p", "previousClose"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/general1.yaml",
        record_mode="new_episodes",
    )
    def test_max_sharpe(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.max_sharpe(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/general1.yaml",
        record_mode="new_episodes",
    )
    def test_min_volatility(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.min_volatility(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/general1.yaml",
        record_mode="new_episodes",
    )
    def test_max_quadratic_utility(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.max_quadratic_utility(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/general1.yaml",
        record_mode="new_episodes",
    )
    def test_efficient_risk(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.efficient_risk(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("The minimum volatility", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/general1.yaml",
        record_mode="new_episodes",
    )
    def test_efficient_return(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.efficient_return(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_port_opt/test_opt_view/test_show_eff.yaml",
        record_mode="new_episodes",
    )
    @mock.patch("matplotlib.pyplot.show")
    def test_show_ef(self, mock_mlp):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.show_ef(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("\n", capt)
