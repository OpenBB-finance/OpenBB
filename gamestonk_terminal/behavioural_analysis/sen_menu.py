import argparse

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.sentiment import google_api, reddit_api, stocktwits_api
from prompt_toolkit.completion import NestedCompleter


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
    print(
        "   spac_c        show other users spacs announcements from subreddit SPACs community"
    )
    print("   spac          show other users spacs announcements from other subs")
    print("")
    print("Stocktwits:")
    print("   bullbear      estimate quick sentiment from last 30 messages on board")
    print("   messages      output up to the 30 last messages on the board")
    print("   trending      trending stocks")
    print("   stalker       stalk stocktwits user's last messages")
    print("")
    print("Twitter:")
    print("   infer         infer about stock's sentiment from latest tweets")
    print("   sentiment     in-depth sentiment prediction from tweets over time")
    print("")
    print("Google:")
    print("   mentions      interest over time based on stock's mentions")
    print("   regions       regions that show highest interest in stock")
    print("   queries       top related queries with this stock")
    print("   rise          top rising related queries with stock")
    print("")

    return


def sen_menu(s_ticker, s_start):

    # Add list of arguments that the discovery parser accepts
    sen_parser = argparse.ArgumentParser(prog="sen", add_help=False)
    choices = [
        "help",
        "q",
        "quit",
        "watchlist",
        "spac",
        "spac_c",
        "wsb",
        "popular",
        "bullbear",
        "messages",
        "trending",
        "stalker",
        "infer",
        "sentiment",
        "mentions",
        "regions",
        "queries",
        "rise",
    ]
    sen_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    print_sentiment()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (sen)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (sen)> ")

        # Parse sentiment command of the list of possible commands
        try:
            (ns_known_args, l_args) = sen_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            print_sentiment()

        elif ns_known_args.cmd == "q":
            # Just leave the DISC menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "watchlist":
            reddit_api.watchlist(l_args)

        elif ns_known_args.cmd == "spac":
            reddit_api.spac(l_args)

        elif ns_known_args.cmd == "spac_c":
            reddit_api.spac_community(l_args)

        elif ns_known_args.cmd == "wsb":
            reddit_api.wsb_community(l_args)

        elif ns_known_args.cmd == "popular":
            reddit_api.popular_tickers(l_args)

        elif ns_known_args.cmd == "bullbear":
            stocktwits_api.bullbear(l_args, s_ticker)

        elif ns_known_args.cmd == "messages":
            stocktwits_api.messages(l_args, s_ticker)

        elif ns_known_args.cmd == "trending":
            stocktwits_api.trending(l_args)

        elif ns_known_args.cmd == "stalker":
            stocktwits_api.stalker(l_args)

        elif ns_known_args.cmd == "infer":
            if not gtff.ENABLE_PREDICT:
                print("Predict is not enabled in feature_flags.py")
                print("Twitter inference menu is disabled")
                print("")
                continue

            try:
                # pylint: disable=import-outside-toplevel
                from gamestonk_terminal.sentiment import twitter_api
            except ModuleNotFoundError as e:
                print("One of the optional packages seems to be missing")
                print("Optional packages need to be installed")
                print(e)
                print("")
                continue
            except Exception as e:
                print(e)
                print("")
                continue

            twitter_api.inference(l_args, s_ticker)

        elif ns_known_args.cmd == "sentiment":
            if not gtff.ENABLE_PREDICT:
                print("Predict is not enabled in config_terminal.py")
                print("Twitter sentiment menu is disabled")
                print("")
                continue

            try:
                # pylint: disable=import-outside-toplevel
                from gamestonk_terminal.sentiment import twitter_api
            except ModuleNotFoundError as e:
                print("One of the optional packages seems to be missing")
                print("Optional packages need to be installed")
                print(e)
                print("")
                continue
            except Exception as e:
                print(e)
                print("")
                continue

            twitter_api.sentiment(l_args, s_ticker)

        elif ns_known_args.cmd == "mentions":
            google_api.mentions(l_args, s_ticker, s_start)

        elif ns_known_args.cmd == "regions":
            google_api.regions(l_args, s_ticker)

        elif ns_known_args.cmd == "queries":
            google_api.queries(l_args, s_ticker)

        elif ns_known_args.cmd == "rise":
            google_api.rise(l_args, s_ticker)

        else:
            print("Command not recognized!")
