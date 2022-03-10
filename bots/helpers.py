import os
from typing import List
import uuid

import df2img
import disnake
import pandas as pd
import yfinance as yf
from numpy.core.fromnumeric import transpose
from PIL import Image

import bots.config_discordbot as cfg
from bots.groupme.groupme_helpers import send_image, send_message

presets_custom = [
    "potential_reversals",
    "golden_cross_penny",
    "rosenwald_gtfo",
    "golden_cross",
    "bull_runs_over_10pct",
    "recent_growth_and_support",
    "heavy_inst_ins",
    "short_squeeze_scan",
    "under_15dol_stocks",
    "top_performers_healthcare",
    "oversold_under_3dol",
    "value_stocks",
    "cheap_dividend",
    "death_cross",
    "top_performers_tech",
    "unusual_volume",
    "cheap_oversold",
    "undervalue",
    "high_vol_and_low_debt",
    "simplistic_momentum_scanner_under_7dol",
    "5pct_above_low",
    "growth_stocks",
    "cheap_bottom_dividend",
    "analyst_strong_buy",
    "oversold",
    "rosenwald",
    "weak_support_and_top_performers",
    "channel_up_and_low_debt_and_sma_50and200",
    "template",
    "modified_neff",
    "buffett_like",
    "oversold_under_5dol",
    "sexy_year",
    "news_scanner",
    "top_performers_all",
    "stocks_strong_support_levels",
    "continued_momentum_scan",
    "modified_dreman",
    "break_out_stocks",
]
signals = [
    "top_gainers",
    "top_losers",
    "new_high",
    "new_low",
    "most_volatile",
    "most_active",
    "unusual_volume",
    "overbought",
    "oversold",
    "downgrades",
    "upgrades",
    "earnings_before",
    "earnings_after",
    "recent_insider_buying",
    "recent_insider_selling",
    "major_news",
    "horizontal_sr",
    "tl_resistance",
    "tl_support",
    "wedge_up",
    "wedge_down",
    "wedge",
    "triangle_ascending",
    "triangle_descending",
    "channel_up",
    "channel_down",
    "channel",
    "double_top",
    "double_bottom",
    "multiple_top",
    "multiple_bottom",
    "head_shoulders",
    "head_shoulders_inverse",
]


def load(ticker, start_date):
    df_stock_candidate = yf.download(ticker, start=start_date, progress=False)
    df_stock_candidate.index.name = "date"
    return df_stock_candidate


def quote(ticker):
    ticker = yf.Ticker(ticker)
    quote_df = pd.DataFrame(
        [
            {
                "Symbol": ticker.info["symbol"],
                "Name": ticker.info["shortName"],
                "Price": ticker.info["regularMarketPrice"],
                "Open": ticker.info["regularMarketOpen"],
                "High": ticker.info["dayHigh"],
                "Low": ticker.info["dayLow"],
                "Previous Close": ticker.info["previousClose"],
                "Volume": ticker.info["volume"],
                "52 Week High": ticker.info["fiftyTwoWeekHigh"],
                "52 Week Low": ticker.info["fiftyTwoWeekLow"],
            }
        ]
    )
    quote_df["Change"] = quote_df["Price"] - quote_df["Previous Close"]
    quote_df["Change %"] = quote_df.apply(
        lambda x: f'{((x["Change"] / x["Previous Close"]) * 100):.2f}%',
        axis="columns",
    )
    for c in [
        "Price",
        "Open",
        "High",
        "Low",
        "Previous Close",
        "52 Week High",
        "52 Week Low",
        "Change",
    ]:
        quote_df[c] = quote_df[c].apply(lambda x: f"{x:.2f}")
    quote_df["Volume"] = quote_df["Volume"].apply(lambda x: f"{x:,}")

    quote_df = quote_df.set_index("Symbol")
    quote_data = transpose(quote_df)
    return quote_data


def uuid_get():
    rand = str(uuid.uuid1()).replace("-", "")
    return rand


def autocrop_image(image, border=0):
    bbox = image.getbbox()
    image = image.crop(bbox)
    (width, height) = image.size
    width += border * 2
    height += border * 2
    cropped_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cropped_image.paste(image, (border, border))
    return cropped_image


def ticker_autocomp(inter, ticker: str):  # pylint: disable=W0613
    if not ticker:
        return ["Start Typing", "for a", "stock ticker"]
    print(f"ticker_autocomp [ticker]: {ticker}")
    tlow = ticker.lower()
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return [ticker for ticker in df if ticker.lower().startswith(tlow)][:24]


def expiry_autocomp(inter, ticker: str):  # pylint: disable=W0613
    data = inter.filled_options["ticker"]
    yf_ticker = yf.Ticker(data)
    dates = list(yf_ticker.options)
    return dates[:24]


