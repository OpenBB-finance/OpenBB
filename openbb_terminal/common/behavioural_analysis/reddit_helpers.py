"""Reddit Helpers"""
__docformat__ = "numpy"

import re
from typing import List

import praw


def find_tickers(submission: praw.models.reddit.submission.Submission) -> List[str]:
    """Extracts potential tickers from reddit submission.

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
        for s_ticker in set(re.findall(r"([A-Z]{3,5} )", s_text)):
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found
