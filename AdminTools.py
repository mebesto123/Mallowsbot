import discord
import pandas as pd
import os

async def AdminTools(message):

    cmd = message.content.split(" ", 1 )

    await message.channel.send("Access Granted")

    # if message.content.lower().startswith("-help admin") or cmd is None:
    #     await AdminHelp(message)
def adminRolesByGuild(guildId, repoPath):
    df = pd.read_csv(repoPath + os.path.sep + "GuildAdminRoles.csv")
    roles = df[(df.Guild == guildId)].Role.tolist()
    
    return roles

async def AdminHelp(message):
    embed = discord.Embed(
        title="Help",
        color=discord.Color.blurple())
    embed.add_field(name="Admin Tools",value="Here is options for the admin tools. Please use all commands like `-admin <command>`")
    await message.channel.send(embed=embed)