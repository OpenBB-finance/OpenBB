#!/usr/bin/env python

import argparse

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import thought_of_the_day as thought
from gamestonk_terminal import res_menu as rm
from gamestonk_terminal.discovery import disc_controller
from gamestonk_terminal.due_diligence import dd_controller
from gamestonk_terminal.fundamental_analysis import fa_controller
from gamestonk_terminal.helper_funcs import b_is_stock_market_open, get_flair
from gamestonk_terminal.main_helper import clear, export, load, print_help, view, candle
from gamestonk_terminal.menu import session
from gamestonk_terminal.papermill import papermill_controller as mill
from gamestonk_terminal.behavioural_analysis import ba_controller
from gamestonk_terminal.technical_analysis import ta_controller
from gamestonk_terminal.comparison_analysis import ca_controller
from gamestonk_terminal.exploratory_data_analysis import eda_controller
from gamestonk_terminal.options import op_controller
from gamestonk_terminal.fred import fred_controller
from gamestonk_terminal.residuals_analysis import ra_controller
from gamestonk_terminal.portfolio import port_controller
from gamestonk_terminal.cryptocurrency import crypto_controller
from gamestonk_terminal.screener import screener_controller
from gamestonk_terminal.portfolio_optimization import po_controller

# import warnings
# warnings.simplefilter("always")


# pylint: disable=too-many-branches


