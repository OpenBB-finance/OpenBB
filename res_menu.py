import config_bot as cfg
import argparse
import webbrowser


# -----------------------------------------------------------------------------------------------------------------------
def print_research():
    """ Print help """

    print("\nResearch Mode:") 
    print("   help              show this fundamental analysis menu again")
    print("   q                 quit this menu, and shows back to main menu")
    print("   quit              quit to abandon program")
    print("")
    print("   macroaxis         www.macroaxis.com")
    print("   yahoo             www.finance.yahoo.com")
    print("   finviz            www.finviz.com")
    print("   mw                www.marketwatch.com")
    print("   fool              www.fool.com")
    print("   bi                www.markets.businessinsider.com")
    print("   fmp               www.financialmodelingprep.com")
    print("   fidelity          www.eresearch.fidelity.com")
    print("")
    return


# ---------------------------------------------------- MENU ----------------------------------------------------
def res_menu(s_ticker):

    # Add list of arguments that the discovery parser accepts
    res_parser = argparse.ArgumentParser(prog='discovery', add_help=False)
    res_parser.add_argument('cmd', choices=['help', 'q', 'quit',
                                            'macroaxis', 'yahoo', 'finviz', 'mw', 'fool', 'bi', 'fmp', 'fidelity'])

    print_research()

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = res_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
            
        if ns_known_args.cmd == 'help':
            print_research()

        elif ns_known_args.cmd == 'q':
            # Just leave the RES menu
            return False

        elif ns_known_args.cmd == 'quit':
            # Abandon the program
            return True

        elif ns_known_args.cmd == 'macroaxis':
            try:
                webbrowser.open(f"https://www.macroaxis.com/invest/market/{s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'yahoo':
            try:
                webbrowser.open(f"https://finance.yahoo.com/quote/{s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'finviz':
            try:
                webbrowser.open(f"https://finviz.com/quote.ashx?t={s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'mw':
            try:
                webbrowser.open(f"https://www.marketwatch.com/investing/stock/{s_ticker}")
                print("")
            except SystemExit:
                print("")
                return
    
        elif ns_known_args.cmd == 'fool':
            try:
                webbrowser.open(f"https://www.fool.com/quote/{s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'bi':
            try:
                webbrowser.open(f"https://markets.businessinsider.com/stocks/{s_ticker}-stock/")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'fmp':
            try:
                webbrowser.open(f"https://financialmodelingprep.com/financial-summary/{s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        elif ns_known_args.cmd == 'fidelity':
            try:
                webbrowser.open(f"https://eresearch.fidelity.com/eresearch/goto/evaluate/snapshot.jhtml?symbols={s_ticker}")
                print("")
            except SystemExit:
                print("")
                return

        # ------------------------------------------------------------------------------------------------------------
        else:
            print("Command not recognized!")