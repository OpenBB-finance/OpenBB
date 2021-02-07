import config_bot as cfg
import argparse
from sentiment import reddit_api

# -----------------------------------------------------------------------------------------------------------------------
def print_sentiment():
    """ Print help """

    print("\nSentiment:") 
    print("   help          show this sentiment menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
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
def sen_menu():

    # Add list of arguments that the discovery parser accepts
    sen_parser = argparse.ArgumentParser(prog='discovery', add_help=False)
    sen_parser.add_argument('cmd', choices=['help', 'q', 'quit',
                                            'watchlist', 'spac', 'spac_c', 'wsb', 'popular'])

    print_sentiment()

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse sentiment command of the list of possible commands
        try:
            (ns_known_args, l_args) = sen_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
            
        if ns_known_args.cmd == 'help':
            print_sentiment()

        elif ns_known_args.cmd == 'q':
            # Just leave the DISC menu
            return False

        elif ns_known_args.cmd == 'quit':
            # Abandon the program
            return True

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