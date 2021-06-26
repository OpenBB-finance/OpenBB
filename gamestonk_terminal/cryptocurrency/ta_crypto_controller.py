"""Technical Analysis Controller Module"""
__docformat__ = "numpy"

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.technical_analysis.ta_controller import (
    TechnicalAnalysisController as TAC,
)


class CryptoTechnicalAnalysisController(TAC):
    """Technical Analysis Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "ema",
        "sma",
        "vwap",
        "cci",
        "macd",
        "rsi",
        "stoch",
        "adx",
        "aroon",
        "bbands",
        "ad",
        "obv",
    ]

    def print_help(self):
        """Print help"""

        print(f"\nCrypto: {self.ticker}")

        print("\nTechnical Analysis:")  # https://github.com/twopirllc/pandas-ta
        print("   help        show this technical analysis menu again")
        print("   q           quit this menu, and shows back to main menu")
        print("   quit        quit to abandon program")
        print("")
        print("overlap:")
        print("   ema         exponential moving average")
        print("   sma         simple moving average")
        print("   vwap        volume weighted average price")
        print("momentum:")
        print("   cci         commodity channel index")
        print("   macd        moving average convergence/divergence")
        print("   rsi         relative strength index")
        print("   stoch       stochastic oscillator")
        print("trend:")
        print("   adx         average directional movement index")
        print("   aroon       aroon indicator")
        print("volatility:")
        print("   bbands      bollinger bands")
        print("volume:")
        print("   ad          chaikin accumulation/distribution line values")
        print("   obv         on balance volume")
        print("")


def menu(crypto: pd.DataFrame, ticker: str, start: datetime, interval: str):
    """Crypto Technical Analysis Menu"""

    ta_controller = CryptoTechnicalAnalysisController(crypto, ticker, start, interval)
    ta_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ta_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (ta)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (ta)> ")

        try:
            plt.close("all")

            process_input = ta_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
