"""Reddit Helpers."""
__docformat__ = "numpy"

import re
from typing import List

import praw

from openbb_terminal.core.models import UserModel


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
