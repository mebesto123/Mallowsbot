import random
import discord
from EasyErrors import easyError


def BuildTeams(members, team_size):
    """Return list of teams (lists of Member objects) by shuffling and chunking.

    members: iterable of discord.Member
    team_size: positive int
    """
    if team_size <= 0:
        raise ValueError("team_size must be greater than 0")

    members_copy = list(members)
    random.shuffle(members_copy)
    return [members_copy[i : i + team_size] for i in range(0, len(members_copy), team_size)]


async def CreateTeams(message):
    # keep original entrypoint name for compatibility
    if message.author.voice is None:
        await easyError(message, "You need to be in a voice channel to use this command.")
        return

    channel = message.author.voice.channel
    members = [message.guild.get_member(x) for x in list(channel.voice_states.keys())]
    members = [m for m in members if m is not None]

    args = message.content.split()
    if len(args) < 2:
        await easyError(message, "You need to specify the number of members per teams, ie `-newTeams 2`")
        return

    try:
        numPerTeams = int(args[1])
    except ValueError:
        await easyError(message, "Incorrect use of command, format as follows `-newTeams #`, ie `-newTeams 2`")
        return

    if numPerTeams <= 0:
        await easyError(message, "Team size must be greater than 0.")
        return

    if numPerTeams > len(members):
        await easyError(message, f"Team size too large. There are only {len(members)} members in the channel.")
        return

    teams = BuildTeams(members, numPerTeams)
    await printTeams(message, teams)


async def printTeams(message, teams):
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="Created Teams", value="Teams were created as follows:", inline=False)

    for idx, team in enumerate(teams, start=1):
        member_names = " ".join(getattr(m, "display_name", str(m)) for m in team if m is not None)
        embed.add_field(name=f"Team {idx}", value=member_names or "No members", inline=True)

    await message.channel.send(embed=embed)