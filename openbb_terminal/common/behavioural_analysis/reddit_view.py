"""Reddit View"""
__docformat__ = "numpy"

import logging
import os
import warnings
from datetime import datetime
from typing import Dict, Optional, Union

import finviz
import matplotlib.pyplot as plt
import pandas as pd
import praw
import seaborn as sns

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.behavioural_analysis import reddit_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, print_rich_table
from openbb_terminal.rich_config import console

# pylint: disable=R0913,C0302
logger = logging.getLogger(__name__)


# TODO: Test OpenBBFigure conversion


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def print_and_record_reddit_post(
    submissions_dict: Dict, submission: praw.models.reddit.submission.Submission
):
    """Prints reddit submission.

    Parameters
    ----------
    submissions_dict : Dict
        Dictionary for storing reddit post information
    submission : praw.models.reddit.submission.Submission
        Submission to show
    """
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    s_link = f"https://old.reddit.com{submission.permalink}"
    s_all_awards = "".join(
        f"{award['count']} {award['name']}\n" for award in submission.all_awardings
    )

    s_all_awards = s_all_awards[:-2]
    # Create dictionary with data to construct dataframe allows to save data
    submissions_dict[submission.id] = {
        "created_utc": s_datetime,
        "subreddit": submission.subreddit,
        "link_flair_text": submission.link_flair_text,
        "title": submission.title,
        "score": submission.score,
        "link": s_link,
        "num_comments": submission.num_comments,
        "upvote_ratio": submission.upvote_ratio,
        "awards": s_all_awards,
    }
    # Print post data collected so far
    console.print(f"[yellow]{s_datetime}[/yellow] - {submission.title}")
    console.print(f"[blue]{s_link}[/blue]\n")
    columns = ["Subreddit", "Flair", "Score", "# Comments", "Upvote %", "Awards"]
    data = [
        submission.subreddit,
        submission.link_flair_text,
        submission.score,
        submission.num_comments,
        f"{round(100 * submission.upvote_ratio)}%",
        s_all_awards,
    ]
    df = pd.DataFrame([data], columns=columns)
    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Reddit Submission"
    )


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def print_reddit_post(sub: tuple):
    """Prints reddit submission.

    Parameters
    ----------
    sub : tuple
        Row from submissions dataframe
    """

    sub_list = list(sub[1])
    date = sub_list[0]
    title = sub_list[3]
    link = sub_list[-1]
    console.print(f"[yellow]{date}[/yellow] - {title}")
    console.print(f"[blue]{link}[/blue]\n")
    columns = [
        "Subreddit",
        "Flair",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
    ]

    print_rich_table(
        pd.DataFrame(sub[1][columns]).T,
        headers=columns,
        show_index=False,
        title="Reddit Submission",
    )


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_watchlist(limit: int = 5):
    """Prints other users watchlist. [Source: Reddit].

    Parameters
    ----------
    limit: int
        Maximum number of submissions to look at
    """
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_watchlists(limit)
    if subs:
        for sub in subs:
            print_and_record_reddit_post({}, sub)
            console.print("")

        if n_flair_posts_found > 0:
            lt_watchlist_sorted = sorted(
                d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
            )
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    # thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    if int(t_ticker[1]) > 1:
                        s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except Exception:
                    # console.print(e, "\n")
                    pass  # noqa
            if n_tickers:
                console.print(
                    "The following stock tickers have been mentioned more than once across the previous watchlists:"
                )
                console.print(s_watchlist_tickers[:-2] + "\n")


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_popular_tickers(
    limit: int = 10,
    post_limit: int = 50,
    subreddits: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Prints table showing latest popular tickers. [Source: Reddit].

    Parameters
    ----------
    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    export : str
        Format to export dataframe
    """
    popular_tickers_df = reddit_model.get_popular_tickers(limit, post_limit, subreddits)
    if not popular_tickers_df.empty:
        print_rich_table(
            popular_tickers_df,
            headers=list(popular_tickers_df.columns),
            show_index=False,
            title=f"The following TOP {limit} tickers have been mentioned",
            export=bool(export),
        )
    else:
        console.print("No tickers found")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "popular",
        popular_tickers_df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_spac_community(limit: int = 10, popular: bool = False):
    """Prints tickers mentioned in r/SPACs [Source: Reddit].

    Parameters
    ----------
    limit: int
        Number of posts to look through
    popular: bool
        Search by popular instead of new
    """
    subs, d_watchlist_tickers = reddit_model.get_spac_community(limit, popular)
    if not subs.empty:
        for sub in subs.iterrows():
            print_reddit_post(sub)
            console.print("")

        if d_watchlist_tickers:
            lt_watchlist_sorted = sorted(
                d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
            )
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    # thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    if int(t_ticker[1]) > 1:
                        s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except Exception:
                    # console.print(e, "\n")
                    pass  # noqa

            if n_tickers:
                console.print(
                    "The following stock tickers have been mentioned more than once across the previous SPACs:"
                )
                console.print(s_watchlist_tickers[:-2])


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_spac(limit: int = 5):
    """Prints posts containing 'spac' in top communities.

    Parameters
    ----------
    limit: int
        Number of posts to get from each subreddit
    """
    warnings.filterwarnings("ignore")  # To avoid printing the warning
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_spac(limit)
    if not subs.empty:
        for sub in subs.iterrows():
            print_reddit_post(sub)
            console.print("")

        if n_flair_posts_found > 0:
            lt_watchlist_sorted = sorted(
                d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
            )
            s_watchlist_tickers = ""
            n_tickers = 0
            for t_ticker in lt_watchlist_sorted:
                try:
                    # If try doesn't trigger exception, it means that this stock exists on finviz
                    # thus we can print it.
                    finviz.get_stock(t_ticker[0])
                    if int(t_ticker[1]) > 1:
                        s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
                except Exception:
                    pass  # noqa
            if n_tickers:
                console.print(
                    "The following stock tickers have been mentioned more than once across the previous SPACs:"
                )
                console.print(s_watchlist_tickers[:-2])


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_wsb_community(limit: int = 10, new: bool = False):
    """Prints WSB posts.

    Parameters
    ----------
    limit : int, optional
        Number of posts to look at, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False
    """
    subs = reddit_model.get_wsb_community(limit, new)
    if not subs.empty:
        for sub in subs.iterrows():
            print_reddit_post(sub)
            console.print("")


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_due_diligence(
    symbol: str, limit: int = 10, n_days: int = 3, show_all_flairs: bool = False
):
    """Prints Reddit due diligence data for a given ticker.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)
    """
    subs = reddit_model.get_due_dilligence(symbol, limit, n_days, show_all_flairs)
    if not subs.empty:
        for sub in subs.iterrows():
            print_reddit_post(sub)
            console.print("")
    else:
        console.print(f"No DD posts found for {symbol}\n")


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def display_redditsent(
    symbol: str,
    sortby: str = "relevance",
    limit: int = 100,
    graphic: bool = False,
    time_frame: str = "week",
    full_search: bool = True,
    subreddits: str = "all",
    display: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Reddit sentiment about a search term. Prints table showing if display is True.

    Parameters
    ----------
    symbol: str
        The ticker symbol being search for in Reddit
    sortby: str
        Type of search
    limit: str
        Number of posts to get at most
    graphic: bool
        Displays box and whisker plot
    time_frame: str
        Time frame for search
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits
    display: bool
        Enable printing of raw sentiment values for each post
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]]
        If supplied, expect 1 external axis
    """
    fig = OpenBBFigure()

    df, polarity_scores, avg_polarity = reddit_model.get_posts_about(
        symbol, limit, sortby, time_frame, full_search, subreddits
    )

    if df.empty:
        return console.print(f"No posts for {symbol} found")

    if display:
        print_rich_table(df=df, export=bool(export))

    if not fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "polarity_scores",
            df,
            sheet_name,
        )

    console.print(f"Sentiment Analysis for {symbol} is {avg_polarity}\n")

    if graphic:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        sns.boxplot(x=polarity_scores, ax=ax)
        ax.set_title(f"Sentiment Score of {symbol}")
        ax.set_xlabel("Sentiment Score")

        if not external_axes:
            theme.visualize_output()

        fig = OpenBBFigure(
            title=f"Sentiment Score of {symbol}", xaxis_title="Sentiment Score"
        )
        fig.add_bar(x=polarity_scores)

        if fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "polarity_scores",
                df,
                sheet_name,
                fig,
            )

        return fig.show(external=external_axes)

    return None
