import discord
import bots.config_discordbot as cfg


class GenericCommands(discord.ext.commands.Cog):
    """Generic discord.ext.commands."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @discord.ext.commands.command(name="about")
    async def about(self, ctx: discord.ext.commands.Context):
        """About OpenBB Terminal"""
        links = (
            "Join our community on discord: https://discord.gg/Up2QGbMKHY\n"
            "Follow our twitter for updates: https://twitter.com/gamestonkt\n"
            "Access our landing page: https://gamestonkterminal.vercel.app\n\n"
            "**Main maintainers:** DidierRLopes, jmaslek, aia\n"
        )
        partnerships = (
            "FinBrain: https://finbrain.tech\n"
            "Quiver Quantitative: https://www.quiverquant.com\n"
            "SentimentInvestor: https://sentimentinvestor.com\n"
        )
        disclaimer = (
            "Trading in financial instruments involves high risks including "
            "the risk of losing some, or all, of your investment amount, and "
            "may not be suitable for all investors. Before deciding to trade "
            "in financial instrument you should be fully informed of the risks "
            "and costs associated with trading the financial markets, carefully "
            "consider your investment objectives, level of experience, and risk "
            "appetite, and seek professional advice where needed. The data "
            "contained in OpenBB Terminal is not necessarily accurate. "
            "GST and any provider of the data contained in this website will not "
            "accept liability for any loss or damage as a result of your trading, "
            "or your reliance on the information displayed."
        )
        embed = discord.Embed(
            title="Investment Research for Everyone",
            description=links,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.add_field(name="Partnerships:", value=partnerships, inline=False)
        embed.add_field(name="Disclaimer:", value=disclaimer, inline=False)

        await ctx.send(embed=embed)

    @discord.ext.commands.command(name="usage")
    async def usage(self, ctx: discord.ext.commands.Context):
        usage_instructions_message = """
```
- Every command starts with an exclamation point "!".

- Any command can be triggered from the chat. For example:

  !about
  or
  !stocks.dps.spos tsla
  or
  !stocks.ta.recom tsla

- Help is available for all menus and functions.

  Call help for individual menus like this:
  !help DarkPoolShortsCommands

  Call help for individual commands like this:
  !help stocks.dps

- Call the help command to see the list of available menus:

  !help
```
        """
        await ctx.send(usage_instructions_message)


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(GenericCommands(bot))
