from unittest import TestCase, mock
import sys
import io

from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_view


class TestOptimizerView(TestCase):
    def test_equal_weights(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.equal_weight(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    def test_property_weighting(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.property_weighting(["TSLA", "GME"], ["-p", "previousClose"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    def test_max_sharpe(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.max_sharpe(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    def test_min_volatility(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.min_volatility(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    def test_max_quadratic_utility(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.max_quadratic_utility(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    def test_efficient_risk(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.efficient_risk(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("The minimum volatility", capt)

    def test_efficient_return(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.efficient_return(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("TSLA", capt)

    @mock.patch("matplotlib.pyplot.show")
    def test_show_ef(self, mock_mlp):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        optimizer_view.show_ef(["TSLA", "GME"], [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("\n", capt)
