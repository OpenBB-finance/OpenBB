import argparse
from datetime import datetime, timedelta

import praw
from prettytable import PrettyTable
from psaw import PushshiftAPI

import config_terminal as cfg
from helper_funcs import check_positive


# -------------------------------------------------------------------------------------------------------------------
def due_diligence(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='red',
                                     description="""Print top stock's due diligence from other users. [Source: Reddit] """)

    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts to retrieve.')
    parser.add_argument('-d', "--days", action="store", dest="n_days", type=check_positive, default=3,
                        help="number of prior days to look for.")
    parser.add_argument('-a', "--all", action="store_true", dest="b_all", default=False,
                        help="""search through all flairs (apart from Yolo and Meme), otherwise we focus on
                        specific flairs: DD, technical analysis, Catalyst, News, Advice, Chart """)

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

        psaw_api = PushshiftAPI()

        n_ts_after = int((datetime.today() - timedelta(days=ns_parser.n_days)).timestamp())
        l_flair_text = ['DD', 'technical analysis', 'Catalyst', 'News', 'Advice', 'Chart']
        l_sub_reddits = ['pennystocks', 'RobinHoodPennyStocks', 'Daytrading', 'StockMarket', 'stocks', 'investing', 'wallstreetbets']

        submissions = psaw_api.search_submissions(after=int(n_ts_after),
                                                  subreddit=l_sub_reddits,
                                                  q=s_ticker,
                                                  filter=['id'])
        d_submission = {}
        n_flair_posts_found = 0
        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed in the meanwhile
                if not submission.removed_by_category:

                    # Either just filter out Yolo, and Meme flairs, or focus on DD, based on b_DD flag
                    if (submission.link_flair_text in l_flair_text,
                        submission.link_flair_text not in ['Yolo', 'Meme'])[ns_parser.b_all]:

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

                            # If needed, submission.comments could give us the top comments

                            # Increment count of valid posts found
                            n_flair_posts_found += 1

                # Check if number of wanted posts found has been reached
                if n_flair_posts_found > ns_parser.n_limit-1:
                    break

            # Check if search_submissions didn't get anymore posts
            else:
                break

        print(f"{('No more posts with specified requirements found.', '')[n_flair_posts_found > ns_parser.n_limit-1]}")
        # Create df with found data. Useful for saving all info in excel file.
        #df_submissions = pd.DataFrame.from_dict(d_submission, orient='index', columns=list(d_submission[next(iter(d_submission.keys()))].keys()))
        #df_submissions.sort_values(by=['created_utc'], inplace=True, ascending=True)

    except:
        print("")
