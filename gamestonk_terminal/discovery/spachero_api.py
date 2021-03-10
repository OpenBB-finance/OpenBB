import argparse
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def spachero(l_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="spachero",
        description="""Great website for SPACs research. [Source: www.spachero.com]""",
    )

    parse_known_args_and_warn(parser, l_args)

    webbrowser.open("https://www.spachero.com")
    print("")
