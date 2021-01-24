import argparse
import webbrowser

# ---------------------------------------------------- MAP_SP500 ----------------------------------------------------
def map_sp500(l_args):
    parser = argparse.ArgumentParser(prog='map', description='''S&P500 index stocks categorized by sectors and industries.
                                                                Size represents market cap.''')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    webbrowser.open('https://finviz.com/map.ashx')
    print("")
