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

async def createConnectionTune(message, repoPath):
    if len(message.attachments) == 1:
        file = message.attachments[0]
        path = repoPath + os.path.sep + "Video.Audio"
        filename = str(message.author.id) + str(message.guild.id) + "Tune" + file.filename[file.filename.rfind("."):]
        await file.save(os.path.join(path,filename))
        updateSong(message.guild.id,message.author.id,filename, repoPath)
        await message.channel.send(":white_check_mark: " + message.author.name + " has updated their Connection Tune!!" )
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-connectiontune`. A single file with audio file type like `.mp3` or `.m4a` must be upload with the command.")
        await message.channel.send(embed=embed)

def audioReader(guildId, memberId, repoPath):
    df = pd.read_csv(repoPath + os.path.sep + "DiscordVoiceUsers.csv")
    song = df[(df.Guild == guildId) & (df.Member == memberId)].Song
    
    if song.empty:
        return 'False'
    
    return song.values[0]

def updateSong(guildId, memberId, songname, repoPath):
    df = pd.read_csv(repoPath + os.path.sep + "DiscordVoiceUsers.csv")
    exists = df[(df.Guild == guildId) & (df.Member == memberId)].index
    
    if exists.empty:
        temp = {"Guild": guildId,"Member": memberId,"Song": songname}
        df = df.append(temp, ignore_index=True)
        df.to_csv(repoPath + os.path.sep + "DiscordVoiceUsers.csv", index=False)
    else:
        df.at[exists[0],"Song"] = songname
        df.to_csv(repoPath + os.path.sep + "DiscordVoiceUsers.csv", index=False)

async def playConnection(message, repoPath):
    song = audioReader(message.guild.id, message.author.id, repoPath)
    if song == 'False':
        song = "teamspeak2.mp3"
    await playfile(song, message.author, repoPath)

async def playfile(song, member, repoPath):
    path = repoPath + os.path.sep + 'Video.Audio'
    if member.voice.channel is not None and member.bot == False:
        vc = await member.voice.channel.connect()
        path += os.path.sep + song
        exe = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
        vc.play(discord.FFmpegPCMAudio(path, executable= repoPath + os.path.sep + "ffmpeg" + os.path.sep + "bin" + os.path.sep + exe))
        while vc.is_playing():
            #Start Playing
            sleep(.1)            
        await vc.disconnect()