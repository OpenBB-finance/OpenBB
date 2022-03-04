from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView, ticker_autocomp
from bots.stocks.government.contracts import contracts_command
from bots.stocks.government.gtrades import gtrades_command
from bots.stocks.government.histcont import histcont_command
from bots.stocks.government.lastcontracts import lastcontracts_command
from bots.stocks.government.lasttrades import lasttrades_command
from bots.stocks.government.lobbying import lobbying_command
from bots.stocks.government.qtrcontracts import qtrcontracts_command
from bots.stocks.government.topbuys import topbuys_command
from bots.stocks.government.toplobbying import toplobbying_command
from bots.stocks.government.topsells import topsells_command


class GovernmentCommands(commands.Cog):
    """Government menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @commands.slash_command(name="gov")
    async def gov(self, inter):
        pass

    @gov.sub_command()
    async def lasttrades(
        self,
        inter: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_days: int = 5,
        representative="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_days: Positive number of past transaction days
        representative: Enter name of a representative
        """
        await ShowView().discord(
            lasttrades_command,
            inter,
            "gov lasttrades",
            gov_type,
            past_days,
            representative,
        )

    @gov.sub_command()
    async def topbuys(
        self,
        inter: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 5,
        num: int = 20,
        raw: bool = False,
    ):
        """Displays most purchased stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        num: Number of most sold stocks to retrieve
        raw: If raw data should be outputted
        """
        await ShowView().discord(
            topbuys_command,
            inter,
            "gov topbuys",
            gov_type,
            past_transactions_months,
            num,
            raw,
        )

    @gov.sub_command()
    async def topsells(
        self,
        inter: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 5,
        num: int = 10,
        raw: bool = False,
    ):
        """Displays most sold stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        num: Number of most sold stocks to retrieve
        raw: If raw data should be outputted
        """
        await ShowView().discord(
            topsells_command,
            inter,
            "gov topsells",
            gov_type,
            past_transactions_months,
            num,
            raw,
        )

    @gov.sub_command()
    async def lastcontracts(
        self, inter: disnake.AppCmdInter, past_transactions_days: int = 2, num: int = 20
    ):
        """Displays last government contracts [quiverquant.com]

        Parameters
        -----------
        past_transactions_days: Positive number of past transaction days
        num: Number of contracts
        """
        await ShowView().discord(
            lastcontracts_command,
            inter,
            "gov lastcontracts",
            past_transactions_days,
            num,
        )

    @gov.sub_command()
    async def qtrcontracts(
        self,
        inter: disnake.AppCmdInter,
        num: int = 20,
        analysis: str = commands.Param(choices=["total", "upmom", "downmom"]),
    ):
        """Displays a look at government contracts [quiverquant.com]

        Parameters
        -----------
        analysis: Possible arguments: total, upmom & downmom
        num: Number of contracts
        """
        await ShowView().discord(
            qtrcontracts_command, inter, "gov qtrcontracts", num, analysis
        )

    @gov.sub_command()
    async def toplobbying(
        self, inter: disnake.AppCmdInter, num: int = 10, raw: bool = False
    ):
        """Displays top lobbying firms [quiverquant.com]

        Parameters
        -----------
        num: Number to show
        raw: If raw data should be outputted
        """
        await ShowView().discord(
            toplobbying_command, inter, "gov toplobbying", num, raw
        )

    @gov.sub_command()
    async def gtrades(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 10,
        raw: bool = False,
    ):
        """Displays government trades [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        raw: If raw data should be outputted
        """
        await ShowView().discord(
            gtrades_command,
            inter,
            "gov gtrades",
            ticker,
            gov_type,
            past_transactions_months,
            raw,
        )

    @gov.sub_command()
    async def contracts(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        past_transaction_days: int = 10,
        raw: bool = False,
    ):
        """Displays contracts associated with tickers [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        past_transaction_days: Number of past transaction months
        raw: If raw data should be outputted
        """
        await ShowView().discord(
            contracts_command,
            inter,
            "gov contracts",
            ticker,
            past_transaction_days,
            raw,
        )

    @gov.sub_command()
    async def histcont(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays historical quarterly-contracts [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(histcont_command, inter, "gov histcont", ticker)

    @gov.sub_command()
    async def lobbying(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Displays lobbying details [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        num: Number of events
        """
        await ShowView().discord(lobbying_command, inter, "gov lobbying", ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(GovernmentCommands(bot))
