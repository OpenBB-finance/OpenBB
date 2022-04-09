from __future__ import annotations

import disnake
import disnake.ext.commands as commands

from bots import helpers
from bots.stocks.sia.cpic import cpic_command
from bots.stocks.sia.cps import cps_command
from bots.stocks.sia.metric import metric_command


class StocksSIACommands(commands.Cog):
    def __init__(self, bot):
        super().__init__
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def sia(self, inter):
        pass

    @sia.sub_command(name="cps")
    async def sia_cps(
        self,
        inter: disnake.AppCmdInter,
        country: str = commands.Param(autocomplete=helpers.country_autocomp),
    ):
        """Display number of companies per industry in a specific country. [Source: Finance Database]

        Parameters
        ----------
        country: Country to Display Companies per Sector
        mktcap: Select market cap of companies to consider from Small, Mid and Large
        """
        await helpers.ShowView().discord(
            cps_command,
            inter,
            "sia cps",
            country,
        )

    @sia.sub_command(name="cpic")
    async def sia_cpic(
        self,
        inter: disnake.AppCmdInter,
        industry: str = commands.Param(autocomplete=helpers.industry_autocomp),
    ):
        """Display number of companies per country in a specific industry. [Source: Finance Database]

        Parameters
        ----------
        industry: Select industry to get number of companies by each country
        mktcap: Select market cap of companies to consider from Small, Mid and Large
        """
        await helpers.ShowView().discord(
            cpic_command,
            inter,
            "sia cpic",
            industry,
        )

    @sia.sub_command(name="metrics")
    async def sia_mertics(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=helpers.ticker_autocomp),
        metric: str = commands.Param(autocomplete=helpers.metric_autocomp),
    ):
        """Visualise financial metric across filters selected [Source: Finance Database]

        Parameters
        ----------
        metric: Select financial metric
        ticker: Company to use for Industry, Sector, and Market Cap
        """
        met_arg = helpers.metric_yf_keys[metric]
        await helpers.ShowView().discord(
            metric_command, inter, "sia metrics", met_arg[0], met_arg[1], ticker
        )


def setup(bot: commands.Bot):
    bot.add_cog(StocksSIACommands(bot))
