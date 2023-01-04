"""HackerNews Model"""
__docformat__ = "numpy"


import logging
import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_stories(limit: int = 10) -> pd.DataFrame:
    """Get top stories from HackerNews.
    Parameters
    ----------
    limit: int
        Number of stories to return
    Returns
    -------
    pd.DataFrame
        DataFrame with stories
    """

    res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if res.status_code == 200:
        top_stories = res.json()
        stories = []
        for story_id in top_stories[:limit]:
            story = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            ).json()
            stories.append(story)
        df = pd.DataFrame(stories)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df[["title", "url", "score", "type", "time"]]
        return df
    return pd.DataFrame()
