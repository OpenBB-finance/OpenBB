"""Substack model"""
__docformat__ = "numpy"

import textwrap
import concurrent.futures
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser


def scrape_substack(url: str) -> list:
    """Helper method to scrape newsletters from substack.
    [Source: substack.com]

    Parameters
    ----------
    url: str
        Url to newsletter on substack domain.

    Returns
    -------
    list
        list of news from given newsletter
    """

    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="lxml")
    results = []
    posts = soup.find("div", class_="portable-archive-list").find_all(
        "div", class_="post-preview portable-archive-post has-image has-author-line"
    )
    for post in posts:
        title, url, time = (
            post.a.text,
            post.a["href"],
            post.find("time").get("datetime"),
        )
        results.append([title, url, time])
    return results


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
                print(e, "\n")
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
