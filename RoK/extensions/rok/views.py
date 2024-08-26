import hikari
import miru
import miru.ext.menu
from extensions.rok.SQLite import Db
from extensions.rok.functions import stats_embed
from miru.ext import menu

rok_db = Db()


class CustomMenu(menu.Menu):
    def __init__(self, author, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.author = author

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        print("figure out how to fix on_timeout")

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if ctx.user.id != self.author.id:
            await ctx.respond(
                "You're not allowed to interact with this panel",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False
        return True


class Linkme_AccountConfirmationScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        username: str,
        gid: str,
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
        await self.menu.push(Linkme_AccountTypeSelectionScreen(self.menu, self.gid))

    @menu.button(label="No", style=hikari.ButtonStyle.DANGER)
    async def no_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.edit_response(
            content="Confirmation declined by the user.", components=None, embed=None
        )
        self.menu.stop()


class Linkme_AccountTypeSelectionScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        gid: str,
    ) -> None:
        super().__init__(menu)
        self.gid = gid

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Please choose your account type")

    @menu.button(label="Main Account")
    async def main_acc_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        rok_db.save_id(ctx.user.id, ctx.user.username, self.gid, "main")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()

    @menu.button(label="2nd Account", style=hikari.ButtonStyle.SECONDARY)
    async def second_acc_button(
        self, ctx: miru.ViewContext, button: miru.Button
    ) -> None:
        rok_db.save_id(ctx.user.id, ctx.user.username, self.gid, "alt")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()

    @menu.button(label="Farm Account", style=hikari.ButtonStyle.SECONDARY)
    async def farm_acc_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        rok_db.save_id(ctx.user.id, ctx.user.username, self.gid, "farm")
        await ctx.edit_response(
            content="You have been successfully registered.", components=[]
        )
        self.menu.stop()


class Mystats_CategorySelectionScreen(menu.Screen):
    def __init__(self, menu: menu.Menu) -> None:
        super().__init__(menu)

    async def build_content(self) -> menu.ScreenContent:
        return menu.ScreenContent("Choose your account")

    @menu.button(label="General")
    async def general_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(Mystats_AccountTypeSelectionScreen(self.menu, "general"))

    @menu.button(label="KvK", style=hikari.ButtonStyle.SUCCESS)
    async def kvk_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(Mystats_AccountTypeSelectionScreen(self.menu, "kvk"))


class Mystats_AccountTypeSelectionScreen(menu.Screen):
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
        await self.menu.push(
            Mystats_postStatsScreen(self.menu, ctx, self.acc_category, "main")
        )

    @menu.button(label="2nd Account", style=hikari.ButtonStyle.SECONDARY)
    async def second_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(
            Mystats_postStatsScreen(self.menu, ctx, self.acc_category, "alt")
        )

    @menu.button(label="Farm Account", style=hikari.ButtonStyle.SECONDARY)
    async def farm_account_button(
        self, ctx: miru.ViewContext, button: menu.ScreenButton
    ) -> None:
        await self.menu.push(
            Mystats_postStatsScreen(self.menu, ctx, self.acc_category, "farm")
        )


class Mystats_postStatsScreen(menu.Screen):
    def __init__(
        self,
        menu: menu.Menu,
        ctx: miru.ViewContext,
        acc_category: str,
        acc_type: str,
    ):
        super().__init__(menu)
        self.ctx = ctx
        self.acc_category = acc_category
        self.acc_type = acc_type

    async def build_content(self) -> menu.ScreenContent:
        gov_user = rok_db.get_gov_user(self.ctx.user.id, stats="general")
        if not gov_user:
            return menu.ScreenContent(f"No {self.acc_type} registered")

        for account_type, details in gov_user.items():
            if account_type == self.acc_type:
                if self.acc_category == "general":
                    if not (
                        embed := await stats_embed(
                            details["id"], self.ctx.user, self.acc_category
                        )
                    ):
                        return menu.ScreenContent(f"No {self.acc_type} registered")
                    return menu.ScreenContent(embed=embed)
                else:
                    return menu.ScreenContent("placeholder Kvk")

        return menu.ScreenContent(f"No {self.acc_type} registered")
