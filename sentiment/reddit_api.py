import argparse
from prettytable import PrettyTable
from datetime import datetime, timedelta
import pandas as pd
from psaw import PushshiftAPI
import praw
from datetime import datetime
from pytz import timezone
from holidays import US as holidaysUS
from helper_funcs import *
import re
import finviz
import config_terminal as cfg
import warnings

# -------------------------------------------------------------------------------------------------------------------
def get_last_time_market_was_open(dt):
    # Check if it is a weekend
    if dt.date().weekday() > 4:
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    # Check if it is a holiday
    if dt.strftime('%Y-%m-%d') in holidaysUS():
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    dt = dt.replace(hour=21, minute=0, second=0)

    return dt


# -------------------------------------------------------------------------------------------------------------------
def watchlist(l_args):
    parser = argparse.ArgumentParser(prog='watchlist',
                                     description="""Print other users watchlist. [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts with watchlists retrieved.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        l_sub_reddits = ['pennystocks', 'RobinHoodPennyStocks', 'Daytrading', 'StockMarket', 'stocks', 'investing', 'wallstreetbets']

        d_submission = {}
        d_watchlist_tickers = {}
        l_watchlist_links = list()
        l_watchlist_author = list()
        ls_text = list()

        praw_api = praw.Reddit(client_id=cfg.API_REDDIT_CLIENT_ID,
                               client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                               username=cfg.API_REDDIT_USERNAME,
                               user_agent=cfg.API_REDDIT_USER_AGENT,
                               password=cfg.API_REDDIT_PASSWORD)

        dt_last_time_market_close = get_last_time_market_was_open(datetime.now()-timedelta(hours=24))
        n_ts_after = int(dt_last_time_market_close.timestamp())
        psaw_api = PushshiftAPI()
        submissions = psaw_api.search_submissions(after=n_ts_after,
                                                    subreddit=l_sub_reddits,
                                                    q='WATCHLIST|Watchlist|watchlist',
                                                    filter=['id'])

        n_flair_posts_found = 0
        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed  by moderator in the meanwhile,
                #that there is a description and it's not just an image, that the flair is
                #meaningful, and that we aren't re-considering same author's watchlist
                if not submission.removed_by_category and submission.selftext \
                    and submission.link_flair_text not in ['Yolo', 'Meme'] \
                    and submission.author.name not in l_watchlist_author:
                        ls_text = list()
                        ls_text.append(submission.selftext)
                        ls_text.append(submission.title)

                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            ls_text.append(comment.body)

                        l_tickers_found = list()
                        for s_text in ls_text:
                            for s_ticker in set(re.findall(r'([A-Z]{3,5} )', s_text)):
                                l_tickers_found.append(s_ticker.strip())

                        if l_tickers_found:
                            # Add another author's name to the parsed watchlists
                            l_watchlist_author.append(submission.author.name)

                            # Lookup stock tickers within a watchlist
                            for key in l_tickers_found:
                                if key in d_watchlist_tickers:
                                    # Increment stock ticker found
                                    d_watchlist_tickers[key] += 1
                                else:
                                    # Initialize stock ticker found
                                    d_watchlist_tickers[key] = 1

                            l_watchlist_links.append(f"https://www.reddit.com{submission.permalink}")
                            # delte below, not necessary I reckon. Probably just link?

                            # Refactor data
                            s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime("%d/%m/%Y %H:%M:%S")
                            s_link = f"https://www.reddit.com{submission.permalink}"
                            s_all_awards = ""
                            for award in submission.all_awardings:
                                s_all_awards += f"{award['count']} {award['name']}\n"
                            s_all_awards = s_all_awards[:-2]

                            # Create dictionary with data to construct dataframe allows to save data
                            d_submission[submission.id] = {
                                                            'created_utc': s_datetime,
                                                            'subreddit': submission.subreddit,
                                                            'link_flair_text': submission.link_flair_text,
                                                            'title':submission.title,
                                                            'score': submission.score,
                                                            'link': s_link,
                                                            'num_comments': submission.num_comments,
                                                            'upvote_ratio': submission.upvote_ratio,
                                                            'awards': s_all_awards
                                                        }

                            # Print post data collected so far
                            print(f"\n{s_datetime} - {submission.title}")
                            print(f"{s_link}")
                            t_post = PrettyTable(['Subreddit', 'Flair', 'Score', '# Comments', 'Upvote %', "Awards"])
                            t_post.add_row([submission.subreddit, submission.link_flair_text, submission.score,
                                            submission.num_comments,f"{round(100*submission.upvote_ratio)}%", s_all_awards])
                            print(t_post)
                            print("")

                            # Increment count of valid posts found
                            n_flair_posts_found += 1

                # Check if number of wanted posts found has been reached
                if n_flair_posts_found > ns_parser.n_limit-1:
                    break

            # Check if search_submissions didn't get anymore posts
            else:
                break

        if n_flair_posts_found:
            lt_watchlist_sorted = sorted(d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True)
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    #thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    if int(t_ticker[1]) > 1:
                        s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except:
                    pass
            if n_tickers:
                print("The following stock tickers have been mentioned more than once across the previous watchlists:")
                print(s_watchlist_tickers[:-2]+'\n')
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def popular_tickers(l_args):
    parser = argparse.ArgumentParser(prog='popular',
                                     description="""Print latest popular tickers. [Source: Reddit] """)
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=50,
                        help='limit of posts retrieved per sub reddit.')
    parser.add_argument('-s', "--sub", action="store", dest="s_subreddit", type=str,
                        help="""subreddits to look for tickers, e.g. pennystocks,stocks.
                        Default: pennystocks, RobinHoodPennyStocks, Daytrading, StockMarket, stocks, investing, wallstreetbets""")
    parser.add_argument('-d', "--days", action="store", dest="n_days", type=check_positive, default=1,
                        help="look for the tickers from those n past days.")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        n_ts_after = int((datetime.today() - timedelta(days=ns_parser.n_days)).timestamp())

        if ns_parser.s_subreddit:
            if ',' in ns_parser.s_subreddit:
                l_sub_reddits = ns_parser.s_subreddit.split(',')
            else:
                l_sub_reddits = [ns_parser.s_subreddit]
        else:
            l_sub_reddits = ['pennystocks', 'RobinHoodPennyStocks', 'Daytrading', 'StockMarket', 'stocks', 'investing', 'wallstreetbets']

        d_submission = {}
        d_watchlist_tickers = {}
        l_watchlist_links = list()
        l_watchlist_author = list()

        praw_api = praw.Reddit(client_id=cfg.API_REDDIT_CLIENT_ID,
                               client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                               username=cfg.API_REDDIT_USERNAME,
                               user_agent=cfg.API_REDDIT_USER_AGENT,
                               password=cfg.API_REDDIT_PASSWORD)

        psaw_api = PushshiftAPI()

        for s_sub_reddit in l_sub_reddits:
            print(f"Search for latest tickers under {ns_parser.n_limit} '{s_sub_reddit}' posts")
            submissions = psaw_api.search_submissions(after=int(n_ts_after),
                                                      subreddit=s_sub_reddit,
                                                      limit=ns_parser.n_limit,
                                                      filter=['id'])

            n_tickers = 0
            while True:
                submission = next(submissions, None)
                if submission:
                    # Get more information about post using PRAW api
                    submission = praw_api.submission(id=submission.id)

                    # Ensure that the post hasn't been removed by moderator in the meanwhile,
                    #that there is a description and it's not just an image, that the flair is
                    #meaningful, and that we aren't re-considering same author's content
                    if not submission.removed_by_category and (submission.selftext or submission.title) \
                        and submission.author.name not in l_watchlist_author:
                        ls_text = list()
                        ls_text.append(submission.selftext)
                        ls_text.append(submission.title)

                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            ls_text.append(comment.body)

                        l_tickers_found = list()
                        for s_text in ls_text:
                            for s_ticker in set(re.findall(r'([A-Z]{3,5} )', s_text)):
                                l_tickers_found.append(s_ticker.strip())

                        if l_tickers_found:
                            n_tickers += len(l_tickers_found)

                            # Add another author's name to the parsed watchlists
                            l_watchlist_author.append(submission.author.name)

                            # Lookup stock tickers within a watchlist
                            for key in l_tickers_found:
                                if key in d_watchlist_tickers:
                                    # Increment stock ticker found
                                    d_watchlist_tickers[key] += 1
                                else:
                                    # Initialize stock ticker found
                                    d_watchlist_tickers[key] = 1

                # Check if search_submissions didn't get anymore posts
                else:
                    break

            print(f"  {n_tickers} tickers found.")

        lt_watchlist_sorted = sorted(d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True)
        if lt_watchlist_sorted:
            print(f"\nThe following TOP10 tickers have been mentioned in the last {ns_parser.n_days} days:")
            n_top_stocks = 0
            for t_ticker in lt_watchlist_sorted:
                if n_top_stocks > 9:
                    break
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    #thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    print(f"{t_ticker[1]} {t_ticker[0]}")
                    n_top_stocks += 1
                except:
                    pass
        else:
            print("No tickers found")
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def spac_community(l_args):
    parser = argparse.ArgumentParser(prog='spac_c',
                                     description="""Print other users SPACs announcement under subreddit 'SPACs' [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=10,
                        help='limit of posts with SPACs retrieved')
    parser.add_argument('-p', "--popular", action="store_true", default=False, dest="b_popular",
                        help='popular flag, if true the posts retrieved are based on score rather than time')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        praw_api = praw.Reddit(client_id=cfg.API_REDDIT_CLIENT_ID,
                                client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                                username=cfg.API_REDDIT_USERNAME,
                                user_agent=cfg.API_REDDIT_USER_AGENT,
                                password=cfg.API_REDDIT_PASSWORD)

        d_submission = {}
        d_watchlist_tickers = {}
        l_watchlist_links = list()
        l_watchlist_author = list()

        psaw_api = PushshiftAPI()

        if ns_parser.b_popular:
            submissions = praw_api.subreddit('SPACs').hot(limit=ns_parser.n_limit)
        else:
            submissions = praw_api.subreddit('SPACs').new(limit=ns_parser.n_limit)

        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed  by moderator in the meanwhile,
                #that there is a description and it's not just an image, that the flair is
                #meaningful, and that we aren't re-considering same author's watchlist
                if not submission.removed_by_category and submission.selftext \
                    and submission.author.name not in l_watchlist_author: # and submission.link_flair_text not in ['Yolo', 'Meme'] \

                        # Make sure there is at least 1 ticker found on the post text
                        l_tickers_found = set(re.findall("[A-Z]{3,5}", submission.selftext))
                        if not l_tickers_found:
                            l_tickers_found = set(re.findall("[A-Z]{3,5}", submission.title))

                        if l_tickers_found:
                            # Add another author's name to the parsed watchlists
                            l_watchlist_author.append(submission.author.name)

                            # Lookup stock tickers within a watchlist
                            for key in l_tickers_found:
                                if key in d_watchlist_tickers:
                                    # Increment stock ticker found
                                    d_watchlist_tickers[key] += 1
                                else:
                                    # Initialize stock ticker found
                                    d_watchlist_tickers[key] = 1

                            l_watchlist_links.append(f"https://www.reddit.com{submission.permalink}")
                            # delte below, not necessary I reckon. Probably just link?

                            # Refactor data
                            s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime("%d/%m/%Y %H:%M:%S")
                            s_link = f"https://www.reddit.com{submission.permalink}"
                            s_all_awards = ""
                            for award in submission.all_awardings:
                                s_all_awards += f"{award['count']} {award['name']}\n"
                            s_all_awards = s_all_awards[:-2]

                            # Create dictionary with data to construct dataframe allows to save data
                            d_submission[submission.id] = {
                                                            'created_utc': s_datetime,
                                                            'subreddit': submission.subreddit,
                                                            'link_flair_text': submission.link_flair_text,
                                                            'title':submission.title,
                                                            'score': submission.score,
                                                            'link': s_link,
                                                            'num_comments': submission.num_comments,
                                                            'upvote_ratio': submission.upvote_ratio,
                                                            'awards': s_all_awards
                                                        }

                            # Print post data collected so far
                            print(f"{s_datetime} - {submission.title}")
                            print(f"{s_link}")
                            t_post = PrettyTable(['Subreddit', 'Flair', 'Score', '# Comments', 'Upvote %', "Awards"])
                            t_post.add_row([submission.subreddit, submission.link_flair_text, submission.score,
                                            submission.num_comments,f"{round(100*submission.upvote_ratio)}%", s_all_awards])
                            print(t_post)
                            print("\n")

            # Check if search_submissions didn't get anymore posts
            else:
                break

        if d_watchlist_tickers:
            lt_watchlist_sorted = sorted(d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True)
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    #thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except:
                    pass
            if n_tickers:
                print("The following stock tickers have been mentioned across the previous SPACs:")
                print(s_watchlist_tickers[:-2])
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def spac(l_args):
    parser = argparse.ArgumentParser(prog='spac',
                                     description=""" Show other users SPACs announcement [Reddit] """)
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts with SPACs retrieved.')
    parser.add_argument('-d', "--days", action="store", dest="n_days", type=check_positive, default=5,
                        help="look for the tickers from those n past days.")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        praw_api = praw.Reddit(client_id=cfg.API_REDDIT_CLIENT_ID,
                               client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                               username=cfg.API_REDDIT_USERNAME,
                               user_agent=cfg.API_REDDIT_USER_AGENT,
                               password=cfg.API_REDDIT_PASSWORD)

        d_submission = {}
        d_watchlist_tickers = {}
        l_watchlist_links = list()
        l_watchlist_author = list()

        n_ts_after = int((datetime.today() - timedelta(days=ns_parser.n_days)).timestamp())
        l_sub_reddits = ['pennystocks', 'RobinHoodPennyStocks', 'Daytrading', 'StockMarket', 'stocks', 'investing', 'wallstreetbets']

        warnings.filterwarnings("ignore") # To avoid printing the warning
        psaw_api = PushshiftAPI()
        submissions = psaw_api.search_submissions(after=n_ts_after,
                                                  subreddit=l_sub_reddits,
                                                  q='SPAC|Spac|spac|Spacs|spacs',
                                                  filter=['id'])
        n_flair_posts_found = 0
        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed  by moderator in the meanwhile,
                #that there is a description and it's not just an image, that the flair is
                #meaningful, and that we aren't re-considering same author's watchlist
                if not submission.removed_by_category and submission.selftext \
                    and submission.link_flair_text not in ['Yolo', 'Meme'] \
                    and submission.author.name not in l_watchlist_author:

                        # Make sure there is at least 1 ticker found on the post text
                        l_tickers_found = set(re.findall("[A-Z]{3,5}", submission.selftext))
                        if not l_tickers_found:
                            l_tickers_found = set(re.findall("[A-Z]{3,5}", submission.title))
                        if l_tickers_found:

                            # Add another author's name to the parsed watchlists
                            l_watchlist_author.append(submission.author.name)

                            # Lookup stock tickers within a watchlist
                            for key in l_tickers_found:
                                if key in d_watchlist_tickers:
                                    # Increment stock ticker found
                                    d_watchlist_tickers[key] += 1
                                else:
                                    # Initialize stock ticker found
                                    d_watchlist_tickers[key] = 1

                            l_watchlist_links.append(f"https://www.reddit.com{submission.permalink}")
                            # delte below, not necessary I reckon. Probably just link?

                            # Refactor data
                            s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime("%d/%m/%Y %H:%M:%S")
                            s_link = f"https://www.reddit.com{submission.permalink}"
                            s_all_awards = ""
                            for award in submission.all_awardings:
                                s_all_awards += f"{award['count']} {award['name']}\n"
                            s_all_awards = s_all_awards[:-2]

                            # Create dictionary with data to construct dataframe allows to save data
                            d_submission[submission.id] = {
                                                            'created_utc': s_datetime,
                                                            'subreddit': submission.subreddit,
                                                            'link_flair_text': submission.link_flair_text,
                                                            'title':submission.title,
                                                            'score': submission.score,
                                                            'link': s_link,
                                                            'num_comments': submission.num_comments,
                                                            'upvote_ratio': submission.upvote_ratio,
                                                            'awards': s_all_awards
                                                        }

                            # Print post data collected so far
                            print(f"{s_datetime} - {submission.title}")
                            print(f"{s_link}")
                            t_post = PrettyTable(['Subreddit', 'Flair', 'Score', '# Comments', 'Upvote %', "Awards"])
                            t_post.add_row([submission.subreddit, submission.link_flair_text, submission.score,
                                            submission.num_comments,f"{round(100*submission.upvote_ratio)}%", s_all_awards])
                            print(t_post)
                            print("\n")

                            # Increment count of valid posts found
                            n_flair_posts_found += 1

                # Check if number of wanted posts found has been reached
                if n_flair_posts_found > ns_parser.n_limit-1:
                    break

            # Check if search_submissions didn't get anymore posts
            else:
                break

        '''
        if n_flair_posts_found:
            lt_watchlist_sorted = sorted(d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True)
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    #thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except:
                    pass
            if n_tickers:
                print("The following stock tickers have been mentioned across the previous SPACs:")
                print(s_watchlist_tickers[:-2])
        '''
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def wsb_community(l_args):
    parser = argparse.ArgumentParser(prog='wsb',
                                     description="""Print what WSB gang are up to in subreddit wallstreetbets. [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive,
                        default=10, help='limit of posts to print.')
    parser.add_argument('-n', "--new", action="store_true", default=False, dest="b_new",
                        help='new flag, if true the posts retrieved are based on being more recent rather than their score.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        praw_api = praw.Reddit(client_id=cfg.API_REDDIT_CLIENT_ID,
                                client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                                username=cfg.API_REDDIT_USERNAME,
                                user_agent=cfg.API_REDDIT_USER_AGENT,
                                password=cfg.API_REDDIT_PASSWORD)

        d_submission = {}
        l_watchlist_links = list()

        psaw_api = PushshiftAPI()

        if ns_parser.b_new:
            submissions = praw_api.subreddit('wallstreetbets').new(limit=ns_parser.n_limit)
        else:
            submissions = praw_api.subreddit('wallstreetbets').hot(limit=ns_parser.n_limit)

        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed  by moderator in the meanwhile,
                #that there is a description and it's not just an image, that the flair is
                #meaningful, and that we aren't re-considering same author's watchlist
                if not submission.removed_by_category:

                    l_watchlist_links.append(f"https://www.reddit.com{submission.permalink}")

                    # Refactor data
                    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime("%d/%m/%Y %H:%M:%S")
                    s_link = f"https://www.reddit.com{submission.permalink}"
                    s_all_awards = ""
                    for award in submission.all_awardings:
                        s_all_awards += f"{award['count']} {award['name']}\n"
                    s_all_awards = s_all_awards[:-2]

                    # Create dictionary with data to construct dataframe allows to save data
                    d_submission[submission.id] = {
                                                    'created_utc': s_datetime,
                                                    'subreddit': submission.subreddit,
                                                    'link_flair_text': submission.link_flair_text,
                                                    'title':submission.title,
                                                    'score': submission.score,
                                                    'link': s_link,
                                                    'num_comments': submission.num_comments,
                                                    'upvote_ratio': submission.upvote_ratio,
                                                    'awards': s_all_awards
                                                }

                    # Print post data collected so far
                    print(f"{s_datetime} - {submission.title}")
                    print(f"{s_link}")
                    t_post = PrettyTable(['Subreddit', 'Flair', 'Score', '# Comments', 'Upvote %', "Awards"])
                    t_post.add_row([submission.subreddit, submission.link_flair_text, submission.score,
                                    submission.num_comments,f"{round(100*submission.upvote_ratio)}%", s_all_awards])
                    print(t_post)
                    print("")
            # Check if search_submissions didn't get anymore posts
            else:
                break
            print("")
    except:
        print("")