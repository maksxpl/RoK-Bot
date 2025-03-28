from typing import Optional, Union

import hikari
import lightbulb
import miru
import miru.ext.menu
from extensions.rok.functions import stats_embed
from extensions.database.rok import GetUser, Id, KvK
from miru.ext import menu

user_id = Id()
get_rok_user = GetUser()
kvk = KvK()


class CustomMenu(menu.Menu):
    def __init__(self, author, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.author = author

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if ctx.user.id != self.author.id:
            await ctx.respond(
                "You're not allowed to interact with this panel",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        if self.message:
            for button in self.children:
                button.disabled = True
            await self.message.edit(components=self)


class LinkmeScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        username: str,
        gid: int,
    ) -> None:
        super().__init__(menu)
        self.username = username
        self.gid = gid

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent(
            f"Please confirm if this is your account?",
            embed=hikari.Embed(
                description=f"Username: {self.username}\nGovernor ID: {self.gid}",
                color=(0, 255, 0),
            ),
        )

    @menu.button(label="Yes")
    async def yes_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(LinkmeAccontSelectionScreen(self.menu, self.gid))

    @menu.button(label="No", style=hikari.ButtonStyle.DANGER)
    async def no_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.edit_response(
            content="Confirmation declined by the user.", components=None, embed=None
        )
        self.menu.stop()


class LinkmeAccontSelectionScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        gid: int,
    ) -> None:
        super().__init__(menu)
        self.gid = gid

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Please choose your account type")

    @menu.button(label="Main Account")
    async def main_acc_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        user_id.save(ctx.user.id, ctx.user.username, self.gid, "main")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()

    @menu.button(label="Alt Account", style=hikari.ButtonStyle.SECONDARY)
    async def second_acc_button(
        self, ctx: miru.ViewContext, button: miru.Button
    ) -> None:
        user_id.save(ctx.user.id, ctx.user.username, self.gid, "alt")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()

    @menu.button(label="Farm Account", style=hikari.ButtonStyle.SECONDARY)
    async def farm_acc_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        user_id.save(ctx.user.id, ctx.user.username, self.gid, "farm")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()


class UnlinkmeScreen(menu.Screen):
    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Which account would you like to unlink?")

    @menu.button(label="Main Account")
    async def main_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        acc_type = "main"
        if self.account_exists(ctx, acc_type):
            await self.menu.push(UnlinkmeConfirmationScreen(self.menu, ctx, acc_type))
        else:
            await ctx.edit_response("Account not found", components=None)

    @menu.button(label="Alt Account", style=hikari.ButtonStyle.SECONDARY)
    async def second_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        acc_type = "alt"
        if self.account_exists(ctx, acc_type):
            await self.menu.push(UnlinkmeConfirmationScreen(self.menu, ctx, acc_type))
        else:
            await ctx.edit_response("Account not found", components=None)

    @menu.button(label="Farm Account", style=hikari.ButtonStyle.SECONDARY)
    async def farm_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        acc_type = "farm"
        if self.account_exists(ctx, acc_type):
            await self.menu.push(UnlinkmeConfirmationScreen(self.menu, ctx, acc_type))
        else:
            await ctx.edit_response("Account not found", components=None)

    def account_exists(self, ctx: miru.ViewContext, acc_type: str) -> bool:
        user = ctx.user
        acc_id = get_rok_user.gov_ids(user.id)[acc_type]
        if not acc_id:
            return False
        return True


class UnlinkmeConfirmationScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        ctx: miru.ViewContext,
        acc_type: str,
    ):
        super().__init__(menu)
        self.ctx = ctx
        self.acc_type = acc_type

    async def build_content(self) -> menu.ScreenContent:
        user = self.ctx.user
        if acc := get_rok_user.gov_ids(user.id):
            acc_id = acc[self.acc_type]
        embed = hikari.Embed(
            title="Are you sure you want to unlink this account?",
            description=f"Username: {user.username}\nGovernor ID: {acc_id}",
            color=hikari.Color.from_rgb(250, 0, 0),
        )
        return menu.ScreenContent(embed=embed)

    @menu.button(label="Yes")
    async def yes_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        user_id.remove(ctx.user.id, self.acc_type)
        await ctx.edit_response(
            f"{self.acc_type.capitalize()} account unlinked",
            components=None,
            embeds=None,
        )

    @menu.button(label="No", style=hikari.ButtonStyle.DANGER)
    async def no_button(self, ctx: miru.ViewContext, button: menu.ScreenButton) -> None:
        await ctx.edit_response("Account unlinking cancelled", components=None)


