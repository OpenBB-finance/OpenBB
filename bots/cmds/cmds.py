# pylint: disable=W0612
import disnake
from disnake.ext import commands

from bots import config_discordbot as cfg
from bots.menus.menu import Menu


class CmdsCommands(commands.Cog):
    """Command List"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="cmds")
    async def cmds(self, ctx: disnake.AppCmdInter):
        """Stocks Command List"""
        siatext = (
            "```md\n[sia metrics](ticker) <METRIC>\n"
            "[sia cps]() <COUNTRY>\n"
            "[sia cpic]() <INDUSTRY>\n```"
        )
        etftext = (
            "```md\n[etfs disc-tops]() <SORT>\n"
            "[etfs holdings by-etf](etf) <NUM>\n"
            "[etfs holdings by-ticker](ticker) <NUM>\n```"
        )
        disctext = (
            "```md\n[disc fidelity]()\n"
            "[disc ugs]() <NUM>\n"
            "[disc tops]() <SORT> <NUM>\n```"
        )
        misctext = (
            "```md\n[futures]()\n"
            "[quote](ticker)\n"
            "[support]() *Mods Only\n"
            "[ins-last](ticker) <NUM>\n"
            "[btc]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
            "[eth]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
            "[sol]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
            "[candle](ticker) <INTERVAL> <PAST_DAYS> <EXTENDED_HOURS> <START> <END> <HEIKIN_CANDLES> <NEWS>\n```"
        )
        opttext = (
            "```md\n[opt unu]()\n"
            "[opt info](ticker)\n"
            "[opt vsurf](ticker) <z>\n"
            "[opt oi](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
            "[opt vol](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
            "[opt overview](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
            "[opt hist](ticker) <STRIKE> <EXPIRATION> <OPT-TYPE>\n"
            "[opt grhist](ticker) <STRIKE> <EXPIRATION> <OPT-TYPE> <GREEK>\n"
            "[opt chain](ticker) <EXPIRATION> <OPT-TYPE> <MIN-SP> <MAX-SP>\n```"
        )
        tatext = (
            "```md\n[ta summary](ticker)\n"
            "[ta view](ticker)\n"
            "[ta recom](ticker)\n"
            "[ta fib](ticker) <START> <END>\n```"
            "```md\n[ta-vol obv](ticker) <START> <END>\n"
            "[ta-vol ad](ticker) <OPEN> <START> <END>\n"
            "[ta-mom cg](ticker) <LENGTH> <START> <END>\n"
            "[ta-mom fisher](ticker) <LENGTH> <START> <END>\n"
            "[ta-mom cci](ticker) <LENGTH> <SCALAR> <START> <END>\n"
            "[ta ma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
            "[ta-trend aroon](ticker) <LENGTH> <SCALAR> <START> <END>\n"
            "[ta-vol adosc](ticker) <OPEN> <FAST> <SLOW> <START> <END>\n"
            "[ta-mom macd](ticker) <FAST> <SLOW> <SIGNAL> <START> <END>\n"
            "[ta-vlt kc](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
            "[ta-trend adx](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
            "[ta-mom rsi](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
            "[ta-mom stoch](ticker) <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
            "[ta-vlt bbands](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
            "[ta-vlt donchian](ticker) <LWR_LENGTH> <UPR_LENGTH> <START> <END>\n```"
            "```md\n👆<INTERVAL> <PAST_DAYS> <EXTENDED_HOURS> <HEIKIN_CANDLES>👆\n```"
        )
        ddtext = (
            "```md\n[dd est](ticker)\n"
            "[dd sec](ticker)\n"
            "[dd analyst](ticker)\n"
            "[dd supplier](ticker)\n"
            "[dd customer](ticker)\n"
            "[dd arktrades](ticker)\n"
            "[dd pt](ticker) <RAW> <DATE_START>\n```"
        )
        dpstext = (
            "```md\n[dps hsi]() <NUM>\n"
            "[dps shorted](NUM)\n"
            "[dps psi](ticker)\n"
            "[dps spos](ticker)\n"
            "[dps dpotc](ticker)\n"
            "[dps pos]() <SORT> <NUM> <ASCENDING>\n"
            "[dps sidtc]() <SORT> <NUM>\n"
            "[dps ftd](ticker) <DATE_START> <DATE_END>\n```"
        )
        scrtext = (
            "```md\n[scr presets_default]()\n"
            "[scr presets_custom]()\n"
            "[scr historical](SIGNAL) <START>\n"
            "[scr overview](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr technical](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr valuation](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr financial](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr ownership](PRESET) <SORT> <LIMIT> <ASCEND>\n"
            "[scr performance](PRESET) <SORT> <LIMIT> <ASCEND>\n```"
        )
        govtext = (
            "```md\n[gov histcont](ticker)\n"
            "[gov lobbying](ticker) <NUM>\n"
            "[gov toplobbying]() <NUM> <RAW>\n"
            "[gov lastcontracts]() <DAYS> <NUM>\n"
            "[gov contracts](ticker) <DAYS> <RAW>\n"
            "[gov qtrcontracts]() <ANALYSIS> <NUM>\n"
            "[gov lasttrades]() <GOV_TYPE> <DAYS> <REP>\n"
            "[gov gtrades](ticker) <GOV_TYPE> <MONTHS> <RAW>\n"
            "[gov topbuys]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
            "[gov topsells]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n```"
            "\n`<DAYS> = Past Transaction Days`\n"
            "`<MONTHS> = Past Transaction Months`"
        )
        econtext = (
            "```md\n[econ softs]()\n"
            "[econ meats]()\n"
            "[econ energy]()\n"
            "[econ metals]()\n"
            "[econ grains]()\n"
            "[econ futures]()\n"
            "[econ usbonds]()\n"
            "[econ glbonds]()\n"
            "[econ indices]()\n"
            "[econ overview]()\n"
            "[econ feargreed]()\n"
            "[econ currencies]()\n"
            "[econ valuation]() <GROUP>\n"
            "[econ performance]() <GROUP>\n```"
        )
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
