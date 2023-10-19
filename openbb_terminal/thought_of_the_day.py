from __future__ import annotations
import random
import re
from bs4 import BeautifulSoup
from openbb_terminal.helper_funcs import async_request
from openbb_terminal.rich_config import console
import asyncio

class ThoughtOfTheDay:
    def __init__(self, urls: dict[str, str] | None = None):
        self.urls = urls or {
            "Marcus_Aurelius": "https://www.goodreads.com/author/quotes/17212.Marcus_Aurelius",
            "Epictetus": "https://www.goodreads.com/author/quotes/13852.Epictetus",
            # ... add other authors and their URLs here
        }

    async def get_metadata(self, author: str) -> dict:
        page = await async_request(self.urls[author])
        quotes_page = BeautifulSoup(page.text, "lxml")
        find_count = quotes_page.find(string=re.compile("Showing 1-30 of"))
        quote_count = re.search(r"Showing 1-30 of (?P<number>[\d,]+)", find_count)

        ret = {"pages": None, "quoutes": None, "quotes": []}

        if quote_count:
            ret["quoutes"] = quote_count.group("number")

        navigation = quotes_page.find("em", {"class": "current"}).find_parent("div")
        page_count = [a_page_ref.text.strip("\n") for a_page_ref in navigation.find_all("a", href=True)]
        ret["pages"] = page_count[-2]

        all_quotes = quotes_page.find_all("div", {"class": "quote"})
        ret["quotes"] = [a_quote.find("div", {"class": "quoteText"}).text for a_quote in all_quotes]

        return ret

    def quote_to_str(self, a_quote: str) -> str:
        lines = [line.strip() for line in a_quote.splitlines() if line.strip()]
        return " ".join(lines)

async def get_thought_of_the_day():
    totd = ThoughtOfTheDay()
    tasks = [totd.get_metadata(author) for author in totd.get_urls()]
    metadata = await asyncio.gather(*tasks)
    quotes = [quote for data in metadata for quote in data["quotes"]]
    selected_quote = random.choice(quotes)

    console.print("Thought of the day:")
    console.print(totd.quote_to_str(selected_quote))
    console.print("\n")

# Usage: asyncio.run(get_thought_of_the_day())

