""" Spachero View """
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def spachero_view(other_args: List[str]):
    """Opens www.spachero.com website in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="spachero",
        description="""Great website for SPACs research. [Source: www.spachero.com]""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        webbrowser.open("https://www.spachero.com")
        print("")

    except Exception as e:
        print(e, "\n")
