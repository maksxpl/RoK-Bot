import hikari
import lightbulb
from extensions.rok.SQLite import Db
from extensions.rok.views import CustomMenu, LinkmeScreen, MystatsScreen, UnlinkmeScreen

plugin = lightbulb.Plugin("slash_commands")

rok_db = Db()


@plugin.command
@lightbulb.option("governor_id", "your governor id", int, required=True)
@lightbulb.command("linkme", "Link your account")
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

    for key, value in ctx.options.items():
        if value == None:  # if no options specified, send buttons
            confirm_menu = CustomMenu(ctx.user)
            builder = await confirm_menu.build_response_async(
                plugin.app.d.miru,
                LinkmeScreen(confirm_menu, username, governor_id),
            )
            await builder.create_initial_response(ctx.interaction)
            plugin.app.d.miru.start_view(confirm_menu)
            break


@plugin.command
@lightbulb.command("unlinkme", "Unlinks chosen account")
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


@plugin.command
@lightbulb.command("me", "Check your linked accounts")
@lightbulb.implements(lightbulb.SlashCommand)
async def me(ctx: lightbulb.SlashContext) -> None:
    main_id, alt_id, farm_id = rok_db.get_user_ids(ctx.user.id).items()
    embed = hikari.Embed(color=hikari.Color.from_rgb(0, 250, 0))

    spaced_ids = {}
    for x in [main_id, [0, 0], alt_id, [1, 1], [2, 2], farm_id]:
        spaced_ids[x[0]] = x[1]

    for key, value in spaced_ids.items():
        if len(str(value)) == 1:
            embed.add_field("\u200B", "\u200B", inline=True)
            continue

        if value:
            embed.add_field(key, value, inline=True)
        else:
            embed.add_field(key, f"-# Not found", inline=True)

    # Simplified version with no spaces
    # for key, value in ids.items():
    #     if value:
    #         embed.add_field(key, value, inline=True)
    #     else:
    #         embed.add_field(key, f"-# Not found", inline=True)

    await ctx.respond(embed=embed)


@plugin.command
## consider using options
# @lightbulb.option(
#     "category", "Select category", required=False, choices=["general", "kvk"]
# )
# @lightbulb.option(
#     "account", "Select account", required=False, choices=["main", "alt", "farm"]
# )
@lightbulb.command("mystats", "Check your governor statistics")
@lightbulb.implements(lightbulb.SlashCommand)
async def mystats(ctx: lightbulb.SlashContext) -> None:
    linked_ids = rok_db.get_user_ids(ctx.author.id)

    if not linked_ids:
        await ctx.respond(f"Sorry, I cannot find you! Please use linkme to link first.")
        return

    print(ctx.options.items())

    ## check if all options were specfied, if so, skip to confirmation
    # for key, value in ctx.options.items():
    # if not value:
    category_menu = CustomMenu(ctx.author)
    builder = await category_menu.build_response_async(
        plugin.app.d.miru,
        MystatsScreen(category_menu),
    )
    await builder.create_initial_response(ctx.interaction)
    plugin.app.d.miru.start_view(category_menu)
    return
    # await ctx.respond("skip to confirmation (placeholder)")


@plugin.command()
@lightbulb.command("total", "Fetch and display cumulative KvK stats of top 300 players")
@lightbulb.implements(lightbulb.SlashCommand)
async def total(ctx: lightbulb.Context) -> None:
    global_stats = rok_db.get_kvk_top_300_global_stats()
    if global_stats:
        embed = hikari.Embed(
            title="KvK stats of Top 300 by power",
            description="- Born to Fight! Trained to Kill! Prepared to Die! -",
            color=hikari.Color.from_rgb(0, 213, 255),
        )
        for key, value in global_stats.items():
            value = format(value, ",")
            embed.add_field(name=f"Total {key}", value=value or "No data", inline=True)
        embed.set_image(
            "https://cdn.discordapp.com/attachments/1276990017301905511/1278809400013881386/Group_1_2.png?ex=66d22790&is=66d0d610&hm=a4a7ab403813eb7a551554671bc27cfdea893114ecae009d8b807a890ae39579&"
        )
    else:
        await ctx.respond("No stats available.")


@plugin.command()
@lightbulb.option(
    "category",
    "Select category",
    required=True,
    choices=["T4 Kills", "T5 Kills", "Deaths"],
)
@lightbulb.command("top10", "Fetch and display top 10 players in selected category")
@lightbulb.implements(lightbulb.SlashCommand)
async def top10(ctx: lightbulb.Context) -> None:
    top_players = rok_db.get_kvk_top_x_player_stats(ctx.options.category)

    embed = hikari.Embed(
        title=f"Top 10 players by {ctx.options.category}",
        color=hikari.Color.from_rgb(0, 250, 0),
    )

    for x, (player, stat) in enumerate(top_players.items(), 1):
        # stat = format(int(stat), ",")
        embed.add_field(f"{x}: {player}", f"<:4_:1277422678470430750> {stat}")
    await ctx.respond(embed=embed)


def load(bot) -> None:
    bot.add_plugin(plugin)
