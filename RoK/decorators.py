import functools

import hikari
import lightbulb
from extensions.rok.functions import is_admin


def administration_only(func):
    @functools.wraps(func)
    async def wrapper(ctx: lightbulb.SlashContext, *args, **kwargs) -> None:

        if await is_admin(ctx):
            return await func(ctx, *args, **kwargs)
        await ctx.respond(
            "You don't have access to this command", flags=hikari.MessageFlag.EPHEMERAL
        )

    return wrapper
