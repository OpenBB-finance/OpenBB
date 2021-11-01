import discord
import config_discordbot as cfg


class GenericCommands(discord.ext.commands.Cog):
    """Generic discord.ext.commands."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="about")
    async def about(self, ctx: discord.ext.commands.Context):
        """About Gamestonk Terminal"""
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
            "contained in Gamestonk Terminal (GST) is not necessarily accurate. "
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


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(GenericCommands(bot))
