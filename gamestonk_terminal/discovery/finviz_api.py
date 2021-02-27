import argparse
import webbrowser

# ---------------------------------------------------- MAP_SP500 ----------------------------------------------------
def map_sp500(l_args):
    parser = argparse.ArgumentParser(prog='map', 
                                     description='''Performance index stocks map categorized by sectors and industries.
                                     Size represents market cap. Opens web-browser. [Source: Finviz]''')

    parser.add_argument('-p', "--period", action="store", dest="s_period", type=str, default="1d", 
                        choices=['1d', '1w', '1m', '3m', '6m', '1y'], help="Performance period.")
    parser.add_argument('-t', "--type", action="store", dest="s_type", type=str, default="sp500", 
                        choices=['sp500', 'world', 'full', 'etf'], help="Map filter type.")

    # Conversion from period and type, to fit url requirements
    d_period = {'1d':'', '1w':'w1', '1m':'w4', '3m':'w13', '6m':'w26', '1y':'w52'}
    d_type = {'sp500':'sec', 'world':'geo', 'full':'sec_all', 'etf':'etf'}

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    
        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        webbrowser.open(f"https://finviz.com/map.ashx?t={d_type[ns_parser.s_type]}&st={d_period[ns_parser.s_period]}")
        print("")

    except SystemExit:
        print("")
        return