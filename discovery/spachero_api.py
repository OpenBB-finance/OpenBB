import argparse
import webbrowser
from helper_funcs import parse_known_args_and_warn

# ---------------------------------------------------- SPACHERO ----------------------------------------------------
def spachero(l_args):
    parser = argparse.ArgumentParser(prog='spachero', 
                                     description='''Great website for SPACs research. [Source: www.spachero.com]''')

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        webbrowser.open(f"https://www.spachero.com")
        print("")

    except SystemExit:
        print("")
        return
