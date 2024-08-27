import logging
import hikari
import lightbulb

plugin = lightbulb.Plugin("listeners")


@plugin.listener(lightbulb.events.LightbulbStartedEvent)
async def on_ready(event: lightbulb.LightbulbStartedEvent) -> None:
    print("Bot started, I think")
    logging.info("RoK-bot has started!")


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if not isinstance(event.exception, lightbulb.CommandInvocationError):
        logging.warning(event.exception.original)
        return

    await event.context.respond(
        embed=hikari.Embed(
            title="Error",
            description="Something went wrong during invocation of command",
            color=hikari.Color.from_rgb(250, 0, 0),
        )
    )


def load(bot):
    bot.add_plugin(plugin)