class StatsScreen(menu.Screen):
    def __init__(self, menu: menu.Menu) -> None:
        super().__init__(menu)

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Choose your account")

    @menu.button(label="General")
    async def general_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(StatsTypeSelectionScreen(self.menu, "general"))

    @menu.button(label="KvK", style=hikari.ButtonStyle.SUCCESS)
    async def kvk_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(StatsTypeSelectionScreen(self.menu, "kvk"))


class StatsTypeSelectionScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        acc_category: str,
    ):
        super().__init__(menu)
        self.acc_category = acc_category

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Please specify")

    @menu.button(label="Main Account")
    async def main_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(StatsPostScreen(self.menu, ctx, self.acc_category, "main"))

    @menu.button(label="Alt Account", style=hikari.ButtonStyle.SECONDARY)
    async def second_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(StatsPostScreen(self.menu, ctx, self.acc_category, "alt"))

    @menu.button(label="Farm Account", style=hikari.ButtonStyle.SECONDARY)
    async def farm_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(StatsPostScreen(self.menu, ctx, self.acc_category, "farm"))


class StatsPostScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        ctx: Union[miru.ViewContext, lightbulb.SlashContext],
        acc_category: str,
        acc_type: str,
        user_id: Optional[hikari.Snowflake] = None,
    ):
        super().__init__(menu)
        self.ctx = ctx
        self.acc_category = acc_category
        self.acc_type = acc_type
        self.user_id = user_id

    async def build_content(self) -> menu.ScreenContent:
        user = await self.get_user()

        # if no id specified
        if self.user_id == None:
            # get it from database
            if gov_user := (
                get_rok_user.gov_user(
                    self.ctx.user.id, self.acc_category, self.acc_type
                )
            ):
                gov_user_id = gov_user["id"]
            # return if nothing was found
            else:
                return menu.ScreenContent(f"No {self.acc_type} account registered")

        else:
            gov_user_id = get_rok_user.gov_ids(user.id)[self.acc_type]

        embed = await stats_embed(user, gov_user_id, self.acc_category)
        return menu.ScreenContent(embed=embed)

    async def get_user(self) -> hikari.User:
        if self.user_id:
            if user_disc_id := (get_rok_user.discord_id_from_gov_id(self.user_id)):
                user = await self.ctx.bot.rest.fetch_user(user_disc_id)
            return user
        return self.ctx.user


class Top10View(miru.View):
    def __init__(self, category) -> None:
        super().__init__()
        self.category = category
        self.toggle_state = "nicknames"

    @miru.button(label="Toggle names")
    async def toggleNames_button(
        self, ctx: miru.ViewContext, button: miru.Button
    ) -> None:
        await ctx.edit_response(embed=self.embed(ctx))

    def embed(self, ctx: miru.ViewContext):
        top_players = kvk.kvk_top_x_player_stats(self.category)
        embed = hikari.Embed(
            title=f"Top 10 players by {self.category}",
            color=hikari.Color.from_rgb(0, 250, 0),
        )

        if self.toggle_state == "nicknames":
            for x, (player, details) in enumerate(top_players.items(), 1):
                embed.add_field(
                    f"{x}: {player}", f"<:4_:1277422678470430750> {details['score']}"
                )
            self.toggle_state = "ids"
        elif self.toggle_state == "ids":
            for x, (_, details) in enumerate(top_players.items(), 1):
                embed.add_field(
                    f"{x}: {details['player_id']}",
                    f"<:4_:1277422678470430750> {details['score']}",
                )
            self.toggle_state = "nicknames"
        return embed

    async def on_timeout(self) -> None:
        if self.message:
            for button in self.children:
                button.disabled = True
            await self.message.edit(components=self)
