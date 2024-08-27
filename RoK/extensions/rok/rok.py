import hikari
import lightbulb
from extensions.rok.SQLite import Db
from extensions.rok.views import (
    CustomMenu,
    LinkmeScreen,
    UnlinkmeScreen,
    MystatsScreen,
)

plugin = lightbulb.Plugin("rok")

rok_db = Db()


#
# text commands
#


# @plugin.listener(hikari.MessageCreateEvent)
# async def on_message_create(event: hikari.MessageCreateEvent) -> None:
#     if not event.is_human or not event.content:
#         return

#     content = event.content.split()
#     command = content[0].lower()
#     prefix = "!"

#     if command == prefix + "unlinkme":
#         await handle_unlinkme(event, content)


#
# slash commands
#


@plugin.command
@lightbulb.command("mystats", "Check your governor statistics")
@lightbulb.implements(lightbulb.SlashCommand)
async def mystats(ctx: lightbulb.SlashContext) -> None:
    linked_ids = rok_db.get_user_ids(ctx.author.id)
    if not linked_ids:
        await ctx.respond(f"Sorry, I cannot find you! Please use linkme to link first.")
        return

    category_menu = CustomMenu(ctx.author)
    builder = await category_menu.build_response_async(
        plugin.app.d.miru,
        MystatsScreen(category_menu),
    )
    await builder.create_initial_response(ctx.interaction)
    plugin.app.d.miru.start_view(category_menu)


@plugin.command
@lightbulb.option("governor_id", "your governor id", int)
@lightbulb.command("linkme", "Links discord account with the database")
@lightbulb.implements(lightbulb.SlashCommand)
async def linkme(ctx: lightbulb.SlashContext) -> None:
    governor_id = ctx.options.governor_id
    # if int_len(governor_id) != 5:  # TODO add validation?
    #     await ctx.respond("Please provide proper governor ID")
    #     return

    username = rok_db.get_discord_user(ctx.author.id, governor_id, "general")
    if username is None:
        await ctx.respond(
            f"{ctx.author.mention} Sorry, I cannot find you! "
            "Please verify the ID you provided or check if you're included in the scan."
        )
        return
    confirm_menu = CustomMenu(ctx.user)
    builder = await confirm_menu.build_response_async(
        plugin.app.d.miru,
        LinkmeScreen(confirm_menu, username, governor_id),
    )
    await builder.create_initial_response(ctx.interaction)
    plugin.app.d.miru.start_view(confirm_menu)


@plugin.command
@lightbulb.command("unlinkme", "Uninks discord account from the database")
@lightbulb.implements(lightbulb.SlashCommand)
async def unlinkme(ctx: lightbulb.SlashContext) -> None:
    linked_ids = rok_db.get_user_ids(ctx.author.id)
    if not linked_ids:
        await ctx.respond(
            f"Sorry, I cannot find you! Seems like your account isn't linked."
        )
        return

    confirm_menu = CustomMenu(ctx.user)
    builder = await confirm_menu.build_response_async(
        plugin.app.d.miru,
        UnlinkmeScreen(confirm_menu),
    )
    await builder.create_initial_response(ctx.interaction)
    plugin.app.d.miru.start_view(confirm_menu)


def load(bot) -> None:
    bot.add_plugin(plugin)
