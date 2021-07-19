"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import argparse
from typing import List
from selenium import webdriver
from bs4 import BeautifulSoup

# from selenium.webdriver.chrome.options import Options as cOpts
# from selenium.webdriver.firefox.options import Options as fOpts
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.config_terminal import (
    PATH_TO_SELENIUM_DRIVER as path_to_driver,
    WEBDRIVER_TO_USE as web,
)
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

browsers = ["chrome", "firefox"]


def print_options_data(stock: str, other_args: List[str]):
    """Scrapes Barchart.com for the options information

    Parameters
    ----------
    stock: str
        Ticker to get options info for
    other_args: List[str]
        Other arguments.  Currently just accepts a browser flag for selenium
    """
    if path_to_driver is None:
        print("Please specify your selenium driver path in config_terminal.py", "\n")
        return

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
        description="Display option data [Source: Barchart.com]",
    )
    parser.add_argument(
        "-b",
        "--browser",
        dest="browser",
        help="selenium webdriver to use",
        choices=browsers,
        default=web,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser.browser:
            browser = ns_parser.browser

        if browser == "chrome":
            # commenting this because it breaks when in usage
            # the downside is that the browser will pop up to get the data
            # options = cOpts()
            # options.headless = True
            driver = webdriver.Chrome(executable_path=path_to_driver)

        elif browser == "firefox":
            # commenting this because it breaks when in usage
            # the downside is that the browser will pop up to get the data
            # options = fOpts()
            # options.headless = True
            driver = webdriver.Firefox(executable_path=path_to_driver)

        page = f"https://www.barchart.com/stocks/quotes/{stock}/overview"
        driver.get(page)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tags = soup.find(
            "div",
            attrs={
                "class": "barchart-content-block symbol-fundamentals bc-cot-table-wrapper"
            },
        )
        data = tags.find_all("li")
        labels = []
        values = []
        print("")
        for row in data:
            labels.append(row.find_all("span")[0].getText())
            values.append(row.find_all("span")[1].getText())

        df = pd.DataFrame(data=[labels, values]).T
        print(tabulate(df, tablefmt="fancy_grid", showindex=False))
        print("")

    except Exception as e:
        print(e, "\n")
