from re import I
import discord
import pandas as pd
import os
import EasyErrors

async def AdminTools(message, repoPath, client):

    cmd = message.content.split(" ", -1 )[1].lower()

    if cmd == "addrole":
        await addAdminRole(message, repoPath)
    elif cmd == "removerole":
        await removeAdminRole(message, repoPath)
    # elif cmd == "vcstop":
    #     await stopMallowsBots(message, repoPath, client)
    # if message.content.lower().startswith("-help admin") or cmd is None:
    #     await AdminHelp(message)

async def AdminRectionConfirms(reaction, user, repoPath):
    if reaction.message.embeds[0].title == 'Role Confirmation' and reaction.message.content == '':
            await confirmAdminRole(reaction, repoPath)
    elif reaction.message.embeds[0].title == 'Role Remove' and reaction.message.content == '':
            await confirmRemoveAdminRole(reaction, repoPath)

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

async def addAdminRole(message, repoPath):
    serverRoles = [ x.name.lower() for x in message.guild.roles]
    adminRoles = [x.lower() for x in adminRolesByGuild(message.guild.id, repoPath)]
    if message.content.split(" ", 2 )[2] == None:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
        
    if str(message.content.split(" ", 2 )[2]).lower() not in serverRoles:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
    
    if str(message.content.split(" ", 2 )[2]).lower() in adminRoles:
        await EasyErrors.easyError(message, "Role already is admin")
        return

    embed = discord.Embed(
        title="Role Confirmation",
        color=discord.Color.blurple())
    embed.add_field(name="Comfirm role: " + str(message.content.split(" ", 2 )[2]),value="Select the green check box to confirm or red to cancel the request.")
    m = await message.channel.send(embed=embed)
    emojis = ['✅','🚫']

    for emoji in emojis:
        await m.add_reaction(emoji)

async def removeAdminRole(message, repoPath):
    serverRoles = [ x.name.lower() for x in message.guild.roles]
    adminRoles = [x.lower() for x in adminRolesByGuild(message.guild.id, repoPath)]
    if message.content.split(" ", 2 )[2] == None:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
        
    if str(message.content.split(" ", 2 )[2]).lower() not in serverRoles:
        await EasyErrors.easyError(message, "You need to provide a that exists role.")
        return
    
    if str(message.content.split(" ", 2 )[2]).lower() not in adminRoles:
        await EasyErrors.easyError(message, "This role is already not an admin")
        return

    embed = discord.Embed(
        title="Role Remove",
        color=discord.Color.blurple())
    embed.add_field(name="Remove role: " + str(message.content.split(" ", 2 )[2]),value="Select the green check box to confirm or red to cancel the request.")
    m = await message.channel.send(embed=embed)
    emojis = ['✅','🚫']

    for emoji in emojis:
        await m.add_reaction(emoji)

async def confirmAdminRole(reaction, repoPath):

    if reaction.emoji == '✅':
        try:
            roleName = reaction.message.embeds[0].fields[0].name.replace("Comfirm role: ", "")
            role = next((x for x in reaction.message.guild.roles if x.name.lower() == roleName.lower()), None)
            df = pd.read_csv(repoPath + os.path.sep + "GuildAdminRoles.csv")
            row = {"Guild": reaction.message.guild.id,"Role": role.name}
            df = df.append(row, ignore_index=True)
            df.to_csv(repoPath + os.path.sep + "GuildAdminRoles.csv", index=False)
            await reaction.message.edit(content="Role " + role.name +  " Added as Admin ✅")
        except:
            await EasyErrors.easyError(reaction.message, "An unhandled Error ooccurred")
    elif reaction.emoji == '🚫':
        await reaction.message.edit(content="Cancelled 🚫")

async def confirmRemoveAdminRole(reaction, repoPath):

    if reaction.emoji == '✅':
        try:
            roleName = reaction.message.embeds[0].fields[0].name.replace("Remove role: ", "")
            role = next((x for x in reaction.message.guild.roles if x.name.lower() == roleName.lower()), None)
            df = pd.read_csv(repoPath + os.path.sep + "GuildAdminRoles.csv")
            row = df[(df.Guild == reaction.message.guild.id) & (df.Role == role.name)].index
            df = df.drop(labels=row[0], axis=0)
            df.to_csv(repoPath + os.path.sep + "GuildAdminRoles.csv", index=False)
            await reaction.message.edit(content="Role " + role.name +  " has been removed as Admin ✅")
        except:
            await EasyErrors.easyError(reaction.message, "An unhandled Error ooccurred")
    elif reaction.emoji == '🚫':
        await reaction.message.edit(content="Cancelled 🚫")


async def checkRole(guild: discord.Guild ,user: discord.User, roleName: str):
    role: discord.Role = [x for x in guild.roles if x.name.lower() == roleName.lower()][0]
    member  = [x for x in role.members if x.id == user.id][0]
    if member is not None:
        return True
    else:
        return False
    
    
# TODO: Find way to interupt the mid Connection Tune
# async def stopMallowsBots(message, repoPath, client):
#     if CheckClientsVoiceStatus(message, client.user):
#         await discord.VoiceProtocol(client, message.guild.get_member(client.user.id).voice.channel).disconnect()
#         await message.channel.send("✅ {0} disconnected successfully".format(client.user))
#     else:
#         EasyErrors.easyError("{0} is not connected in any voice channel.".format(client.user))

# def CheckClientsVoiceStatus(message, clientUser):
#     ##Check is client is in Voice
#     channels = message.guild.voice_channels
#     for channel in channels:
#         for memeber in  [message.guild.get_member(x) for x in list(channel.voice_states.keys())]:
#             if memeber.id == clientUser.id:
#                 return True
#     return False