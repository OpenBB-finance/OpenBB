""" Thought of The Day """

from __future__ import annotations

import random
import re

from bs4 import BeautifulSoup

from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

__docformat__ = "numpy"


class ThoughtOfTheDay:
    """ThoughtOfTheDay class"""

    def __init__(self, urls: dict[str, str] | None = None):
        """Constructor"""

        self.metadata: dict = {}

        if urls is None:
            self.urls = {
                "Marcus_Aurelius": "https://www.goodreads.com/author/quotes/17212.Marcus_Aurelius",
                "Epictetus": "https://www.goodreads.com/author/quotes/13852.Epictetus",
                "Seneca": "https://www.goodreads.com/author/quotes/4918776.Seneca",
                "Marcus_Tullius_Cicero": "https://www.goodreads.com/author/quotes/13755.Marcus_Tullius_Cicero",
                "Aristotle": "https://www.goodreads.com/author/quotes/2192.Aristotle",
                "Plato": "https://www.goodreads.com/author/quotes/879.Plato",
                "Pythagoras": "https://www.goodreads.com/author/quotes/203707.Pythagoras",
            }

            return

        self.urls = urls

    def get_urls(self) -> dict:
        """Getter method for URLs"""
        return self.urls

    def get_metadata(self, author: str) -> dict:
        """Loads metadata for a given author

        Parameters
        ----------
        author : str
            Author key - Marcus_Aurelius, Epictetus, Seneca, Marcus_Tullius_Cicero, Aristotle, Plato, Pythagoras

        Returns
        ----------
        dict
            Metadata dictionary that includes number of quotes, number of pages and first 30 quotes
        """
        quotes_page = BeautifulSoup(
            request(self.urls[author]).text,
            "lxml",
        )

        find_navigation = quotes_page.find("em", {"class": "current"}).find_parent(
            "div"
        )

        page_count = [
            a_page_ref.text.strip("\n")
            for a_page_ref in find_navigation.find_all("a", href=True)
        ]

        ret = {}
        ret["pages"] = page_count[-2]

        find_count = quotes_page.find(string=re.compile("Showing 1-30 of"))

        quote_count = re.search(r"Showing 1-30 of (?P<number>[\d,]+)", find_count)

        if quote_count:
            ret["quoutes"] = quote_count.group("number")

        all_quotes = quotes_page.find_all("div", {"class": "quote"})

        ret["quotes"] = []

        for a_quote in all_quotes:
            parsed_quote = {}

            parsed_quote = a_quote.find("div", {"class": "quoteText"}).text

            ret["quotes"].append(parsed_quote)

        return ret

    def quote_to_str(self, a_quote: str) -> str:
        """Format a quote parsed from Goodreads into a string

        Parameters
        ----------
        a_quote : str
            A quote formatted by Goodreads

        Returns
        ----------
        str
            A string version of the quote
        """
        ready = []
        prev = None
        for a_line in a_quote:
            if not prev:
                ready.append(a_line)
                prev = a_line
                continue

            if a_line != "\n":
                ready.append(a_line)
                prev = a_line
                continue

            if prev == "  \n":
                ready.pop()
                prev = None

        return "".join(map(str, ready))


def get_thought_of_the_day():
    """Pick a thought of the day"""
    totd = ThoughtOfTheDay()

    quotes = []
    for an_author in totd.get_urls():
        metadata = totd.get_metadata(an_author)
        quotes = quotes + metadata["quotes"]

    console.print("Thought of the day:")
    console.print(
        totd.quote_to_str(quotes[random.randint(0, len(quotes) - 1)])  # nosec
    )

    console.print("\n")
