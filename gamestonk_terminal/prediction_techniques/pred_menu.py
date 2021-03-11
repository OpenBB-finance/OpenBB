import argparse

import matplotlib.pyplot as plt
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.prediction_techniques import (
    arima,
    ets,
    fbprophet,
    knn,
    neural_networks,
    regression,
    sma,
)
from prompt_toolkit.completion import NestedCompleter


def print_prediction(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f"Intraday {s_interval}", "Daily")[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nPrediction Techniques:")
    print("   help        show this prediction techniques menu again")
    print("   q           quit this menu, and shows back to main menu")
    print("   quit        quit to abandon program")
    print("")
    print("   sma         simple moving average")
    print("   ets         exponential smoothing (e.g. Holt-Winters)")
    print("   knn         k-Nearest Neighbors")
    print("   linear      linear regression (polynomial 1)")
    print("   quadratic   quadratic regression (polynomial 2)")
    print("   cubic       cubic regression (polynomial 3)")
    print("   regression  regression (other polynomial)")
    print("   arima       autoregressive integrated moving average")
    print("   prophet     Facebook's prophet prediction")
    print("   mlp         MultiLayer Perceptron")
    print("   rnn         Recurrent Neural Network")
    print("   lstm        Long-Short Term Memory")
    print("")


def pred_menu(df_stock, s_ticker, s_start, s_interval):

    # Add list of arguments that the prediction techniques parser accepts
    pred_parser = argparse.ArgumentParser(prog="pred", add_help=False)
    choices = [
        "help",
        "q",
        "quit",
        "sma",
        "ets",
        "knn",
        "linear",
        "quadratic",
        "cubic",
        "regression",
        "arima",
        "prophet",
        "mlp",
        "rnn",
        "lstm",
    ]
    pred_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    print_prediction(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        if session:
            as_input = session.prompt(
                f"{get_flair()} (pred)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (pred)> ")

        # Images are non blocking - allows to close them if we type other command
        plt.close()

        # Parse prediction techniques command of the list of possible commands
        try:
            (ns_known_args, l_args) = pred_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            print_prediction(s_ticker, s_start, s_interval)

        elif ns_known_args.cmd == "q":
            # Just leave the FA menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "sma":
            sma.simple_moving_average(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "ets":
            ets.exponential_smoothing(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "knn":
            knn.k_nearest_neighbors(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "linear":
            regression.regression(l_args, s_ticker, df_stock, regression.LINEAR)

        elif ns_known_args.cmd == "quadratic":
            regression.regression(l_args, s_ticker, df_stock, regression.QUADRATIC)

        elif ns_known_args.cmd == "cubic":
            regression.regression(l_args, s_ticker, df_stock, regression.CUBIC)

        elif ns_known_args.cmd == "regression":
            regression.regression(l_args, s_ticker, df_stock, regression.USER_INPUT)

        elif ns_known_args.cmd == "arima":
            arima.arima(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "prophet":
            fbprophet.fbprophet(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "mlp":
            neural_networks.mlp(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "rnn":
            neural_networks.rnn(l_args, s_ticker, df_stock)

        elif ns_known_args.cmd == "lstm":
            neural_networks.lstm(l_args, s_ticker, df_stock)

        else:
            print("Command not recognized!")
