import config_bot as cfg
import argparse
from discovery import alpha_vantage_api
from discovery import yahoo_finance_api
from discovery import reddit_api
from discovery import finviz_api
from discovery import short_interest_api


# -----------------------------------------------------------------------------------------------------------------------
def print_discovery():
    """ Print help """

    print("\nDiscovery Mode:") 
    print("   help          show this fundamental analysis menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   map           S&P500 index stocks map [Finviz]")
    print("   sectors       show sectors performance [Alpha Vantage]")
    print("   gainers       show latest top gainers [Yahoo Finance]")
    print("   high_short    show top high short interest stocks of over 20% ratio [www.highshortinterest.com]")
    print("   low_float     show low float stocks under 10M shares float [www.lowfloat.com]")
    print("")
    print("Reddit:")
    print("   wsb           show what WSB gang is up to in subreddit wallstreetbets")
    print("   watchlist     show other users watchlist")
    print("   popular       show popular tickers")
    print("   spac          show other users spacs announcements")
    print("   spac_c        show other users spacs announcements from subreddit SPACs")
    print("")
    return


# ---------------------------------------------------- MENU ----------------------------------------------------
def disc_menu():

    # Add list of arguments that the discovery parser accepts
    disc_parser = argparse.ArgumentParser(prog='discovery', add_help=False)
    disc_parser.add_argument('cmd', choices=['help', 'q', 'quit',
                                             'map', 'sectors', 'gainers', 'high_short', 'low_float',
                                             'watchlist', 'spac', 'spac_c', 'wsb', 'popular'])

    print_discovery()

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = disc_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
            
        if ns_known_args.cmd == 'help':
            print_discovery()

        elif ns_known_args.cmd == 'q':
            # Just leave the DISC menu
            return False

        elif ns_known_args.cmd == 'quit':
            # Abandon the program
            return True

        # --------------------------------------------------- FINVIZ ---------------------------------------------------
        elif ns_known_args.cmd == 'map':
            finviz_api.map_sp500(l_args)
        
        # ------------------------------------------------ ALPHA VANTAGE -----------------------------------------------
        elif ns_known_args.cmd == 'sectors':
            alpha_vantage_api.sectors(l_args)
        
        # ------------------------------------------------ YAHOO FINANCE ------------------------------------------------
        elif ns_known_args.cmd == 'gainers':
            yahoo_finance_api.gainers(l_args)

        # ------------------------------------------------ SHORT_INTEREST ------------------------------------------------
        elif ns_known_args.cmd == 'high_short':
            short_interest_api.high_short_interest(l_args)
        
        elif ns_known_args.cmd == 'low_float':
            short_interest_api.low_float(l_args)

        # ---------------------------------------------------- REDDIT ---------------------------------------------------
        elif ns_known_args.cmd == 'watchlist':
            reddit_api.watchlist(l_args)
        
        elif ns_known_args.cmd == 'spac':
            reddit_api.spac(l_args)

        elif ns_known_args.cmd == 'spac_c':
            reddit_api.spac_community(l_args)

        elif ns_known_args.cmd == 'wsb':
            reddit_api.wsb_community(l_args)

        elif ns_known_args.cmd == 'popular':
            reddit_api.popular_tickers(l_args)

        # ------------------------------------------------------------------------------------------------------------
        else:
            print("Command not recognized!")