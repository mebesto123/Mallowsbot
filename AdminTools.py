import discord
import pandas as pd
import os
import EasyErrors

async def AdminTools(message):

    cmd = message.content.split(" ", -1 )[1].lower()

    if cmd == "addrole":
        await confirmRole(message)

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

async def confirmRole(message):
    serverRoles = [ x.name.lower() for x in message.guild.roles]
    if message.content.split(" ", -1 )[2] == None:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
        
    if str(message.content.split(" ", -1 )[2]).lower() not in serverRoles:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
    
    embed = discord.Embed(
        title="Role Confirmation",
        color=discord.Color.blurple())
    embed.add_field(name="Comfirm role: " + str(message.content.split(" ", -1 )[2]),value="Select the green check box to confirm or red to cancel the request.")
    m = await message.channel.send(embed=embed)
    emojis = ['✅','🚫']

    for emoji in emojis:
        await m.add_reaction(emoji)
