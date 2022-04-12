import discord
import pandas as pd
from time import sleep
import os
import platform

async def helpConnectionTune(message):
    embed = discord.Embed(
            title="Help",
            color=discord.Color.blurple())
    embed.add_field(name="-connectiontune",value="Use this command like `-connectiontune` and upload your tune in the same message. Mallows Bot can play most file types but if your file type is not playing change to one of these file types `.mp3`, `.ogg`, or `.m4a`")
    await message.channel.send(embed=embed)

async def helpDisconnectionTune(message):
    embed = discord.Embed(
            title="Help",
            color=discord.Color.blurple())
    embed.add_field(name="-disconnectiontune",value="Use this command like `-disconnectiontune` and upload your tune in the same message. Mallows Bot can play most file types but if your file type is not playing change to one of these file types `.mp3`, `.ogg`, or `.m4a`")
    await message.channel.send(embed=embed)

async def createConnectionTune(message, repoPath, csvFile):
    if len(message.attachments) == 1:
        file = message.attachments[0]
        path = repoPath + os.path.sep + "Video.Audio"
        filename = str(message.author.id) + str(message.guild.id) + "Tune" + file.filename[file.filename.rfind("."):]
        await file.save(os.path.join(path,filename))
        updateSong(message.guild.id,message.author.id,filename, repoPath + os.path.sep + csvFile)
        await message.channel.send(":white_check_mark: " + message.author.name + " has updated their Connection Tune!!" )
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-connectiontune` or `-disconnectiontune`. A single file with audio file type like `.mp3` or `.m4a` must be upload with the command.")
        await message.channel.send(embed=embed)

def audioReader(guildId, memberId, repoPath):
    df = pd.read_csv(repoPath)
    song = df[(df.Guild == guildId) & (df.Member == memberId)].Song
    
    if song.empty:
        return 'False'
    
    return song.values[0]

def updateSong(guildId, memberId, songname, repoPath):
    df = pd.read_csv(repoPath)
    exists = df[(df.Guild == guildId) & (df.Member == memberId)].index
    
    if exists.empty:
        temp = {"Guild": guildId,"Member": memberId,"Song": songname}
        df = df.append(temp, ignore_index=True)
        df.to_csv(repoPath, index=False)
    else:
        df.at[exists[0],"Song"] = songname
        df.to_csv(repoPath, index=False)

async def playConnection(guildId, author, repoPath):
    song = audioReader(guildId, author.id, repoPath + os.path.sep + "DiscordVoiceUsers.csv")
    if song == 'False':
        song = "teamspeak2.mp3"
    await playfile(song, author, repoPath)

async def playDisconnection(guildId, author, repoPath, onDisconnect = None):
    song = audioReader(guildId, author.id, repoPath + os.path.sep + "DisconnectionVoiceUsers.csv")
    if song == 'False':
        song = "Userdisconnected.mp3"
    if onDisconnect is not None:
        await playfile(song, author, repoPath, onDisconnect)
    else:
        await playfile(song, author, repoPath)

async def playfile(song, member, repoPath, onDisconnect = None):
    path = repoPath + os.path.sep + 'Video.Audio'
    channel = member.voice.channel if onDisconnect is None else onDisconnect.channel
    if (member.voice is not None or onDisconnect is not None) and member.bot == False:
        vc = await channel.connect()
        path += os.path.sep + song
        exe = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
        vc.play(discord.FFmpegPCMAudio(path, executable= repoPath + os.path.sep + "ffmpeg" + os.path.sep + "bin" + os.path.sep + exe))
        while vc.is_playing():
            #Start Playing
            sleep(.1)            
        await vc.disconnect()