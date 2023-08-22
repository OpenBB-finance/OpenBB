"""Reddit Helpers."""
__docformat__ = "numpy"

import logging
import re
import urllib.request
from typing import List

import pandas as pd
import praw
from prawcore.exceptions import ResponseException

from openbb_terminal.core.models import UserModel
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

reddit_requirements = [
    "API_REDDIT_CLIENT_ID",
    "API_REDDIT_CLIENT_SECRET",
    "API_REDDIT_USERNAME",
    "API_REDDIT_USER_AGENT",
    "API_REDDIT_PASSWORD",
]


def find_tickers(submission: praw.models.reddit.submission.Submission) -> List[str]:
    """Extract potential tickers from reddit submission.

    Parameters
    ----------
    submission : praw.models.reddit.submission.Submission
        Reddit post to scan

    Returns
    -------
    List[str]
        List of potential tickers
    """
    ls_text = [submission.selftext, submission.title]
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        ls_text.append(comment.body)

    l_tickers_found = []
    for s_text in ls_text:
        for s_ticker in set(re.findall(r"([A-Z]{3,5})", s_text)):
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found


def get_praw_api(current_user: UserModel) -> praw.Reddit:
    """Get praw api.

    Parameters
    ----------
    current_user : UserModel
        The user model

    Returns
    -------
    praw.Reddit
        Praw api
    """
    # See https://github.com/praw-dev/praw/issues/1016 regarding praw arguments
    praw_api = praw.Reddit(
        client_id=current_user.credentials.API_REDDIT_CLIENT_ID,
        client_secret=current_user.credentials.API_REDDIT_CLIENT_SECRET,
        username=current_user.credentials.API_REDDIT_USERNAME,
        user_agent=current_user.credentials.API_REDDIT_USER_AGENT,
        password=current_user.credentials.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    return praw_api


def has_author(submission_, authors) -> bool:
    """Check if submission has author."""
    return (
        hasattr(submission_, "author")
        and hasattr(submission_.author, "name")
        and submission_.author.name not in authors
    )


def has_content(submission_) -> bool:
    """Check if submission has text or title."""
    return hasattr(submission_, "selftext") or hasattr(submission_, "title")


class RedditResponses:
    tickers: dict = {}
    authors: List[str] = []

    def __init__(self):
        pass

    def gather(self, praw_api, responses) -> int:
        count = 0
        for submission in responses:
            try:
                # Get more information about post using PRAW api
                submission_ = praw_api.submission(id=submission["id"])

                # Ensure that the post hasn't been removed by moderator in the meanwhile,
                # that there is a description and it's not just an image, that the flair is
                # meaningful, and that we aren't re-considering same author's content

                if (
                    submission_ is not None
                    and not submission_.removed_by_category
                    and has_content(submission_)
                    and has_author(submission_, self.authors)
                ):
                    l_tickers_found = find_tickers(submission_)

                    if l_tickers_found:
                        count += len(l_tickers_found)

                        # Add another author's name to the parsed watchlists
                        self.authors.append(submission_.author.name)

                        # Lookup stock tickers within a watchlist
                        for key in l_tickers_found:
                            if key in self.tickers:
                                # Increment stock ticker found
                                self.tickers[key] += 1
                            else:
                                # Initialize stock ticker found
                                self.tickers[key] = 1

            except ResponseException as e:
                logger.exception("Invalid response: %s", str(e))

                if "received 401 HTTP response" in str(e):
                    console.print("[red]Invalid API Key[/red]\n")
                else:
                    console.print(f"[red]Invalid response: {str(e)}[/red]\n")
                return 0
        return count

    def validate(
        self,
        url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/all/all_tickers.txt",
    ) -> None:
        """Validate tickers."""
        valids = []
        with urllib.request.urlopen(url) as file:  # noqa: S310
            for line in file:
                new_item = line.decode("utf-8").replace("\n", "").strip()
                valids.append(new_item)

        for key in list(self.tickers.keys()):
            if key not in valids:
                self.tickers.pop(key)

    def to_df(self) -> pd.DataFrame:
        popularity = pd.DataFrame.from_dict(self.tickers, orient="index")
        popularity.columns = ["Mentions"]
        popularity = popularity.sort_values(by=["Mentions"], ascending=False)
        return popularity
