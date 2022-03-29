import logging
import time

import bs4
import disnake
import pandas as pd
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By

from bots import imps
from openbb_terminal.decorators import log_start_end

# pylint:disable=no-member

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def by_ticker_command(ticker="", sort="fund_percent", num: int = 15):
    """Display ETF Holdings. [Source: StockAnalysis]"""

    # Debug
    if imps.DEBUG:
        logger.debug("etfs")

    options = uc.ChromeOptions()

    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options, version_main=98)
    driver.set_window_size(1920, 1080)
    driver.get(f"http://etf.com/stock/{ticker.upper()}/")

    time.sleep(2)
    driver.find_element(By.XPATH, "(//div[@id='inactiveResult'])[3]").click()
    soup5 = bs4.BeautifulSoup(driver.page_source, "html.parser")
    r_ticker, r_holdings, r_name, r_market = [], [], [], []

    table1 = soup5.find("table", id="StockTable")
    table = table1.find("tbody")
    for x in table.find_all("tr"):
        r_ticker.append(x.find("td").text)
        r_name.append(x.find("td").findNext("td").text)
        r_holdings.append(
            x.find("td").findNext("td").findNext("td").findNext("td").text
        )
        r_market.append(
            x.find("td")
            .findNext("td")
            .findNext("td")
            .findNext("td")
            .findNext("td")
            .text
        )
    driver.quit()
    df = pd.DataFrame(
        {
            "Ticker": r_ticker,
            "Name": r_name,
            "Holdings": r_holdings,
            "Market Value": r_market,
        }
    )

    if df.empty:
        raise Exception("No company holdings found!\n")

    if sort == "mkt_value":
        key = imps.natsort.index_natsorted(
            df["Market Value"],
            key=lambda x: imps.unit_finder.sub(imps.unit_replacer, x),
            reverse=True,
        )
        df = df.reindex(key)

    df = df.iloc[:num]
    df.set_index("Ticker", inplace=True)

    title = f"ETF's Holding {ticker.upper()}"
    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = [], [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(800, (40 * dindex)),
                col_width=[0.6, 3.5, 0.65, 1.1],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(
                cells=(dict(align=["center", "center", "center", "right"]))
            )
            imagefile = "etf-byticker.png"
            imagefile = imps.save_image(imagefile, fig)

            if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
                image_link = imps.multi_image(imagefile)
                images_list.append(imagefile)
            else:
                image_link = imps.multi_image(imagefile)

            embeds_img.append(
                f"{image_link}",
            )
            embeds.append(
                disnake.Embed(
                    title=title,
                    colour=imps.COLOR,
                ),
            )
            i2 += 1
            i += 15
            end += 15

        # Author/Footer
        for i in range(0, i2):
            embeds[i].set_author(
                name=imps.AUTHOR_NAME,
                url=imps.AUTHOR_URL,
                icon_url=imps.AUTHOR_ICON_URL,
            )
            embeds[i].set_footer(
                text=imps.AUTHOR_NAME,
                icon_url=imps.AUTHOR_ICON_URL,
            )

        i = 0
        for i in range(0, i2):
            embeds[i].set_image(url=embeds_img[i])

            i += 1
        embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
        choices = [
            disnake.SelectOption(label="Home", value="0", emoji="🟢"),
        ]

        output = {
            "view": imps.Menu,
            "title": title,
            "embed": embeds,
            "choices": choices,
            "embeds_img": embeds_img,
            "images_list": images_list,
        }
    else:
        fig = imps.plot_df(
            df,
            fig_size=(800, (40 * dindex)),
            col_width=[0.6, 3.5, 0.65, 1.1],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "center", "center", "right"])))
        imagefile = imps.save_image("etf-holdings.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
