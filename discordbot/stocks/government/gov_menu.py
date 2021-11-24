import asyncio
import discord
import config_discordbot as cfg

# pylint: disable=wrong-import-order,too-many-branches
from discordbot import gst_bot

from stocks.government.lasttrades import lasttrades_command
from stocks.government.topbuys import topbuys_command
from stocks.government.topsells import topsells_command
from stocks.government.lastcontracts import lastcontracts_command
from stocks.government.qtrcontracts import qtrcontracts_command
from stocks.government.toplobbying import toplobbying_command
from stocks.government.gtrades import gtrades_command
from stocks.government.contracts import contracts_command
from stocks.government.histcont import histcont_command
from stocks.government.lobbying import lobbying_command


class GovernmentCommands(discord.ext.commands.Cog):
    """Government menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.gov.lasttrades")
    async def lasttrades(
        self,
        ctx: discord.ext.commands.Context,
        gov_type="",
        past_transactions_days="",
        representative="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: str
            Possible arguments: congress, senate & house
        past_transactions_days: int
            Positive number of past transaction days
        representative: str
            Enter name of a representative
        """
        await lasttrades_command(ctx, gov_type, past_transactions_days, representative)

    @discord.ext.commands.command(name="stocks.gov.topbuys")
    async def topbuys(
        self,
        ctx: discord.ext.commands.Context,
        gov_type="",
        past_transactions_months="",
        num="",
        raw="",
    ):
        """Displays most purchased stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: str
            Possible arguments: congress, senate & house
        past_transactions_months: int
            Positive number of past transaction months
        num: int
            Number of most sold stocks to retrieve
        raw: boolean
            True or false
        """
        await topbuys_command(ctx, gov_type, past_transactions_months, num, raw)

    @discord.ext.commands.command(name="stocks.gov.topsells")
    async def topsells(
        self,
        ctx: discord.ext.commands.Context,
        gov_type="",
        past_transactions_months="",
        num="",
        raw="",
    ):
        """Displays most sold stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: str
            Possible arguments: congress, senate & house
        past_transactions_months: int
            Positive number of past transaction months
        num: int
            Number of most sold stocks to retrieve
        raw: boolean
            True or false
        """
        await topsells_command(ctx, gov_type, past_transactions_months, num, raw)

    @discord.ext.commands.command(name="stocks.gov.lastcontracts")
    async def lastcontracts(
        self, ctx: discord.ext.commands.Context, past_transactions_days="", num=""
    ):
        """Displays last government contracts [quiverquant.com]

        Parameters
        -----------
        past_transactions_days: int
            Positive number of past transaction days
        num: int
            Number of contracts
        """
        await lastcontracts_command(ctx, past_transactions_days, num)

    @discord.ext.commands.command(name="stocks.gov.qtrcontracts")
    async def qtrcontracts(
        self, ctx: discord.ext.commands.Context, num="", analysis=""
    ):
        """Displays a look at government contracts [quiverquant.com]

        Parameters
        -----------
        analysis: str
            Possible arguments: total, upmom & downmom
        num: int
            Number of contracts
        """
        await qtrcontracts_command(ctx, num, analysis)

    @discord.ext.commands.command(name="stocks.gov.toplobbying")
    async def toplobbying(self, ctx: discord.ext.commands.Context, num="", raw=""):
        """Displays top lobbying firms [quiverquant.com]

        Parameters
        -----------
        num: int
            Number to show
        raw: boolean
            True or false
        """
        await toplobbying_command(ctx, num, raw)

    @discord.ext.commands.command(name="stocks.gov.gtrades")
    async def gtrades(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        gov_type="",
        past_transactions_months="",
        raw="",
    ):
        """Displays government trades [quiverquant.com]

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        gov_type: str
            Possible arguments: congress, senate & house
        past_transactions_months: int
            Positive number of past transaction months
        raw: boolean
            True or false
        """
        await gtrades_command(ctx, ticker, gov_type, past_transactions_months, raw)

    @discord.ext.commands.command(name="stocks.gov.contracts")
    async def contracts(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        past_transaction_days="",
        raw="",
    ):
        """Displays contracts associated with tickers [quiverquant.com]

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        past_transaction_days: int
            Number of past transaction months
        raw: boolean
            True or false
        """
        await contracts_command(ctx, ticker, past_transaction_days, raw)

    @discord.ext.commands.command(name="stocks.gov.histcont")
    async def histcont(self, ctx: discord.ext.commands.Context, ticker=""):
        """Displays historical quarterly-contracts [quiverquant.com]

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        """
        await histcont_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.gov.lobbying")
    async def lobbying(self, ctx: discord.ext.commands.Context, ticker="", num=""):
        """Displays lobbying details [quiverquant.com]

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        num: int
            Number of events
        """
        await lobbying_command(ctx, ticker, num)

    @discord.ext.commands.command(name="stocks.gov")
    async def government_menu(self, ctx: discord.ext.commands.Context, ticker=""):
        """Stocks Context - Shows Government Menu

        Returns
        -------
        Sends a message to the discord user with the commands from the gov context.
        The user can then select a reaction to trigger a command.
        """

        if cfg.DEBUG:
            print(f"\n!stocks.gov {ticker}")

        text = (
            "0️⃣ !stocks.gov.lasttrades <GOV_TYPE> <PAST_TRANSACTION_DAYS> "
            "<REPRESENTATIVE>\n"
            "1️⃣ !stocks.gov.topbuys <GOV_TYPE> <PAST_TRANSACTION_MONTHS>"
            "<NUM> <RAW>\n"
            "2️⃣ !stocks.gov.topsells <GOV_TYPE> <PAST_TRANSACTION_MONTHS>"
            "<NUM> <RAW>\n"
            "3️⃣ !stocks.gov.lastcontracts <PAST_TRANSACTION_DAYS> <NUM>\n"
            "4️⃣ !stocks.gov.qtrcontracts <ANALYSIS> <NUM>\n"
            "5️⃣ !stocks.gov.toplobbying <NUM> <RAW>\n"
        )
        if ticker:
            text += (
                f"6️⃣ !stocks.gov.gtrades {ticker} <GOV_TYPE> <PAST_TRANSACTION_MONTHS>"
                f"<RAW>\n"
                f"7️⃣ !stocks.gov.contracts {ticker} <PAST_TRANSACTION_DAYS> <RAW>\n"
                f"8️⃣ !stocks.gov.histcont {ticker}\n"
                f"9️⃣ !stocks.gov.lobbying {ticker} <NUM>\n"
            )
        else:
            text += (
                "\nMore commands available when providing a ticker with:"
                "\n!stocks.gov <TICKER>"
            )

        title = "Stocks: Government (GOV) Menu"
        embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        msg = await ctx.send(embed=embed)

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        if ticker:
            emoji_list += ["5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

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
                await lasttrades_command(ctx)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                await topbuys_command(ctx)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                await topsells_command(ctx)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                await lastcontracts_command(ctx)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                await qtrcontracts_command(ctx)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                await toplobbying_command(ctx, ticker)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                await gtrades_command(ctx, ticker)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                await contracts_command(ctx, ticker)
            elif reaction.emoji == "8️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 8")
                await histcont_command(ctx, ticker)
            elif reaction.emoji == "9️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 9")
                await lobbying_command(ctx, ticker)

            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)

        except asyncio.TimeoutError:
            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)
            embed = discord.Embed(
                description="Error timeout - you snooze you lose! 😋",
                colour=cfg.COLOR,
                title="TIMEOUT Stocks: Government (GOV) Menu",
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(GovernmentCommands(bot))
