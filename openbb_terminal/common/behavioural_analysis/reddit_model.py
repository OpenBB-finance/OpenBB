"""Reddit Model."""
__docformat__ = "numpy"
# pylint:disable=C0302

import logging
import warnings
from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd
import praw
from pmaw import PushshiftAPI
from prawcore.exceptions import ResponseException
from sklearn.feature_extraction import _stop_words
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from openbb_terminal.common.behavioural_analysis.reddit_helpers import (
    RedditResponses,
    find_tickers,
    get_praw_api,
    reddit_requirements,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

l_sub_reddits = [
    "Superstonk",
    "pennystocks",
    "RobinHoodPennyStocks",
    "Daytrading",
    "StockMarket",
    "stocks",
    "investing",
    "wallstreetbets",
]


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_popular_tickers(
    limit: int = 10, post_limit: int = 50, subreddits: str = ""
) -> pd.DataFrame:
    """Get popular tickers from list of subreddits [Source: reddit].

    Parameters
    ----------
    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.

    Returns
    -------
    pd.DataFrame
        DataFrame of top tickers from supplied subreddits
    """
    current_user = get_current_user()
    sub_reddit_list = (
        (subreddits.split(",") if "," in subreddits else [subreddits])
        if subreddits
        else l_sub_reddits
    )

    praw_api = get_praw_api(current_user)
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    pmaw_api = PushshiftAPI()

    responses = RedditResponses()
    for s_sub_reddit in sub_reddit_list:
        console.print(
            f"Searching for tickers in latest {post_limit} '{s_sub_reddit}' posts"
        )
        warnings.filterwarnings(
            "ignore", message=".*Not all PushShift shards are active.*"
        )
        submissions = pmaw_api.search_submissions(
            subreddit=s_sub_reddit,
            limit=post_limit,
            filter=["id"],
        )

        count = responses.gather(praw_api, submissions.responses)
        responses.validate()
        console.print(f"  {count} potential tickers found.")

    return responses.to_df().head(limit)


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_spac_community(
    limit: int = 10, popular: bool = False
) -> Tuple[pd.DataFrame, dict]:
    """Get top tickers from r/SPACs [Source: reddit].

    Parameters
    ----------
    limit : int
        Number of posts to look at
    popular : bool
        Search by hot instead of new

    Returns
    -------
    Tuple[pd.DataFrame, dict]
        Dataframe of reddit submission,
        Dictionary of tickers and number of mentions.
    """
    current_user = get_current_user()

    praw_api = get_praw_api(current_user)
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame(), {}

    d_watchlist_tickers: dict = {}
    l_watchlist_author = []

    if popular:
        submissions = praw_api.subreddit("SPACs").hot(limit=limit)
    else:
        submissions = praw_api.subreddit("SPACs").new(limit=limit)

    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for sub in submissions:
            if not sub:
                break

            # Get more information about post using PRAW api
            submission = praw_api.submission(id=sub.id)

            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if (
                not submission.removed_by_category
                and submission.selftext
                and submission.link_flair_text not in ["Yolo", "Meme"]
                and submission.author.name not in l_watchlist_author
            ):
                l_tickers_found = find_tickers(submission)

                if l_tickers_found:
                    # Add another author's name to the parsed watchlists
                    l_watchlist_author.append(submission.author.name)
                    s_datetime = datetime.utcfromtimestamp(
                        submission.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    s_link = f"https://old.reddit.com{submission.permalink}"
                    s_all_awards = "".join(
                        f"{award['count']} {award['name']}\n"
                        for award in submission.all_awardings
                    )

                    s_all_awards = s_all_awards[:-2]

                    data = [
                        s_datetime,
                        submission.subreddit,
                        submission.link_flair_text,
                        submission.title,
                        submission.score,
                        submission.num_comments,
                        f"{round(100 * submission.upvote_ratio)}%",
                        s_all_awards,
                        s_link,
                    ]
                    subs.loc[len(subs)] = data
                    # Lookup stock tickers within a watchlist
                    for key in l_tickers_found:
                        if key in d_watchlist_tickers:
                            # Increment stock ticker found
                            d_watchlist_tickers[key] += 1
                        else:
                            # Initialize stock ticker found
                            d_watchlist_tickers[key] = 1

    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")

    return subs, d_watchlist_tickers


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_wsb_community(limit: int = 10, new: bool = False) -> pd.DataFrame:
    """Get wsb posts [Source: reddit].

    Parameters
    ----------
    limit : int, optional
        Number of posts to get, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of reddit submissions
    """
    current_user = get_current_user()

    praw_api = get_praw_api(current_user)
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    if new:
        submissions = praw_api.subreddit("wallstreetbets").new(limit=limit)
    else:
        submissions = praw_api.subreddit("wallstreetbets").hot(limit=limit)

    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for submission in submissions:
            submission_ = praw_api.submission(submission.id)
            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if not submission_.removed_by_category:
                s_datetime = datetime.utcfromtimestamp(
                    submission_.created_utc
                ).strftime("%Y-%m-%d %H:%M:%S")
                s_link = f"https://old.reddit.com{submission_.permalink}"
                s_all_awards = "".join(
                    f"{award['count']} {award['name']}\n"
                    for award in submission_.all_awardings
                )

                s_all_awards = s_all_awards[:-2]

                data = [
                    s_datetime,
                    submission_.subreddit,
                    submission_.link_flair_text,
                    submission_.title,
                    submission_.score,
                    submission_.num_comments,
                    f"{round(100 * submission_.upvote_ratio)}%",
                    s_all_awards,
                    s_link,
                ]
                subs.loc[len(subs)] = data
    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")
    return subs


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_due_dilligence(
    limit: int = 5, n_days: int = 3, show_all_flairs: bool = False
) -> pd.DataFrame:
    """Get due diligence posts from list of subreddits [Source: reddit].

    Parameters
    ----------
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)

    Returns
    -------
    pd.DataFrame
        Dataframe of submissions
    """
    current_user = get_current_user()

    praw_api = get_praw_api(current_user)
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    pmaw_api = PushshiftAPI()

    n_ts_after = int((datetime.today() - timedelta(days=n_days)).timestamp())
    l_flair_text = [
        "DD",
        "technical analysis",
        "Catalyst",
        "News",
        "Advice",
        "Chart",
        "Charts and Setups",
        "Fundamental Analysis",
        "forex",
        "Trade Idea",
    ]
    l_sub_reddits_dd = [
        "pennystocks",
        "RobinHoodPennyStocks",
        "Daytrading",
        "StockMarket",
        "stocks",
        "investing",
        "wallstreetbets",
        "forex",
        "Forexstrategy",
    ]

    submissions = pmaw_api.search_submissions(
        after=int(n_ts_after),
        subreddit=l_sub_reddits_dd,
        filter=["id"],
    )
    n_flair_posts_found = 0
    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for submission in submissions.responses:
            # Get more information about post using PRAW api
            submission_ = praw_api.submission(id=submission["id"])

            # Ensure that the post hasn't been removed in the meanwhile
            # Either just filter out Yolo, and Meme flairs, or focus on DD, based on b_DD flag
            if (
                not submission_.removed_by_category
                and submission_.link_flair_text in l_flair_text,
                submission_.link_flair_text not in ["Yolo", "Meme"],
            )[show_all_flairs]:
                s_datetime = datetime.utcfromtimestamp(
                    submission_.created_utc
                ).strftime("%Y-%m-%d %H:%M:%S")
                s_link = f"https://old.reddit.com{submission_.permalink}"
                s_all_awards = "".join(
                    f"{award['count']} {award['name']}\n"
                    for award in submission_.all_awardings
                )

                s_all_awards = s_all_awards[:-2]

                data = [
                    s_datetime,
                    submission_.subreddit,
                    submission_.link_flair_text,
                    submission_.title,
                    submission_.score,
                    submission_.num_comments,
                    f"{round(100 * submission_.upvote_ratio)}%",
                    s_all_awards,
                    s_link,
                ]
                subs.loc[len(subs)] = data
                # Increment count of valid posts found
                n_flair_posts_found += 1

            # Check if number of wanted posts found has been reached
            if n_flair_posts_found > limit - 1:
                break
    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")
    return subs


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_posts_about(
    symbol: str,
    limit: int = 100,
    sortby: str = "relevance",
    time_frame: str = "week",
    full_search: bool = True,
    subreddits: str = "all",
) -> Tuple[pd.DataFrame, list, float]:
    """Find posts related to a specific search term in Reddit.

    Parameters
    ----------
    symbol: str
        Ticker symbol to search for
    limit: int
        Number of posts to get per subreddit
    sortby: str
        Search type (Possibilities: "relevance", "hot", "top", "new", or "comments")
    time_frame: str
        Relative time of post (Possibilities: "hour", "day", "week", "month", "year", "all")
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits

    Returns
    -------
    Tuple[pd.DataFrame, list, float]:
        Dataframe of submissions related to the search term,
        List of polarity scores,
        Average polarity score.
    """
    current_user = get_current_user()

    praw_api = get_praw_api(current_user)
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    subreddits_l = subreddits.split(",")
    posts = []
    post_ids = set()
    console.print("Searching through subreddits for posts.")
    for sub_str in tqdm(subreddits_l):
        try:
            subreddit = praw_api.subreddit(sub_str)
        except Exception:
            console.print("Invalid subreddit name {sub_str}, skipping")
            continue
        submissions = subreddit.search(
            query=symbol,
            limit=limit,
            sort=sortby,
            time_filter=time_frame,
        )
        for sub in submissions:
            if (
                sub.selftext
                and sub.title
                and not sub.removed_by_category
                and sub.id not in post_ids
            ):
                post_ids.add(sub.id)
                posts.append(sub)

    polarity_scores = []
    post_data = []
    console.print("Analyzing each post...")
    for p in tqdm(posts):
        texts = [p.title, p.selftext]
        if full_search:
            top_level_comments = get_comments(p)
            texts.extend(top_level_comments)
        preprocessed_text = clean_reddit_text(texts)
        sentiment = get_sentiment(preprocessed_text)
        polarity_scores.append(sentiment)
        post_data.append([p.title, sentiment])

    avg_polarity = sum(polarity_scores) / len(polarity_scores)

    columns = ["Title", "Polarity Score"]
    df = pd.DataFrame(post_data, columns=columns)

    return df, polarity_scores, avg_polarity


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_comments(
    post: praw.models.reddit.submission.Submission,
) -> List[praw.models.reddit.comment.Comment]:
    """Recursively gets comments from a post.

    Parameters
    ----------
    post: praw.models.reddit.submission.Submission
        Post to get comments from

    Returns
    -------
    list[praw.models.reddit.comment.Comment]
        List of all comments on the post
    """

    def get_more_comments(comments):
        sub_top_level_comments = []
        for comment in comments:
            if isinstance(comment, praw.models.reddit.comment.Comment):
                sub_top_level_comments.append(comment.body)
            else:
                sub_comments = get_more_comments(comment.comments())
                sub_top_level_comments.extend(sub_comments)
        return sub_top_level_comments

    if post.comments:
        return get_more_comments(post.comments)
    return []


@log_start_end(log=logger)
def clean_reddit_text(docs: List[str]) -> List[str]:
    """Tokenize and clean a list of documents for sentiment analysis.

    Parameters
    ----------
    docs: list[str]
        A list of documents to prepare for sentiment analysis

    Returns
    -------
    list[str]
        List of cleaned and prepared docs
    """
    stop_words = _stop_words.ENGLISH_STOP_WORDS
    clean_docs = []
    docs = [doc.lower().strip() for doc in docs]

    for doc in docs:
        clean_doc = []
        tokens = doc.split()
        for tok in tokens:
            clean_tok = [c for c in tok if c.isalpha()]
            tok_ = "".join(clean_tok)
            if tok_ not in stop_words:
                clean_doc.append(tok_)
        clean_docs.append(" ".join(clean_doc))
    return clean_docs


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def get_sentiment(post_data: List[str]) -> float:
    """Find the sentiment of a post and related comments.

    Parameters
    ----------
    post_data: list[str]
        A post and its comments in string form

    Returns
    -------
    float
        A number in the range [-1, 1] representing sentiment
    """
    analyzer = SentimentIntensityAnalyzer()
    post_data_l = " ".join(post_data)
    sentiment = analyzer.polarity_scores(post_data_l)
    score = sentiment["pos"] - sentiment["neg"]
    return (score - 0.06) * 8
