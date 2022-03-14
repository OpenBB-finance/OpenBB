from typing import List

import disnake
from disnake.ext import commands

import bots.config_discordbot as cfg
from bots import helpers

bot = commands.Bot()


class Menu(disnake.ui.View):
    def __init__(
        self, embeds: List[disnake.Embed], options: List[disnake.SelectOption]
    ):
        super().__init__(timeout=None)

        # Sets the embed list variable.
        self.embeds = embeds
        self.options = options

        # Current embed number.
        self.embed_count = 0

        # Disables previous page button by default.
        self.prev_page.disabled = True

        # Sets the footer of the embeds with their respective page numbers.
        self.count = 0
        self.set_link_button()

        for opt in options:
            self.selector.append_option(opt)  # pylint: disable=E1101
        for i, embed in enumerate(self.embeds):
            embed.set_footer(
                text=f"Page {i + 1} of {len(self.embeds)}",
                icon_url=cfg.AUTHOR_ICON_URL,
            )

    def set_link_button(self) -> None:
        if not hasattr(self, "link_button"):
            self.link_button: disnake.ui.Button = disnake.ui.Button(
                style=disnake.ButtonStyle.url,
                url="https://github.com/GamestonkTerminal/GamestonkTerminal",
                label="Site",
                row=0,
            )
            self.add_item(self.link_button)
        self.link_button.label = "Site"
        self.count += 1

    @disnake.ui.select(
        placeholder="Page Select",
        custom_id=f"select_{str(disnake.Member)}_{helpers.uuid_get()}",
        row=1,
    )
    async def selector(
        self,
        select: disnake.ui.Select,
        inter: disnake.MessageInteraction,
    ) -> None:
        self.set_link_button()
        s = ""
        str1 = s.join(select.values)
        ind = int(str1)
        self.embed_count = ind
        self.next_page.disabled = False
        self.prev_page.disabled = False
        if self.embed_count == 0:
            self.prev_page.disabled = True
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True
        print(select.values)
        await inter.response.edit_message(embed=self.embeds[ind], view=self)

    @disnake.ui.button(
        label="Previous page",
        emoji="<a:leftarrow:929686892339937371>",
        style=disnake.ButtonStyle.red,
        custom_id=f"persistent_view:prevpage_{str(disnake.Member)}_{helpers.uuid_get()}",
    )
    async def prev_page(  # pylint: disable=W0613
        self,
        button: disnake.ui.Button,
        interaction: disnake.MessageInteraction,
    ):
        # Decrements the embed count.
        self.embed_count -= 1

        # Gets the embed object.
        embed = self.embeds[self.embed_count]

        # Enables the next page button and disables the previous page button if we're on the first embed.
        self.next_page.disabled = False
        if self.embed_count == 0:
            self.prev_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(
        label="Next page",
        emoji="<a:rightarrow:929686891891155006>",
        style=disnake.ButtonStyle.red,
        custom_id=f"persistent_view:nextpage_{str(disnake.Member)}_{helpers.uuid_get()}",
    )
    async def next_page(  # pylint: disable=W0613
        self,
        button: disnake.ui.Button,
        interaction: disnake.MessageInteraction,
    ):
        # Increments the embed count.
        self.embed_count += 1

        # Gets the embed object.
        embed = self.embeds[self.embed_count]

        # Enables the previous page button and disables the next page button if we're on the last embed.
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)
