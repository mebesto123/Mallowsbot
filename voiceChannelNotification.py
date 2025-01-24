import discord
import pandas as pd
import os
import EasyErrors
from datetime import *


async def sendNotifications(member, before, after, repoPath):

    df = pd.read_csv(repoPath)
    subs = df[(df.Guild == member.guild.id) & (df.Sub == member.id)]

    vc_before = before.channel
    vc_after = after.channel

    if vc_after != vc_before and vc_after is not None and vc_before is None and member.bot == False and not subs.empty:
        for index, row in subs.iterrows():
            sub = discord.utils.get(member.guild.members, id=row.Member)
            channel = await sub.create_dm()
            await channel.send("{} has joined voice on {}".format(member.name, member.guild.name) )
            
async def setupVoiceChannelSubcriber(message, repoPath, csvFile):
    ms = message.content.split(" ")
    if len(ms) > 1 :
        member = discord.utils.get(message.guild.members, name=ms[1])

        if member is None:
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcsub`: User `" + ms[1] + "` not found. Correct capitalization is required.")
            await message.channel.send(embed=embed)
        elif vcCsvExist(message.guild.id, message.author.id, member.id, repoPath + os.path.sep + csvFile):
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcsub`: You already subcribed to User `" + ms[1] + "`.")
            await message.channel.send(embed=embed)
        else:
            df = pd.read_csv(repoPath + os.path.sep + csvFile)
            temp = {"Guild": message.guild.id,"Member": message.author.id, "Sub": member.id}
            df = df.append(temp, ignore_index=True)
            df.to_csv(repoPath + os.path.sep + csvFile, index=False)

            await message.channel.send(":white_check_mark: " + message.author.name + " has subcribed to " + ms[1] + "!!" )
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-vcsub`: No User name supplied")
        await message.channel.send(embed=embed)

async def setupVoiceChannelUnsubcriber(message, repoPath, csvFile):
    ms = message.content.split(" ")
    if len(ms) > 1 :
        member = discord.utils.get(message.guild.members, name=ms[1])

        if member is None:
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcunsub`: User `" + ms[1] + "` not found. Correct capitalization is required.")
            await message.channel.send(embed=embed)
        elif not vcCsvExist(message.guild.id, message.author.id, member.id, repoPath + os.path.sep + csvFile):
            embed = discord.Embed(
                    #title="Command Error",
                    color=discord.Color.red())
            embed.add_field(name="Error",value="Error using command `-vcunsub`: You are not subcribed to User `" + ms[1] + "`.")
            await message.channel.send(embed=embed)
        else:
            df = pd.read_csv(repoPath + os.path.sep + csvFile)
            df = df.drop(df[(df.Guild == message.guild.id) & (df.Member == message.author.id) & (df.Sub == member.id)].index)
            df.to_csv(repoPath + os.path.sep + csvFile, index=False)

            await message.channel.send(":white_check_mark: " + message.author.name + " has unsubcribed to " + ms[1] + "!!" )
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-vcunsub`: No User name supplied")
        await message.channel.send(embed=embed)
        
async def sendCampfire(member, before, after, repoPath):
    vc_before = before.channel
    vc_after = after.channel
    
    df = pd.read_csv(repoPath)
    message = df[(df.Guild == member.guild.id) & (df.Channel == vc_after)]
    if message.empty:
        return 'False'
    
    #1234567890123456789
    #2025-01-08 20:25:04.625175
    strTime = df.at[message.index[0],"EndTime"]
    timer = datetime.strptime(strTime[0:19], "%Y-%m-%d %H:%M:%S")
    if timer > datetime.now():
        df.drop(message.index[0])
        df.to_csv(repoPath, index=False)
        return 'False'

    if vc_after != vc_before and vc_after is not None and vc_before is None and member.bot == False and not message.empty:
        sub = discord.utils.get(member.guild.members, id=member.id)
        channel = await sub.create_dm()
        await channel.send(message.Message)
        
async def setupCampfire(message: discord.Message, repoPath, csvFile):
    #-setupcampfire action "channel" "message" durationHour=3hr
    path = repoPath + os.path.sep + csvFile
    msParSplit = message.content.split('"')
    msSpSplit = message.content.split(' ')
    if len(msSpSplit) >= 3:
        action = msSpSplit[1]
        if (action.lower() == "new" or  action.lower() == "add") and len(msSpSplit) > 3 and len(msSpSplit) >= 4:
            channel = msParSplit[1]
            id = channelCheck(message, channel)
            if id is not None:
                df: pd.DataFrame = pd.read_csv(path)
                notes: pd.DataFrame = df[(df.Guild == message.guild.id) & (df.Channel == id) & (datetime.strptime(notes.EndTime, "%Y-%m-%d %H:%M:%S") < datetime.now().__format__("%Y-%m-%d %H:%M:%S"))]
                df = df[(datetime.strptime(df.EndTime, "%Y-%m-%d %H:%M:%S") > datetime.now().__format__("%Y-%m-%d %H:%M:%S"))]
                df.to_csv(path, index=False)
                    
                if notes.empty:
                    t = (int(msParSplit[4].lstrip()) if msParSplit[4].lstrip().isdigit() else 3) if len(msParSplit) >= 5 else 3 
                    temp = {"Guild": message.guild.id,"Channel": message.channel.id,"Message": msParSplit[3], "EndTime": datetime.now() + timedelta(hours=t)}
                    df = df.append(temp, ignore_index=True)
                    df.to_csv(path, index=False)
                    embed = discord.Embed(
                            color=discord.Color.blurple())
                    embed.add_field(name="Add Message for Channel",value=":white_check_mark: Voice Channel is in use. It will free up at " + notes["EndTime"].iloc[0])
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                            color=discord.Color.red())
                    embed.add_field(name="Channel in Use",value="Voice Channel is in use. It will free up at " + notes["EndTime"].iloc[0])
                    await message.channel.send(embed=embed)
            
        if action.lower() == "edit" or  action.lower() == "update" and len(msSpSplit) > 3 and len(msSpSplit) >= 4:
            channel = msParSplit[1]
            id = channelCheck(message, channel)
            if id is not None:
                df: pd.DataFrame = pd.read_csv(path)
                notes: pd.DataFrame = df[(df.Guild == message.guild.id) & (df.Channel == id) & (datetime.strptime(notes.EndTime, "%Y-%m-%d %H:%M:%S") < datetime.now().__format__("%Y-%m-%d %H:%M:%S"))]
                df = df[(datetime.strptime(df.EndTime, "%Y-%m-%d %H:%M:%S") > datetime.now().__format__("%Y-%m-%d %H:%M:%S"))]
                df.to_csv(path, index=False)
                    
                if notes.empty:
                    t = (int(msParSplit[4].lstrip()) if msParSplit[4].lstrip().isdigit() else 3) if len(msParSplit) >= 5 else 3 
                    temp = {"Guild": message.guild.id,"Channel": message.channel.id,"Message": msParSplit[3], "EndTime": datetime.now() + timedelta(hours=t)}
                    df = df.append(temp, ignore_index=True)
                    df.to_csv(path, index=False)
                else:
                    embed = discord.Embed(
                            color=discord.Color.red())
                    embed.add_field(name="Channel in Use",value="Voice Channel is in use. It will free up at " + notes["EndTime"].iloc[0])
                    await message.channel.send(embed=embed)
                    
        if action.lower() == "end" or  action.lower() == "delete" and len(msSpSplit) >= 3 and len(msSpSplit) >= 2:  
            raise NotImplemented  
    
async def channelCheck(message: discord.Message, channel: str, action, repoPath):
    exist = [x for x in message.guild.voice_channels if channel.lower() == x.name.lower()]
    if len(exist) == 1:
        return exist[0].id
    else:
        cList = "``` \n"
        for c in message.guild.voice_channels:
            cList += c.name + "\n"
        cList += "```"
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Voice Channel was not found. Please use one of the following " + cList)
        await message.channel.send(embed=embed)
        return None
            
def vcCsvExist(guildId, memberId, subId, repoPath):
    df = pd.read_csv(repoPath)
    exist = df[(df.Guild == guildId) & (df.Member == memberId) & (df.Sub == subId)].Sub
    
    if exist.empty:
        return False
    
    return True

def joinedVoiceChannel():
    raise NotImplemented
    
def setVoiceChannelMessage():
    raise NotImplemented

        
