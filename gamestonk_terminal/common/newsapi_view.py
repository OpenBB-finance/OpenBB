""" News View """
__docformat__ = "numpy"

import requests

from gamestonk_terminal import config_terminal as cfg


def news(
    term: str,
    num: int,
    s_from: str,
    show_newest: bool,
    sources: str,
):
    """Display news for a given title. [Source: NewsAPI]

    Parameters
    ----------
    term : str
        term to search on the news articles
    num : int
        number of articles to display
    s_from: str
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from
    """
    link = (
        f"https://newsapi.org/v2/everything?q={term}&from={s_from}&sortBy=publishedAt&language=en"
        f"&apiKey={cfg.API_NEWS_TOKEN}"
    )

    if sources:
        link += f"&domains={sources}"

    response = requests.get(link)

    # Check that the API response was successful
    if response.status_code == 426:
        print(f"Error in request: {response.json()['message']}", "\n")

    elif response.status_code != 200:
        print(f"Error in request {response.status_code}. Check News API token", "\n")

    else:
        print(
            f"{response.json()['totalResults']} news articles for {term} were found since {s_from}\n"
        )

        if show_newest:
            articles = response.json()["articles"]

        else:
            articles = response.json()["articles"][::-1]

        for idx, article in enumerate(articles):
            print(
                article["publishedAt"].replace("T", " ").replace("Z", ""),
                " ",
                article["title"],
            )
            # Unnecessary to use name of the source because contained in link article["source"]["name"]
            print(article["url"], "\n")

            if idx >= num - 1:
                break
