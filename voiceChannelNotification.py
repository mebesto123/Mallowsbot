import discord
import pandas as pd
import os
import EasyErrors

async def sendNotifications(member, before, after):
    1 + 1

async def setupVoiceChannelSubcriber(message, repoPath, csvFile):
    ms = message.content.split(" ", 1 )[1][1:].split('"', 1 )
    if len(ms) > 1:
        member = discord.utils.get(message.guild.members, name=ms[0])

        if member is None:
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcsub`: User `" + ms[0] + "` not found. Correct capitalization is required.")
            await message.channel.send(embed=embed)

        if vcCsvReader(message.guild.id, message.author.id, member.id, repoPath + os.path.sep + csvFile):
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcsub`: You already subcribed to User `" + ms[0] + "`.")
            await message.channel.send(embed=embed)

        df = pd.read_csv(repoPath + os.path.sep + csvFile)
        temp = {"Guild": message.guild.id,"Member": message.author.id, "Sub": member.id}
        df = df.append(temp, ignore_index=True)
        df.to_csv(repoPath + os.path.sep + csvFile, index=False)

        await message.channel.send(":white_check_mark: " + message.author.name + " has subcribed to " + ms[0] + "!!" )
            
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-vcsub`: You must use double quotes for user names `\"example_user_name\"`")
        await message.channel.send(embed=embed)


def vcCsvReader(guildId, memberId, subId, repoPath):
    df = pd.read_csv(repoPath)
    exist = df[(df.Guild == guildId) & (df.Member == memberId) & (df.Sub == subId)].Sub
    
    if exist.empty:
        return False
    
    return True
