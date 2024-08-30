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


async def stats_embed(user: hikari.User, gov_id: int, acc_category: str):
    """
    Builds an embed from individual player stats based on the stats type.

    Args:
        user (hikari.User): Hikari user object.
        gov_id (int): Governor ID.
        acc_category (str): Determines whether to fetch 'general' or 'kvk' stats.

    Returns:
        hikari.Embed or None: The constructed embed or None if no stats are found.
    """
    player_stats = rok_db.get_kvk_user_stats(gov_id, acc_category)

    if player_stats is None:
        return None

    userpfp = (
        user.avatar_url
        or "https://media.discordapp.net/attachments/1076154233197445201/1127610236744773792/discord-black-icon-1.png"
    )

    # Create the embed object
    embed = hikari.Embed(color=hikari.Color.from_rgb(0, 200, 250))

    if acc_category == "general":
        # General stats embed
        embed.title = "Basic Stats :chart_with_upwards_trend:"
        description = (
            f"**Governor**: {player_stats.get('Governor Name', '0')}\n"
            f"**Governor ID**: {player_stats.get('Governor ID', '0')}\n"
            f"**Alliance**: {player_stats.get('Alliance', 'Unknown')}\n"
            f"**Power**: {player_stats.get('Power', '0')}\n"
            f"**Kill Points**: {player_stats.get('Kill Points', '0')}\n"
        )
        embed.description = description
        embed.add_field(
            name="<:4_:1277422678470430750> T4 KILLS",
            value=player_stats.get("T4 Kills", "0"),
            inline=True,
        )
        embed.add_field(
            name="\n<:5_:1277422745960841276> T5 KILLS",
            value=player_stats.get("T5 Kills", "0"),
            inline=True,
        )
        embed.add_field(
            name="\n:skull: DEATHS", value=player_stats.get("Deaths", "0"), inline=True
        )
    elif acc_category == "kvk":
        # KvK stats embed
        embed.title = "KvK Personal Stats :chart_with_upwards_trend:"
        description = (
            f"**Governor**: {player_stats.get('Governor Name', '0')}\n"
            f"**Alliance**: {player_stats.get('Alliance', 'Unknown')}\n"
            f"**Power**: {player_stats.get('Power', '0')}\n"
            f"**Governor ID**: {player_stats.get('Governor ID', '0')}\n"
        )
        embed.description = description
        embed.add_field(
            name=":trophy: Rank",
            value=player_stats.get("Rank", "Unranked"),
            inline=True,
        )
        embed.add_field(
            name="DKP Required",
            value=player_stats.get("DKP Required", "0"),
            inline=True,
        )
        embed.add_field(
            name="DKP Achieved",
            value=player_stats.get("DKP Achieved", "0"),
            inline=True,
        )
        embed.add_field(
            name="<:4_:1277422678470430750> T4 KILLS",
            value=player_stats.get("T4 Kills", "0"),
            inline=True,
        )
        embed.add_field(
            name="\n<:5_:1277422745960841276> T5 KILLS",
            value=player_stats.get("T5 Kills", "0"),
            inline=True,
        )
        embed.add_field(
            name="\n:skull: DEATHS", value=player_stats.get("Deaths", "0"), inline=True
        )

    # Set the footer
    embed.set_footer(
        text=f"Requested by @{user.username}       Updated: 19 August 2024 ",
        icon=userpfp,
    )

    return embed
