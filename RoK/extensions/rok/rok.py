import hikari
import lightbulb
from extensions.rok.SQLite import Db
from extensions.rok.views import (
    CustomMenu,
    Linkme_AccountConfirmationScreen,
    Mystats_CategorySelectionScreen,
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
    linked_ids = rok_db.get_gov_user(ctx.author.id, stats="general")
    if not linked_ids:
        await ctx.respond(f"Sorry, I cannot find you! Please use linkme to link first.")
        return

    category_menu = CustomMenu(ctx.author)
    builder = await category_menu.build_response_async(
        plugin.app.d.miru,
        Mystats_CategorySelectionScreen(category_menu),
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

    username = rok_db.get_discord_id(ctx.author.id, governor_id, "general")

    if username is None:
        await ctx.respond(
            f"{ctx.author.mention} Sorry, I cannot find you! "
            "Please verify the ID you provided or check if you're included in the scan."
        )
        return
    confirm_menu = CustomMenu(ctx.user)
    builder = await confirm_menu.build_response_async(
        plugin.app.d.miru,
        Linkme_AccountConfirmationScreen(confirm_menu, username, governor_id),
    )
    await builder.create_initial_response(ctx.interaction)
    plugin.app.d.miru.start_view(confirm_menu)


# UnlinkMe command handling
# async def handle_unlinkme(event: hikari.MessageCreateEvent, content: list[str]):
#     if len(content) == 1:
#         await event.message.respond(
#             "Please provide a governor ID, e.g., unlinkme 123456789"
#         )
#         return

#     linked_ids = await fetch_linked_ids(event.author.id)

#     if not linked_ids:
#         await event.message.respond(
#             f"{event.author.mention}\nSorry, I cannot find you! Please use linkme to link first."
#         )
#         return

#     await event.message.respond(
#         f"{event.author.mention}\nWhich account would you like to unlink?",
#         component=MyView3(linked_ids, event.author),
#     )


def load(bot) -> None:
    bot.add_plugin(plugin)
