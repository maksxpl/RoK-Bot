from extensions.rok.SQLite import Db
import hikari

rok_db = Db()
# def int_len(n) -> int:
#     if n > 0:
#         digits = int(math.log10(n)) + 1
#     elif n == 0:
#         digits = 1
#     else:
#         digits = int(math.log10(-n)) + 2  # +1 if you don't count the '-'
#     return digits


async def stats_embed(gov_id: int, user: hikari.User, stats: str):
    """
    builds embed from individual player stats.

    Args:
        gov_id (int): Governor ID.
        user: Discord user.
    """
    player_stats = rok_db.get_kvk_stats(gov_id, stats)

    if player_stats is None:
        return None

    player_name = player_stats["Governor Name"]
    player_id = player_stats["Governor ID"]
    player_snapshot_power = player_stats["Power"]
    player_current_points = player_stats["Kill Points"]
    player_t4kills = player_stats["T4 Kills"]
    player_t5kills = player_stats["T5 Kills"]
    player_deads = player_stats["Deaths"]
    vendetta = player_stats["Alliance"]

    if user.avatar_url:
        userpfp = user.avatar_url
    else:
        userpfp = "https://media.discordapp.net/attachments/1076154233197445201/1127610236744773792/discord-black-icon-1.png"

    if player_stats:
        embed = hikari.Embed(color=hikari.Color.from_rgb(0, 200, 250))

        embed.title = f"Basic Stats :chart_with_upwards_trend: "

        description = f"**Governor**: {player_name if player_name else '0'}\n**Governor ID**: {player_id if player_id else '0'}\n**Alliance**:{vendetta}\n**Power**: {player_snapshot_power if player_snapshot_power else '0'}\n**Kill Points**:{player_current_points if player_current_points else '0'}\n"
        embed.description = description

        embed.add_field(
            name="<:4_:1277422678470430750> T4 KILLS",
            value=f"{player_t4kills}",
            inline=True,
        )
        embed.add_field(
            name="\n<:5_:1277422745960841276> T5 KILLS",
            value=f"{player_t5kills}",
            inline=True,
        )
        embed.add_field(name="\n:skull: DEATHS", value=f"{player_deads}", inline=True)

        embed.set_footer(
            text=f"Requested by @{user.username}       Updated: 19 August 2024 ",
            icon=f"{userpfp}",
        )
        return embed
