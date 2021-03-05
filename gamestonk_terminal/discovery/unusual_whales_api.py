import argparse
import webbrowser

# ---------------------------------------------------- UNUSUAL WHALES ----------------------------------------------------
def unusual_whales(l_args):
    parser = argparse.ArgumentParser(
        prog="uwhales",
        description="""Good website for SPACs research. [Source: www.unusualwhales.com]""",
    )

    try:
        (_, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        webbrowser.open("https://unusualwhales.com/spacs")
        print("")

    except SystemExit:
        print("")
        return