def main():
    """
    Gamestonk Terminal is an awesome stock market terminal that has been developed for fun,
    while I saw my GME shares tanking. But hey, I like the stock.
    """
    # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
    if sys.platform == "win32":
        os.system("")

    s_ticker = ""
    s_start = ""
    df_stock = pd.DataFrame()
    s_interval = "1440min"

    # Set stock by default to speed up testing
    # s_ticker = "BB"
    # ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    # df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')
    # df_stock.sort_index(ascending=True, inplace=True)
    # s_start = datetime.strptime("2020-06-04", "%Y-%m-%d")
    # df_stock = df_stock[s_start:]

    # Add list of arguments that the main parser accepts
    menu_parser = argparse.ArgumentParser(add_help=False, prog="gamestonk_terminal")
    choices = [
        "help",
        "quit",
        "q",
        "clear",
        "load",
        "candle",
        "view",
        "export",
        "disc",
        "scr",
        "mill",
        "ba",
        "res",
        "fa",
        "ta",
        "dd",
        "eda",
        "pred",
        "ca",
        "op",
        "fred",
        "pa",
        "crypto",
        "ra",
        "po",
    ]

    menu_parser.add_argument("opt", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    # Print first welcome message and help
    print("\nWelcome to Gamestonk Terminal 🚀\n")
    should_print_help = True
    parsed_stdin = False

    if gtff.ENABLE_THOUGHTS_DAY:
        print("-------------------")
        try:
            thought.get_thought_of_the_day()
        except Exception as e:
            print(e)
        print("")

    # Loop forever and ever
    while True:
        main_cmd = False
        if should_print_help:
            print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
            should_print_help = False

        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # Get input command from stdin or user
        if not parsed_stdin and len(sys.argv) > 1:
            as_input = " ".join(sys.argv[1:])
            parsed_stdin = True
            print(f"{get_flair()}> {as_input}")
        elif session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(f"{get_flair()}> ", completer=completer)
        else:
            as_input = input(f"{get_flair()}> ")

        # Is command empty
        if not as_input:
            print("")
            continue

        # Parse main command of the list of possible commands
        try:
            (ns_known_args, l_args) = menu_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        b_quit = False
        if ns_known_args.opt == "help":
            should_print_help = True

        elif (ns_known_args.opt == "quit") or (ns_known_args.opt == "q"):
            break

        elif ns_known_args.opt == "clear":
            s_ticker, s_start, s_interval, df_stock = clear(
                l_args, s_ticker, s_start, s_interval, df_stock
            )
            main_cmd = True

        elif ns_known_args.opt == "load":
            s_ticker, s_start, s_interval, df_stock = load(
                l_args, s_ticker, s_start, s_interval, df_stock
            )
            main_cmd = True

        elif ns_known_args.opt == "candle":

            if s_ticker:
                candle(
                    s_ticker,
                    (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                )

            else:
                print(
                    "No ticker selected. Use 'load ticker' to load the ticker you want to look at.",
                    "\n",
                )

            main_cmd = True

        elif ns_known_args.opt == "view":

            if s_ticker:
                view(l_args, s_ticker, s_start, s_interval, df_stock)

            else:
                print(
                    "No ticker selected. Use 'load ticker' to load the ticker you want to look at.",
                    "\n",
                )
            main_cmd = True

        elif ns_known_args.opt == "export":
            export(l_args, df_stock)
            main_cmd = True

        elif ns_known_args.opt == "disc":
            b_quit = disc_controller.menu()

        elif ns_known_args.opt == "mill":
            b_quit = mill.papermill_menu()

        elif ns_known_args.opt == "ba":
            b_quit = ba_controller.menu(
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker, s_start
            )

        elif ns_known_args.opt == "res":
            b_quit = rm.res_menu(
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                s_start,
                s_interval,
            )

        elif ns_known_args.opt == "ca":
            b_quit = ca_controller.menu(df_stock, s_ticker, s_start, s_interval)

        elif ns_known_args.opt == "fa":
            b_quit = fa_controller.menu(
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                s_start,
                s_interval,
            )

        elif ns_known_args.opt == "ta":
            b_quit = ta_controller.menu(
                df_stock,
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                s_start,
                s_interval,
            )

        elif ns_known_args.opt == "dd":
            b_quit = dd_controller.menu(
                df_stock,
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                s_start,
                s_interval,
            )

        elif ns_known_args.opt == "eda":
            if s_interval == "1440min":
                b_quit = eda_controller.menu(
                    df_stock,
                    s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                    s_start,
                    s_interval,
                )
            else:
                df_stock = yf.download(s_ticker, start=s_start, progress=False)
                df_stock = df_stock.rename(
                    columns={
                        "Open": "1. open",
                        "High": "2. high",
                        "Low": "3. low",
                        "Close": "4. close",
                        "Adj Close": "5. adjusted close",
                        "Volume": "6. volume",
                    }
                )
                df_stock.index.name = "date"
                s_interval = "1440min"

                b_quit = eda_controller.menu(
                    df_stock,
                    s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                    s_start,
                    s_interval,
                )

        elif ns_known_args.opt == "op":
            b_quit = op_controller.menu(
                s_ticker, df_stock["5. adjusted close"].values[-1]
            )

        elif ns_known_args.opt == "fred":
            b_quit = fred_controller.menu()

        elif ns_known_args.opt == "pa":
            b_quit = port_controller.menu()

        elif ns_known_args.opt == "crypto":
            b_quit = crypto_controller.menu()

        elif ns_known_args.opt == "po":
            b_quit = po_controller.menu([s_ticker])

        elif ns_known_args.opt == "pred":

            if not gtff.ENABLE_PREDICT:
                print("Predict is not enabled in feature_flags.py")
                print("Prediction menu is disabled")
                print("")
                continue

            try:
                # pylint: disable=import-outside-toplevel
                from gamestonk_terminal.prediction_techniques import pred_controller
            except ModuleNotFoundError as e:
                print("One of the optional packages seems to be missing")
                print("Optional packages need to be installed")
                print(e)
                print("")
                continue
            except Exception as e:
                print(e)
                print("")
                continue

            if s_interval == "1440min":
                b_quit = pred_controller.menu(
                    df_stock,
                    s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                    s_start,
                    s_interval,
                )
            # If stock data is intradaily, we need to get data again as prediction
            # techniques work on daily adjusted data. By default we load data from
            # Alpha Vantage because the historical data loaded gives a larger
            # dataset than the one provided by quandl
            else:
                try:
                    ts = TimeSeries(
                        key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
                    )
                    # pylint: disable=unbalanced-tuple-unpacking
                    df_stock_pred, _ = ts.get_daily_adjusted(
                        symbol=s_ticker, outputsize="full"
                    )
                    # pylint: disable=no-member
                    df_stock_pred = df_stock_pred.sort_index(ascending=True)
                    df_stock_pred = df_stock_pred[s_start:]
                    b_quit = pred_controller.menu(
                        df_stock_pred,
                        s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                        s_start,
                        interval="1440min",
                    )
                except Exception as e:
                    print(e)
                    print("Either the ticker or the API_KEY are invalids. Try again!")
                    return

        elif ns_known_args.opt == "ra":
            b_quit = ra_controller.menu(
                df_stock,
                s_ticker.split(".")[0] if "." in s_ticker else s_ticker,
                s_start,
                s_interval,
            )

        elif ns_known_args.opt == "scr":
            b_quit = screener_controller.menu()

        else:
            print("Shouldn't see this command!")
            continue

        if b_quit:
            break
        else:
            if not main_cmd:
                should_print_help = True

    print(
        "Hope you enjoyed the terminal. Remember that stonks only go up. Diamond hands.\n"
    )


if __name__ == "__main__":
    main()
