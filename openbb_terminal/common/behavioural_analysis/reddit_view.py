"""Reddit View."""
__docformat__ = "numpy"

import io
import logging
import os
import textwrap
from datetime import datetime
from typing import Dict, Optional, Union

import pandas as pd
import praw
from finvizfinance.screener.ticker import Ticker

from openbb_terminal import OpenBBFigure, rich_config
from openbb_terminal.common.behavioural_analysis import reddit_model
from openbb_terminal.common.behavioural_analysis.reddit_helpers import (
    reddit_requirements,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

# pylint: disable=R0913,C0302
logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def print_and_record_reddit_post(
    submissions_dict: Dict, submission: praw.models.reddit.submission.Submission
):
    """Print reddit submission.

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
@check_api_key(reddit_requirements)
def print_reddit_post(sub: tuple):
    """Print reddit submission.

    Parameters
    ----------
    sub : tuple
        Row from submissions dataframe
    """
    sub_list = list(sub[1])
    date = sub_list[0]
    title = sub_list[3]
    link = sub_list[-1]

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
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
@check_api_key(reddit_requirements)
def display_popular_tickers(
    limit: int = 10,
    post_limit: int = 50,
    subreddits: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Print table showing latest popular tickers. [Source: Reddit].

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
    if popular_tickers_df.empty:
        console.print("No tickers found")
        return
    print_rich_table(
        popular_tickers_df,
        headers=list(popular_tickers_df.columns),
        show_index=True,
        title=f"The following TOP {limit} tickers have been mentioned",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "popular",
        popular_tickers_df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def display_spac_community(limit: int = 10, popular: bool = False):
    """Print tickers mentioned in r/SPACs [Source: Reddit].

    Parameters
    ----------
    limit: int
        Number of posts to look through
    popular: bool
        Search by popular instead of new
    """
    subs, d_watchlist_tickers = reddit_model.get_spac_community(limit, popular)
    if not subs.empty:
        if d_watchlist_tickers:
            lt_watchlist_sorted = sorted(
                d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
            )
            s_watchlist_tickers = ""
            n_tickers = 0
            tickers = Ticker()
            ticker_list = tickers.screener_view()
            # validate against a list of all tickers
            for t_ticker in lt_watchlist_sorted:
                if t_ticker[0] in ticker_list:
                    if int(t_ticker[1]) > 1:
                        s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                    n_tickers += 1
            if n_tickers:
                console.print(
                    "The following stock tickers have been mentioned more than once across the previous posts on "
                    "r/spaccs: "
                )
                console.print(s_watchlist_tickers[:-2])
        print_rich_table(
            pd.DataFrame(subs),
            show_index=False,
            title="Reddit Submission",
        )


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def display_wsb_community(limit: int = 10, new: bool = False):
    """Print WSB posts.

    Parameters
    ----------
    limit : int, optional
        Number of posts to look at, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False
    """
    subs = reddit_model.get_wsb_community(limit, new)
    # I am not proud of this, but it works to eliminate the max recursion bug
    subs = pd.read_csv(io.StringIO(subs.to_csv()), index_col=0).fillna("-")
    if not subs.empty:
        print_rich_table(subs)


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
def display_due_diligence(
    limit: int = 10, n_days: int = 3, show_all_flairs: bool = False
):
    """Print Reddit due diligence data for a given ticker.

    Parameters
    ----------
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)
    """
    subs = reddit_model.get_due_dilligence(limit, n_days, show_all_flairs)
    if not subs.empty:
        for sub in subs.iterrows():
            print_reddit_post(sub)
            console.print("")
    else:
        console.print("No DD posts found\n")


@log_start_end(log=logger)
@check_api_key(reddit_requirements)
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
    """Plot Reddit sentiment about a search term. Prints table showing if display is True.

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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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
        df["Title"] = df["Title"].apply(
            lambda x: "<br>".join(textwrap.wrap(str(x), 50))
        )
        fig = OpenBBFigure(
            title=f"Sentiment Score of {symbol}",
            xaxis_title="Sentiment Score",
        )
        fig.add_bar(
            x=polarity_scores,
            customdata=df["Title"],
            hovertemplate="%{customdata}<extra></extra>",
        )
        fig.update_layout(hovermode="y")

        # remove y ticks of graph object because number based index doesn't make sense here
        fig.layout.yaxis.tickvals = []

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
