import argparse
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn

from gamestonk_terminal.comparison_analysis import yahoo_finance_api as yf_api


def get_similar_companies(l_args, s_ticker):
    """ Get similar companies. [Source: Polygon API] """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="get",
        description="""Get similar companies to compare with.""",
    )

    l_similar = []
    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        result = requests.get(
            f"https://api.polygon.io/v1/meta/symbols/{s_ticker}/company?&apiKey={cfg.API_POLYGON_KEY}"
        )

        if result.status_code == 200:
            l_similar = result.json()["similar"]

    except Exception as e:
        print(e)

    print("")
    return l_similar


def select_similar_companies(l_args):
    """ Select similar companies, e.g. NIO,XPEV,LI"""
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="select",
        description="""Select similar companies to compare with.""",
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="similar companies to compare with.",
    )

    try:
        # For the case where a user uses: 'select NIO,XPEV,LI'
        if l_args:
            if "-" not in l_args[0]:
                l_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        print("")
        return ns_parser.l_similar

    except Exception as e:
        print(e)
        print("")
        return []


def print_comparison_analysis(s_ticker, s_start, s_interval, l_similar, b_user):
    """ Print help """

    s_intraday = (f"Intraday {s_interval}", "Daily")[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    s_similar_source = ("Polygon API", "User")[b_user]

    if l_similar:
        print(f"[{s_similar_source}] Similar Companies: {', '.join(l_similar)}")
    else:
        print(f"No similar companies [{s_similar_source}]")

    print("\nComparison Analysis Mode:")
    print("   help          show this comparison analysis menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   get           get similar companies [Polygon API]")
    print("   select        select similar companies")
    print("")
    print("   historical    historical data comparison")
    print("   corr          correlation between similar companies")
    print("")
    return


def ca_menu(df_stock, s_ticker, s_start, s_interval):

    # Add list of arguments that the comparison analysis parser accepts
    ca_parser = argparse.ArgumentParser(prog="ca", add_help=False)
    ca_parser.add_argument(
        "cmd",
        choices=[
            "help",
            "q",
            "quit",
            "get",
            "select",
            "historical",
            "corr",
        ],
    )

    b_user = False
    l_similar = get_similar_companies([], s_ticker)
    print_comparison_analysis(s_ticker, s_start, s_interval, l_similar, b_user)

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input(f"{get_flair()} (ca)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = ca_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            print_comparison_analysis(s_ticker, s_start, s_interval, l_similar, b_user)

        elif ns_known_args.cmd == "q":
            # Just leave the CA menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "get":
            l_similar = get_similar_companies(l_args, s_ticker)
            b_user = False

        elif ns_known_args.cmd == "select":
            l_similar = select_similar_companies(l_args)
            b_user = True

        elif ns_known_args.cmd == "historical":
            yf_api.historical(
                l_args, df_stock, s_ticker, s_start, s_interval, l_similar
            )

        elif ns_known_args.cmd == "corr":
            yf_api.correlation(
                l_args, df_stock, s_ticker, s_start, s_interval, l_similar
            )

        else:
            print("Command not recognized!")
