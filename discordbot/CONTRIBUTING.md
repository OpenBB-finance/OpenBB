# CONTRIBUTING

- [CONTRIBUTING](#contributing)
  - [Introduction](#introduction)
  - [Code Structure](#code-structure)
  - [Developer Journey](#developer-journey)
    - [Adding a new context/category](#adding-a-new-contextcategory)
    - [Adding a new command](#adding-a-new-command)
    - [Selecting a command through a reaction in a menu bot message](#selecting-a-command-through-a-reaction-in-a-menu-bot-message)

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines for the Discord Bot)! 🚀

## Introduction

The following is a set of guidelines for contributing to Gamestonk Terminal. These are mostly guidelines, not rules.
Use your best judgment, and feel free to propose changes to this document in a pull request.

The [Github Discord Bot board](https://github.com/GamestonkTerminal/GamestonkTerminal/projects/4) will display the
tickets we're currently working on, or have planned to work on. As a first step towards contribution, you should look
into what is there to implement or reach out to the community in discord and ask what they want/need. For more
information reach out to @lardigalltomhistoria or @SexyYear on discord.

The reader reading this document should read [CONTRIBUTING.md](CONTRIBUTING.md) document. This is because the
contributing steps are identical with the difference of having a different coding structure, which is where this
document will mainly focus.

## Code Structure

It is critical for our discord bot to go hand in hand with Gamestonk Terminal commands structure. As we want the
community to learn the structure of the commands for GST and the GST bot, simultaneously. This is so that if I know
that I can reach "Price vs Short Interest" command in Terminal through `(stocks)>(dps)>psi`, I know that the discord
bot will invoke the same command with `!stocks.dps.psi`.

The code structure is as follows:

```text
discordbot/discordbot.py
          /economy/economy_menu.py
                  /currencies.py
                  /...
                  /feargreed.py
          /stocks/dark_pool_shorts/dps_menu.py
                                  /dpotc.py
                                  /...
                                  /spos.py
```

The main difference between discord bot code structure and Gamestonk Terminal is in the fact that in Gamestonk Terminal
the files are organized by data source whereas in the discord bot each files corresponds at a different bot command.

The file that has the name of the context or category (e.g. `economy_menu` or `dps_menu`) will contain a collection of
possible commands from the ones within that same directory. The user will be able to select these through an emoji reaction.

## Developer Journey

When adding a new command to our discord bot this is the journey that the developer must follow.

Does the appropriate `context/category` already exists for the command you are looking to implement? If it does,
jump to [adding a new command](#adding-a-new-command), otherwise carry on.

### Adding a new context/category

If you want to add a new context/category, you just need to create the corresponding `_menu` file in the correct
location. E.g. let's suppose you want to create `stocks/dark_pool_shorts`, then you create a `dps_menu.py` file under
that directory. Such `dps_menu.py` file will have a code along these lines:

```python
import asyncio
import discord
import discordbot.config_discordbot as cfg
import yfinance as yf

# pylint: disable=wrong-import-order
from discordbot.run_discordbot import gst_bot


class DarkPoolShortsCommands(discord.ext.commands.Cog):
    """Dark Pool Shorts menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    # The commands will be added here as a function

def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(DarkPoolShortsCommands(bot))
```

In order for the bot to know about this new `context/category` you need to go into
[discordbot.py](discordbot/discordbot.py) and add it to the section before running the bot, using:

```python
gst_bot.load_extension("stocks.dark_pool_shorts.dps_menu")
```

### Adding a new command

For adding a new command, you need to add the name of the command under the `context/category` it belongs to.
Let's assume you want to add the `ftd` command (failure-to-deliver) on `stocks/dark_pool_shorts`, then you need to
create an [ftd.py](discordbot/stocks/dark_pool_shorts/ftd.py).

Such file will have the following format:

```python
# DO ALL THE IMPORTS NECESSARY HERE
import os
from datetime import datetime, timedelta
import discord
import yfinance as yf
import discordbot.config_discordbot as cfg
import discordbot.helpers
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from discordbot.run_discordbot import gst_imgur

# IMPORT THE GST MODEL/VIEW THAT RETRIEVES DATA WANTED
from gamestonk_terminal.stocks.dark_pool_shorts import sec_model

# DEFINE THE COMMAND AND ITS ARGUMENTS
async def ftd_command(ctx, ticker="", start="", end=""):
    """Fails-to-deliver data [SEC]"""

    # ADD A BIG TRY-CATCH IN CASE IT FAILS TO RETURN A MESSAGE TO USER
    try:
        # DEBUG USER INPUT
        if cfg.DEBUG:
            print(f"\n!stocks.dps.ftd {ticker} {start} {end}")

        # CHECK FOR ARGUMENT VALIDITY
        if ticker == "":
            raise Exception("Stock ticker is required")
        ticker = ticker.upper()
        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")
        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)
        if end == "":
            end = datetime.now()
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)

        # RETRIEVE DATA
        ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, 0)

        # DEBUG OUTPUT
        if cfg.DEBUG:
            print(ftds_data.to_string())

        # PROCESS DATA TO OUTPUT
        plt.bar(
            ftds_data["SETTLEMENT DATE"],
            ftds_data["QUANTITY (FAILS)"] / 1000,
        )
        plt.ylabel("Shares [K]")
        plt.title(f"Fails-to-deliver Data for {ticker}")
        plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.gcf().autofmt_xdate()
        plt.xlabel("Days")
        _ = plt.gca().twinx()
        stock= discordbot.helpers.load(ticker, start)
        stock_ftd = stock[stock.index > start]
        stock_ftd = stock_ftd[stock_ftd.index < end]
        plt.plot(stock_ftd.index, stock_ftd["Adj Close"], color="tab:orange")
        plt.ylabel("Share Price [$]")
        plt.savefig("dps_ftd.png")
        plt.close("all")
        uploaded_image = gst_imgur.upload_image("dps_ftd.png", title="something")
        image_link = uploaded_image.link

        # PREPARE SUCCESSFUL DISCORD EMBED TO SHOW USER
        title = "Stocks: [SEC] Failure-to-deliver " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)

        os.remove("dps_ftd.png")

        # SEND MESSAGE IN DISCORD
        await ctx.send(embed=embed)

    except Exception as e:
        # PREPARE DISCORD EMBED TO SHOW USER THE ERROR
        embed = discord.Embed(
            title=f"ERROR Stocks: [SEC] Failure-to-deliver {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
```

The main variation in each command occurs at the output level, where the bot reply could be either:

- A simple **string**.
- A **table**, which relies on a pandas dataframe output and pagination is used for the user to iterate through columns.
  See [shorted.py](discordbot/stocks/dark_pool_shorts/shorted.py)
- An **image**, which relies on matplotlib output and IMGUR is used to upload this image to send to the user. See
  [ftd.py](discordbot/stocks/dark_pool_shorts/ftd.py).

Once the command file has been added, one needs to make sure our bot is aware of it. Therefore we need to add it in
the `dps_menu` file, same one that was created in [Adding a new context/category](#adding-a-new-context/category).

This is achieved by adding the following method to `DarkPoolShortsCommands(discord.ext.commands.Cog)` class:

```python
@discord.ext.commands.command(name="stocks.dps.ftd")
async def ftd(self, ctx: discord.ext.commands.Context, ticker="", start="", end=""):
    """Fails-to-deliver data [SEC]

    Parameters
    ----------
    ticker: str
        Stock ticker
    start: datetime
        Start of date
    end: datetime
        End of date
    """
    await ftd_command(ctx, ticker, start, end)
```

Note that the docstring is *CRITICAL* to be added as this will allow the user to query about this command with
`!help stocks.dps.ftd` and understand what the function outputs, what source it uses and ultimately, the expected arguments.

### Selecting a command through a reaction in a menu bot message

Finally, it was important for us that the users had the same experience given by the terminal. Hence we set the code
structure in a way so that the user could call a menu like `!stocks.dps` and be able to select multiple commands from
the menu that popped-up through message reactions.

Taking the `dps_menu` as example, this is done by adding the following method to
`DarkPoolShortsCommands(discord.ext.commands.Cog)` class:

```python
@discord.ext.commands.command(name="stocks.dps")
async def dark_pool_shorts_menu(self, ctx: discord.ext.commands.Context):
    """Stocks Context - Shows Dark Pool Shorts Menu"""

    if cfg.DEBUG:
        print(f"\n!stocks.dps {ticker}")

    text = (
        "0️⃣ !stocks.dps.shorted <NUM>\n"
        "1️⃣ !stocks.dps.hsi <NUM>\n"
        "2️⃣ !stocks.dps.pos <NUM> <SORT>\n"
    )

    title = "Dark Pool Shorts (DPS) Menu"
    embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
    embed.set_author(
        name=cfg.AUTHOR_NAME,
        icon_url=cfg.AUTHOR_ICON_URL,
    )
    msg = await ctx.send(embed=embed)

    emoji_list = ["0️⃣", "1️⃣", "2️⃣"]
    for emoji in emoji_list:
        await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in emoji_list

    try:
        reaction, _ = await gst_bot.wait_for(
            "reaction_add", timeout=cfg.MENU_TIMEOUT, check=check
        )
        if reaction.emoji == "0️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 0")
            await shorted_command(ctx)
        elif reaction.emoji == "1️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 1")
            await hsi_command(ctx)
        elif reaction.emoji == "2️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 2")
            await pos_command(ctx)

        for emoji in emoji_list:
            await msg.remove_reaction(emoji, ctx.bot.user)

    except asyncio.TimeoutError:
        text = text + "\n\nCommand timeout."
        embed = discord.Embed(title=title, description=text)
        await msg.edit(embed=embed)
        for emoji in emoji_list:
            await msg.remove_reaction(emoji, ctx.bot.user)
```