def presets_custom_autocomp(inter, preset: str):  # pylint: disable=W0613
    df = presets_custom
    if not preset:
        return df[:24]
    plow = preset.lower()
    print(f"preset_custom_autocomp [preset]: {preset}")
    return [preset for preset in df if preset.lower().startswith(plow)][:24]


def signals_autocomp(inter, signal: str):  # pylint: disable=W0613
    df = signals
    if not signal:
        return df[:24]
    print(f"signal_autocomp [signal]: {signal}")
    slow = signal.lower()
    return [signal for signal in df if signal.lower().startswith(slow)][:24]


def save_image(file, fig):
    imagefile = f"{file.replace('.png', '')}_{uuid_get()}.png"
    df2img.save_dataframe(fig=fig, filename=imagefile)
    image = Image.open(imagefile)
    image = autocrop_image(image, 0)
    image.save(imagefile, "PNG", quality=100)
    return imagefile


def image_border(file, **kwargs):
    imagefile = f"{file.replace('.png', '')}_{uuid_get()}.png"
    if "fig" in kwargs:
        fig = kwargs["fig"]
        fig.write_image(imagefile)
        img = Image.open(imagefile)
    else:
        img = Image.open(file)
    im_bg = Image.open(cfg.IMG_BG)
    h = img.height + 240
    w = img.width + 520

    # Paste fig onto background img and autocrop background
    img = img.resize((w, h), Image.ANTIALIAS)
    x1 = int(0.5 * im_bg.size[0]) - int(0.5 * img.size[0])
    y1 = int(0.5 * im_bg.size[1]) - int(0.5 * img.size[1])
    x2 = int(0.5 * im_bg.size[0]) + int(0.5 * img.size[0])
    y2 = int(0.5 * im_bg.size[1]) + int(0.5 * img.size[1])
    img = img.convert("RGB")
    im_bg.paste(img, box=(x1 - 5, y1, x2 - 5, y2))
    im_bg.save(file, "PNG", quality=100)
    image = Image.open(file)
    image = autocrop_image(image, 0)
    image.save(imagefile, "PNG", quality=100)
    return imagefile


class ShowView:
    async def run_discord(self, func, inter, *args, **kwargs):
        data = func(*args, **kwargs)

        if "view" in data:
            await inter.send(
                embed=data["embed"][0],
                view=data["view"](data["embed"], data["choices"]),
            )

        else:
            title = data.get("title", "")
            embed = disnake.Embed(
                title=title, colour=cfg.COLOR, description=data.get("description", "")
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            if "imagefile" in data:
                image = disnake.File(data["imagefile"])
                embed.set_image(url=f"attachment://{data['imagefile']}")
                os.remove(data["imagefile"])
                await inter.send(embed=embed, file=image)
            else:
                await inter.send(embed=embed)

    async def discord(self, func, inter, name, *args, **kwargs):
        await inter.response.defer()
        cfg.logger.info(name)
        if os.environ.get("DEBUG_MODE") == "true":
            await self.run_discord(func, inter, *args, **kwargs)
        else:
            try:
                await self.run_discord(func, inter, *args, **kwargs)
            except Exception as e:
                embed = disnake.Embed(
                    title=name,
                    colour=cfg.COLOR,
                    description=e,
                )
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )

                await inter.send(embed=embed, delete_after=30.0)

    def groupme(self, func, group_id, name, *args, **kwargs):
        data = func(*args, **kwargs)
        if "imagefile" in data:
            send_image(data["imagefile"], group_id, data.get("description", ""), True)
        elif "embeds_img" in data:
            send_image(
                data["embeds_img"][0], group_id, data.get("description", ""), True
            )
        elif "description" in data:
            title = data.get("title", "")
            # TODO: Allow navigation through pages
            description = data.get("description")
            if isinstance(description, List):
                clean_desc = description[0].replace("Page ", "")
            else:
                clean_desc = description.replace("Page ", "")
            message = f"{title}\n{clean_desc}"
            send_message(message, group_id)

    def telegram(self, func, message, bot, cmd, *args, **kwargs):
        data = func(*args, **kwargs)
        if "imagefile" in data:
            with open(data["imagefile"], "rb") as image:
                bot.reply_to(message, data["title"])
                bot.send_photo(message.chat.id, image)
            os.remove(data["imagefile"])
        elif "embeds_img" in data:
            with open(data["embeds_img"][0], "rb") as image:
                bot.reply_to(message, data["title"])
                bot.send_photo(message.chat.id, image)
            os.remove(data["embeds_img"][0])
        elif "description" in data:
            title = data.get("title", "")
            # TODO: Allow navigation through pages
            description = data.get("description")
            if isinstance(description, List):
                clean_desc = description[0].replace("Page ", "")
            else:
                clean_desc = description.replace("Page ", "")
            res = f"{title}\n{clean_desc}"
            bot.reply_to(message, res)
