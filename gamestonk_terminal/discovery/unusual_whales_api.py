import argparse
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def unusual_whales(l_args):
    parser = argparse.ArgumentParser(
        prog="uwhales",
        description="""Good website for SPACs research. [Source: www.unusualwhales.com]""",
    )

    parse_known_args_and_warn(parser, l_args)

    webbrowser.open("https://unusualwhales.com/spacs")
    print("")
