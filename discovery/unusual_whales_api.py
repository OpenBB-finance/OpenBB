import argparse
import webbrowser
from helper_funcs import parse_known_args_and_warn

# ---------------------------------------------------- UNUSUAL WHALES ----------------------------------------------------
def unusual_whales(l_args):
    parser = argparse.ArgumentParser(prog='uwhales', 
                                     description='''Good website for SPACs research. [Source: www.unusualwhales.com]''')

    ns_parser = parse_known_args_and_warn(parser, l_args)
    webbrowser.open(f"https://unusualwhales.com/spacs")
