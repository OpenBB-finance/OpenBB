import argparse
from typing import List
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def unusual_whales_view(other_args: List[str]):
    """Opens unusualwhales.com in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="uwhales",
        description="""Good website for SPACs research. [Source: www.unusualwhales.com]""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        webbrowser.open("https://unusualwhales.com/spacs")
        print("")

    except Exception as e:
        print(e, "\n")
