# pylint: disable=W0612
import disnake
from disnake.ext import commands

from bots import config_discordbot as cfg
from bots.common.help_text import cmds_text
from bots.menus.menu import Menu


class CmdsCommands(commands.Cog):
    """Command List"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="cmds")
    async def cmds(self, ctx: disnake.AppCmdInter):
        """Stocks Command List"""
        siatext = f"```md{cmds_text['sia']}```"
        etftext = f"```md{cmds_text['etf']}```"
        disctext = f"```md{cmds_text['disc']}```"
        misctext = f"```md{cmds_text['misc']}```"
        opttext = f"```md{cmds_text['opt']}```"
        tatext = (
            f"```md{cmds_text['ta']}```"
            f"```md{cmds_text['ta_candle']}```"
            f"```md{cmds_text['ta_ext']}```"
        )
        ddtext = f"```md{cmds_text['dd']}```"
        dpstext = f"```md{cmds_text['dps']}```"
        scrtext = f"```md{cmds_text['scr']}```"
        govtext = f"```md{cmds_text['gov']}```" f"{cmds_text['gov_ext']}"
        econtext = f"```md{cmds_text['econ']}```"
        options = [disnake.SelectOption(label="Home", value="0", emoji="🟢")]
        embeds = [
            disnake.Embed(
                title="Stocks: Technical Analysis Command List",
                description=tatext,
                color=cfg.COLOR,
            ),
            disnake.Embed(
                title="",
                description=(
                    f"**Options Command List**\n{opttext}\n"
                    f"**Dark Pool Shorts Command List**\n{dpstext}\n"
                    f"**Due Diligence Command List**\n{ddtext}\n"
                ),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                title="",
                description=(
                    f"**ETF Command List**\n{etftext}\n"
                    f"**Sector and Industry Analysis Command List**\n{siatext}\n"
                    f"**Stocks Discovery Command List**\n{disctext}\n"
                    f"**Other Command List**\n{misctext}\n"
                ),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                title="",
                description=(f"**Economy Command List**\n{econtext}\n"),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                title="",
                description=(
                    f"**Screener Command List**\n{scrtext}\n"
                    f"**Government Command List**\n{govtext}\n"
                ),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                title="No Manipulation Here",
                description="```diff\n- Nothing to SEC here..... Yet.\n```",
                color=cfg.COLOR,
            ),
        ]
        embeds[0].set_author(
            name=cfg.AUTHOR_NAME,
            url=cfg.AUTHOR_URL,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embeds[0].set_footer(
            text=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
        await ctx.send(embed=embeds[0], view=Menu(embeds, options))


def setup(bot: commands.Bot):
    bot.add_cog(CmdsCommands(bot))
