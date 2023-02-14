"""Substack model"""
__docformat__ = "numpy"

import concurrent.futures
import logging
import textwrap
from typing import List

import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def scrape_substack(url: str) -> List[List[str]]:
    """Helper method to scrape newsletters from substack.
    [Source: substack.com]

    Parameters
    ----------
    url: str
        Url to newsletter on substack domain.

    Returns
    -------
    List[List[str]]
        List of lists containing:
            - title of newsletter
            - url to newsletter
            - str datetime of newsletter [Format: "%Y-%m-%d %H:%M:%S"]
    """

    req = request(url)
    soup = BeautifulSoup(req.text, features="lxml")
    results: List[List[str]] = []
    archive = soup.find("div", class_="portable-archive-list")
    if archive:
        posts = archive.find_all(
            "div", class_="post-preview portable-archive-post has-image has-author-line"
        )
        for post in posts:
            title: str = post.a.text
            post_url: str = post.a["href"]
            time: str = post.find("time").get("datetime")
            results.append([title, post_url, time])
    return results


@log_start_end(log=logger)
def get_newsletters() -> pd.DataFrame:
    """Scrape all substack newsletters from url list.
    [Source: substack.com]

    Returns
    -------
    pd.DataFrame
        DataFrame with recent news from most popular DeFi related newsletters.
    """

    urls = [
        "https://defiweekly.substack.com/archive",
        "https://newsletter.thedefiant.io/archive",
        "https://thedailygwei.substack.com/archive",
        "https://todayindefi.substack.com/archive",
        "https://newsletter.banklesshq.com/archive",
        "https://defislate.substack.com/archive",
    ]

    threads = len(urls)
    newsletters = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for newsletter in executor.map(scrape_substack, urls):
            try:
                newsletters.append(pd.DataFrame(newsletter))
            except KeyError as e:
                logger.exception(str(e))
                console.print(e, "\n")
                continue

    df = pd.concat(newsletters, ignore_index=True)
    df.columns = ["Title", "Link", "Date"]

    df["Title"] = df["Title"].apply(lambda x: "".join(i for i in x if ord(i) < 128))
    df["Date"] = df["Date"].apply(
        lambda x: parser.parse(x).strftime("%Y-%m-%d %H:%M:%S")
    )
    df["Title"] = df["Title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
    )
    return (
        df[["Title", "Date", "Link"]]
        .sort_values(by="Date", ascending=False)
        .reset_index(drop="index")
    )
