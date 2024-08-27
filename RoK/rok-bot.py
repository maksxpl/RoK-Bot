import os

import hikari
import lightbulb
import miru
from data_manager import bot_dir, config

os.chdir(bot_dir)  # set bot's work directory

bot_config = config()["bot"]

bot = lightbulb.BotApp(
    token=bot_config["token"],
    prefix=bot_config["prefix"],
    intents=hikari.Intents.ALL,
    owner_ids=bot_config["owner_id"],
    # default_enabled_guilds=[bot_config["guild_id"]],
    logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            # "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
            "miru": {"level": "INFO"},
        },
    },
)


# to ensure the bot's ability to write
@bot.listen(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent) -> None:
    if event.content and bot.get_me().mention in event.content:
        await event.message.respond("You mentioned me!")


bot.d.miru = miru.Client(bot)

if __name__ == "__main__":
    # main modules
    bot.load_extensions("extensions.rok.rok")
    bot.load_extensions("extensions.listeners")

    # external modules
    if os.path.exists(bot_dir + "/extensions/test.py"):
        bot.load_extensions("extensions.test")

    bot.run()
