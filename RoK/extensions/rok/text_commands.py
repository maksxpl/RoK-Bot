import hikari
import lightbulb
from extensions.rok.views import CustomMenu, StatsScreen
from extensions.database.rok import GetUser

plugin = lightbulb.Plugin("text_commands")
get_rok_user = GetUser()


@plugin.listener(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human or not event.content:
        return

    content = event.content.split()
    command = content[0].lower()
    prefix = "!"

    print("content: ", content)
    print("command: ", command)

    if command == prefix + "mystats":
        await mystats(event)


async def mystats(ctx: hikari.MessageCreateEvent):
    linked_ids = get_rok_user.gov_ids(ctx.author.id)
    if not linked_ids:
        await ctx.message.respond(
            "Sorry, I cannot find you! Please use linkme to link first."
        )
        return

    stats_menu = CustomMenu(ctx.author)
    builder = await stats_menu.build_response_async(
        plugin.app.d.miru,
        StatsScreen(stats_menu),
    )

    message = await ctx.message.respond(
        content=builder.content,
        components=builder.components,
    )

    plugin.app.d.miru.start_view(stats_menu, bind_to=message)


def load(bot) -> None:
    bot.add_plugin(plugin)
