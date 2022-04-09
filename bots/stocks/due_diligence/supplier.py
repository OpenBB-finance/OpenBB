import logging

import disnake
import requests
from bs4 import BeautifulSoup

from bots import imps
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def supplier_command(ticker=""):
    """Displays suppliers of the company [CSIMarket]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dd supplier %s", ticker)

    if not ticker:
        raise Exception("A ticker is required")

    url_supply_chain = (
        f"https://csimarket.com/stocks/competitionNO3.php?supply&code={ticker.upper()}"
    )
    text_supplier_chain = BeautifulSoup(requests.get(url_supply_chain).text, "lxml")

    l_suppliers = list()
    for supplier in text_supplier_chain.findAll(
        "td", {"class": "svjetlirub11 block al"}
    ):
        l_suppliers.append(supplier.text.replace("\n", "").strip())

    if not l_suppliers:
        raise Exception("No suppliers found.\n")

    # Debug user output
    if imps.DEBUG:
        logger.debug(l_suppliers)

    suppliers, unique = [], []
    i = 0

    for value in l_suppliers:
        name = value
        if name in unique:  # pylint: disable=R1724
            continue
        else:
            unique.append(name)

    while i < len(unique):
        warp = unique[i][0:28]
        text = f"{warp:<30}" if (i % 2) == 0 else f"{warp}\n"
        suppliers.append(text)
        i += 1

    title = f"Stocks: [CSIMarket] {ticker.upper()} Suppliers"
    reports = []
    embeds = []
    choices = [
        disnake.SelectOption(label="Home", value="0", emoji="🟢"),
    ]

    if len(suppliers) < 30:
        description = f"```{''.join(suppliers)}```"
        embeds.append(
            disnake.Embed(
                title=title,
                description=suppliers,
                colour=imps.COLOR,
            ).set_author(
                name=imps.AUTHOR_NAME,
                icon_url=imps.AUTHOR_ICON_URL,
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
        i, end = 0, 30
        while i < len(suppliers):
            description = f"```{''.join(suppliers[i:end])}```"
            embeds.append(
                disnake.Embed(
                    title=title,
                    description=description,
                    colour=imps.COLOR,
                ).set_author(
                    name=imps.AUTHOR_NAME,
                    icon_url=imps.AUTHOR_ICON_URL,
                )
            )
            i += 30
            end += 30
            reports.append(f"{description}")

        # Output data
        output = {
            "view": imps.Menu,
            "title": title,
            "description": reports,
            "embed": embeds,
            "choices": choices,
        }

    return output
