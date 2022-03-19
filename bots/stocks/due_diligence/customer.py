import logging

import disnake
import requests
from bs4 import BeautifulSoup

import bots.config_discordbot as cfg
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def customer_command(ticker=""):
    """Displays customers of the company [CSIMarket]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dd customer %s", ticker)

    if not ticker:
        raise Exception("A ticker is required")

    url_customer_chain = (
        f"https://csimarket.com/stocks/custexNO.php?markets&code={ticker.upper()}"
    )
    text_customer_chain = BeautifulSoup(requests.get(url_customer_chain).text, "lxml")

    l_customer = list()
    for customer in text_customer_chain.findAll("td", {"class": "plava svjetlirub"}):
        l_customer.append(customer.text)

    if not l_customer:
        raise Exception("No customers found.")

    # Debug user output
    if cfg.DEBUG:
        logger.debug(l_customer)

    customers, unique = [], []
    i = 0
    i2 = 0

    for value in l_customer:
        name = value
        if name in unique:  # pylint: disable=R1724
            continue
        else:
            unique.append(name)

    while i < len(unique):
        warp = unique[i][0:6]
        if i2 > 3:
            text = f"{warp}\n"
            i2 = 0
        else:
            text = f"{warp:<10}"
            i2 += 1
        customers.append(text)
        i += 1

    title = f"Stocks: [CSIMarket] {ticker.upper()} Customers"
    reports, embeds = [], []
    choices = [
        disnake.SelectOption(label="Home", value="0", emoji="🟢"),
    ]

    if len(customers) < 60:
        description = f"```{''.join(customers)}```"
        embeds.append(
            disnake.Embed(
                title=title,
                description=customers,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        reports.append(f"{description}")

        # Output data
        output = {
            "title": title,
            "description": reports,
            "embed": embeds,
        }
    else:
        i, end = 0, 60
        while i < len(customers):
            description = f"```{''.join(customers[i:end])}```"
            embeds.append(
                disnake.Embed(
                    title=title,
                    description=description,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            i += 60
            end += 60
            reports.append(f"{description}")

        # Output data
        output = {
            "view": Menu,
            "title": title,
            "description": reports,
            "embed": embeds,
            "choices": choices,
        }

    return output
