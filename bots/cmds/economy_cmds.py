import disnake
from disnake.ext import commands

from bots.economy.currencies import currencies_command
from bots.economy.energy import energy_command
from bots.economy.feargreed import feargreed_command
from bots.economy.futures import futures_command
from bots.economy.glbonds import glbonds_command
from bots.economy.grains import grains_command
from bots.economy.indices import indices_command
from bots.economy.meats import meats_command
from bots.economy.metals import metals_command
from bots.economy.overview import overview_command
from bots.economy.performance import performance_command
from bots.economy.softs import softs_command
from bots.economy.usbonds import usbonds_command
from bots.economy.valuation import valuation_command
from bots.helpers import ShowView
from bots.common import commands_dict


class EconomyCommands(commands.Cog):
    """Economy Commands menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="econ-feargreed")
    async def feargreed(self, inter: disnake.AppCmdInter):
        """Feargreed command [CNN]"""
        await ShowView().discord(feargreed_command, inter, "econ-feargreed")

    @commands.slash_command(name="econ-overview")
    async def overview(self, inter: disnake.AppCmdInter):
        """Market data overview [Wall St. Journal]"""
        await ShowView().discord(overview_command, inter, "econ-overview")

    @commands.slash_command(name="econ-indices")
    async def indices(self, inter: disnake.AppCmdInter):
        """US indices overview [Wall St. Journal]"""
        await ShowView().discord(indices_command, inter, "econ-indices")

    @commands.slash_command(name="econ-futures")
    async def futures(self, inter: disnake.AppCmdInter):
        """Futures and commodities overview [Wall St. Journal]"""
        await ShowView().discord(futures_command, inter, "econ-futures")

    @commands.slash_command(name="econ-usbonds")
    async def usbonds(self, inter: disnake.AppCmdInter):
        """US bonds overview [Wall St. Journal]"""
        await ShowView().discord(usbonds_command, inter, "econ-usbonds")

    @commands.slash_command(name="econ-glbonds")
    async def glbonds(self, inter: disnake.AppCmdInter):
        """Global bonds overview [Wall St. Journal]"""
        await ShowView().discord(glbonds_command, inter, "econ-glbonds")

    @commands.slash_command(name="econ-energy")
    async def energy(self, inter: disnake.AppCmdInter):
        """Displays energy futures data [Finviz]"""
        await ShowView().discord(energy_command, inter, "econ-energy")

    @commands.slash_command(name="econ-metals")
    async def metals(self, inter: disnake.AppCmdInter):
        """Displays metals futures data [Finviz]"""
        await ShowView().discord(metals_command, inter, "econ-metals")

    @commands.slash_command(name="econ-meats")
    async def meats(self, inter: disnake.AppCmdInter):
        """Displays meats futures data [Finviz]"""
        await ShowView().discord(meats_command, inter, "econ-meats")

    @commands.slash_command(name="econ-grains")
    async def grains(self, inter: disnake.AppCmdInter):
        """Displays grains futures data [Finviz]"""
        await ShowView().discord(grains_command, inter, "econ-grains")

    @commands.slash_command(name="econ-softs")
    async def softs(self, inter: disnake.AppCmdInter):
        """Displays softs futures data [Finviz]"""
        await ShowView().discord(softs_command, inter, "econ-softs")

    @commands.slash_command(name="econ-currencies")
    async def currencies(self, inter: disnake.AppCmdInter):
        """Currencies overview [Wall St. Journal]"""
        await ShowView().discord(currencies_command, inter, "econ-currencies")

    @commands.slash_command(name="econ-valuation")
    async def valuation(
        self,
        inter: disnake.AppCmdInter,
        economy_group: str = commands.Param(choices=commands_dict.econ_group),
    ):
        """Valuation of sectors, industry, country [Finviz]

        Parameters
        -----------
        economy_group: Economy Group
        """
        await ShowView().discord(
            valuation_command, inter, "econ-valuation", economy_group
        )

    @commands.slash_command(name="econ-performance")
    async def performance(
        self,
        inter: disnake.AppCmdInter,
        economy_group: str = commands.Param(choices=commands_dict.econ_group),
    ):
        """Performance of sectors, industry, country [Finviz]

        Parameters
        -----------
        economy_group: Economy Group
        """
        await ShowView().discord(
            performance_command, inter, "econ-performance", economy_group
        )


def setup(bot: commands.Bot):
    bot.add_cog(EconomyCommands(bot))
