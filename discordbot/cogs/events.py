import disnake
import disnake.ext.commands as commands


class EventListeners(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):
        print("Scheduled event create", repr(event), sep="\n", end="\n\n")

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):
        print("Scheduled event update", repr(before), repr(after), sep="\n", end="\n\n")

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        print("Scheduled event delete", repr(event), sep="\n", end="\n\n")

    @commands.Cog.listener()
    async def on_guild_scheduled_event_subscribe(self, event, user):
        print("Scheduled event subscribe", event, user, sep="\n", end="\n\n")

    @commands.Cog.listener()
    async def on_guild_scheduled_event_unsubscribe(self, event, user):
        print("Scheduled event unsubscribe", event, user, sep="\n", end="\n\n")


def setup(bot):
    bot.add_cog(EventListeners(bot))
    print(f"> Extension {__name__} is ready\n")
