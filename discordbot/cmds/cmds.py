# pylint: disable=W0612
import disnake
from disnake.ext import commands
from menus.menu import Menu

import discordbot.config_discordbot as cfg


class CmdsCommands(commands.Cog):
    """Command List"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="cmds")
    async def ta(self, ctx: disnake.AppCmdInter):
        """Stocks Command List"""
        misctext = "```md\n[disc-fidelity]()\n" "[ins-last](ticker) <num>\n```"
        opttext = (
            "```md\n[opt-unu]()\n"
            "[opt-iv](ticker)\n"
            "[opt-vsurf](ticker) <z>\n"
            "[opt-hist](ticker) <strike> <expiration> <opt-typ>\n"
            "[opt-oi](ticker) <expiration> <min-sp> <max-sp>\n"
            "[opt-vol](ticker) <expiration> <min-sp> <max-sp>\n"
            "[opt-overview](ticker) <expiration> <min-sp> <max-sp>\n"
            "[opt-chain](ticker) <expiration> <opt-typ> <min-sp> <max-sp>\n```"
        )
        tatext = (
            "```md\n[ta-summary](ticker)\n"
            "[ta-view](ticker)\n"
            "[ta-recom](ticker)\n"
            "[ta-obv](ticker) <START> <END>\n"
            "[ta-fib](ticker) <START> <END>\n"
            "[ta-ad](ticker) <OPEN> <START> <END>\n"
            "[ta-cg](ticker) <LENGTH> <START> <END>\n"
            "[ta-fisher](ticker) <LENGTH> <START> <END>\n"
            "[ta-cci](ticker) <LENGTH> <SCALAR> <START> <END>\n"
            "[ta-ema](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-sma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-wma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-hma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-zlma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-aroon](ticker) <LENGTH> <SCALAR> <START> <END>\n"
            "[ta-adosc](ticker) <OPEN> <FAST> <SLOW> <START> <END>\n"
            "[ta-macd](ticker) <FAST> <SLOW> <SIGNAL> <START> <END>\n"
            "[ta-kc](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
            "[ta-adx](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
            "[ta-rsi](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
            "[ta-stoch](ticker) <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
            "[ta-bbands](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
            "[ta-donchian](ticker) <LWR_LENGTH> <UPR_LENGTH> <START> <END>\n```"
        )
        ddtext = (
            "```md\n[dd-est](ticker)\n"
            "[dd-sec](ticker)\n"
            "[dd-analyst](ticker)\n"
            "[dd-supplier](ticker)\n"
            "[dd-customer](ticker)\n"
            "[dd-arktrades](ticker)\n"
            "[dd-pt](ticker) <RAW> <DATE_START>\n```"
        )
        dpstext = (
            "```md\n[dps.hsi]() <NUM>\n"
            "[dps.shorted](NUM)\n"
            "[dps.psi](ticker)\n"
            "[dps.spos](ticker)\n"
            "[dps.dpotc](ticker)\n"
            "[dps.pos]() <NUM> <SORT>\n"
            "[dps.sidtc]() <NUM> <SORT>\n"
            "[dps.ftd](ticker) <DATE_START> <DATE_END>\n```"
        )
        scrtext = (
            "```md\n[scr.presets_default]()\n"
            "[scr.presets_custom]()\n"
            "[scr.historical](SIGNAL) <START>\n"
            "[scr.overview](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr.technical](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr.valuation](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr.financial](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr.ownership](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr.performance](PRESET) <SORT> <LIMIT> <ASCEND>\n```"
        )
        govtext = (
            "```md\n[gov-histcont](ticker)\n"
            "[gov-lobbying](ticker) <NUM>\n"
            "[gov-toplobbying]() <NUM> <RAW>\n"
            "[gov-lastcontracts]() <DAYS> <NUM>\n"
            "[gov-contracts](ticker) <DAYS> <RAW>\n"
            "[gov-qtrcontracts]() <ANALYSIS> <NUM>\n"
            "[gov-lasttrades]() <GOV_TYPE> <DAYS> <REP>\n"
            "[gov-gtrades](ticker) <GOV_TYPE> <MONTHS> <RAW>\n"
            "[gov-topbuys]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
            "[gov-topsells]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n```"
            "\n`<DAYS> = Past Transaction Days`\n"
            "`<MONTHS> = Past Transaction Months`"
        )
        econtext = (
            "```md\n[econ-softs]()\n"
            "[econ-meats]()\n"
            "[econ-energy]()\n"
            "[econ-metals]()\n"
            "[econ-grains]()\n"
            "[econ-futures]()\n"
            "[econ-usbonds]()\n"
            "[econ-glbonds]()\n"
            "[econ-indices]()\n"
            "[econ-overview]()\n"
            "[econ-feargreed]()\n"
            "[econ-currencies]()\n"
            "[econ-valuation]() <GROUP>\n"
            "[econ-performance]() <GROUP>\n```"
        )
        options = [disnake.SelectOption(label="Home", value="0", emoji="🟢")]
        embeds = [
            disnake.Embed(
                title="Stocks: Technical Analysis Command List",
                description=tatext,
                color=cfg.COLOR,
            ),
            disnake.Embed(
                description=(
                    f"**Options Command List**\n{opttext}\n"
                    f"**Dark Pool Shorts Command List**\n{dpstext}\n"
                    f"**Due Diligence Command List**\n{ddtext}\n"
                ),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                description=(
                    f"**Screener Command List**\n{scrtext}\n"
                    f"**Government Command List**\n{govtext}\n"
                ),
                color=cfg.COLOR,
            ),
            disnake.Embed(
                description=(
                    f"**Economy Command List**\n{econtext}\n"
                    f"**Other Command List**\n{misctext}\n"
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
