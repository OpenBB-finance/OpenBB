"""Blockchain Center Model"""
from typing import List, Union
import pandas as pd
import requests
from requests.adapters import HTTPAdapter, RetryError
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import get_user_agent
from gamestonk_terminal.rich_config import console

HACKS_COLUMNS = ["Platform", "Date", "Amount [$]", "Audit", "Slug", "URL"]

POSSIBLE_SLUGS = [
    "polynetwork-rekt",
    "bitmart-rekt",
    "compound-rekt",
    "vulcan-forged-rekt",
    "cream-rekt-2",
    "badger-rekt",
    "ascendex-rekt",
    "easyfi-rekt",
    "uranium-rekt",
    "bzx-rekt",
    "pancakebunny-rekt",
    "epic-hack-homie",
    "alpha-finance-rekt",
    "veefinance-rekt",
    "cryptocom-rekt",
    "meerkat-finance-bsc-rekt",
    "monox-rekt",
    "spartan-rekt",
    "grim-finance-rekt",
    "stablemagnet-rekt",
    "paid-rekt",
    "harvest-finance-rekt",
    "xtoken-rekt",
    "popsicle-rekt",
    "pickle-finance-rekt",
    "cream-rekt",
    "snowdog-rekt",
    "bearn-rekt",
    "indexed-finance-rekt",
    "eminence-rekt-in-prod",
    "furucombo-rekt",
    "deathbed-confessions-c3pr",
    "value-rekt3",
    "yearn-rekt",
    "arbix-rekt",
    "rari-capital-rekt",
    "value-rekt2",
    "cover-rekt",
    "punkprotocol-rekt",
    "visor-finance-rekt",
    "thorchain-rekt2",
    "hack-epidemic",
    "lcx-rekt",
    "anyswap-rekt",
    "warp-finance-rekt",
    "burgerswap-rekt",
    "value-defi-rekt",
    "alchemix-rekt",
    "belt-rekt",
    "bondly-rekt",
    "roll-rekt",
    "thorchain-rekt",
    "xtoken-rekt-x2",
    "11-rekt",
    "chainswap-rekt",
    "daomaker-rekt",
    "jaypegs-automart-rekt",
    "pancakebunny2-rekt",
    "au-dodo-rekt",
    "akropolis-rekt",
    "bent-finance",
    "8ight-finance-rekt",
    "levyathan-rekt",
    "the-big-combo",
    "autoshark-rekt",
    "merlinlabs-rekt",
    "merlin2-rekt",
    "merlin3-rekt",
    "saddle-finance-rekt",
    "safedollar-rekt",
]


def _retry_session(
    url: str, retries: int = 3, backoff_factor: float = 1.0
) -> requests.Session:
    """Helper methods that retries to make request


    Parameters
    ----------
    url: str
        Url to mount a session
    retries: int
        How many retries
    backoff_factor: float
        Backoff schema - time periods between retry

    Returns
    -------
    requests.Session
        Mounted session
    """

    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(url, adapter)
    return session


def _make_request(url: str) -> Union[BeautifulSoup, None]:
    """Helper method to scrap

    Parameters
    ----------
    url : str
        url to scrape

    Returns
    -------
        BeautifulSoup object
    """
    headers = {"User-Agent": get_user_agent()}
    session = _retry_session("https://www.coingecko.com")
    try:
        req = session.get(url, headers=headers, timeout=5)
    except Exception as error:
        console.print(error)
        raise RetryError(
            "Connection error. Couldn't connect to CoinGecko and scrape the data. "
            "Please visit CoinGecko site, and check if it's not under maintenance"
        ) from error

    if req.status_code == 404:
        return None

    if req.status_code >= 400:
        raise Exception(
            f"Couldn't connect to {url}. Status code: {req.status_code}. Reason: {req.reason}"
        )

    return BeautifulSoup(req.text, features="lxml")


def get_crypto_hacks() -> pd.DataFrame:
    """Get major crypto-related hacks
    [Source: https://rekt.news]

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL}
    """
    soup = _make_request("https://rekt.news/leaderboard")
    if soup:
        rekt_list = soup.find("ol", {"class": "leaderboard-content"}).find_all("li")
        df = pd.DataFrame(columns=HACKS_COLUMNS)
        for item in rekt_list:
            a = item.find("a", href=True)
            audit = item.find("span", {"class": "leaderboard-audit"}).text
            details = item.find("div", {"class": "leaderboard-row-details"}).text.split(
                "|"
            )
            url = a["href"]
            title = a.text
            amount = int(details[0][1:].replace(",", ""))
            date = details[1].replace(" ", "")
            df.loc[len(df.index)] = [
                title,
                date,
                amount,
                audit,
                url.replace("/", ""),
                f"https://rekt.news{url}",
            ]
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    return pd.DataFrame()


def get_crypto_hack(slug: str) -> Union[str, None]:
    """Get crypto hack
    [Source: https://rekt.news]

    Parameters
    ----------
    slug: str
        slug of crypto hack

    Returns
    -------
    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,URL}
    """
    url = f"https://rekt.news/{slug}"
    soup = _make_request(url)
    if not soup:
        slugs = get_crypto_hack_slugs()
        console.print(
            f'Slug "{slug}" not found, try one of the following:', ",".join(slugs)
        )
        return None
    title = soup.find("h1", {"class": "post-title"}).text
    date = soup.find("time").text
    content = (
        soup.find("section", {"class": "post-content"})
        .get_text("\n")
        .replace("\r\n,", ", ")
        .replace("\n,", ", ")
        .replace("\r\n.", ".\n\t")
        .replace("\n.", ".\n\t")
        .replace("\r\n ", " ")
        .replace("\n ", " ")
    ).split("""SUBSCRIBE""")[0]
    final_str = f"""
    {title}
    {date}

    {content}

    Detailed history in {url}
    """
    return final_str


def get_crypto_hack_slugs() -> List[str]:
    """Get all crypto hack slugs
    [Source: https://rekt.news]
    Returns
    -------
    List[str]:
        List with slugs
    """
    soup = _make_request("https://rekt.news/leaderboard")
    href_list = []
    if soup:
        rekt_list = soup.find("ol", {"class": "leaderboard-content"}).find_all("li")
        for item in rekt_list:
            a = item.find("a", href=True)["href"].replace("/", "")
            href_list.append(a)
        return href_list
    return href_list
