import discord
import pandas as pd
from time import sleep
import os

client = discord.Client()
repoPath = r"C:\Users\Mebesto\Documents\Code and Shit\Discord Bots"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    #User name comes in like <@!#######>
    #also there is Get_All_Members
    #print("Author: ",message.author," Message: ",message.content)
    
    if message.content.lower().startswith("-connectiontune"):
        await connectionTune(message)
        
    
    if message.content.lower().startswith("-help connectiontune") or message.content.lower().startswith("-help mallowsbot"):
        await helpConnectionTune(message)
    
    
@client.event
async def on_voice_state_update(member, before, after):
    #print("Member Name", member.name,"Member Id ", member.id, "  Guild Id  ", member.guild.id)
    path = repoPath + '\Video.Audio'
    vc_before = before.channel
    vc_after = after.channel
        
    song = audioReader(member.guild.id,member.id)
    # Malllows Bot:883163633666908172 and Pancake: 239631525350604801
    if vc_after != vc_before and vc_after is not None and member.bot == False:
        try:
            if song != 'False':
                vc = await vc_after.connect()
                path += "\\" + song
                vc.play(discord.FFmpegPCMAudio(path))#, executable= repoPath + r"\ffmpeg\bin\ffmpeg.exe"))
                while vc.is_playing():
                    #Start Playing
                    sleep(.1)            
                await vc.disconnect()
            else:
                vc = await vc_after.connect()
                path += r"\teamspeak2.mp3"
                vc.play(discord.FFmpegPCMAudio(path))#, executable=repoPath + r"\ffmpeg\bin\ffmpeg.exe"))
                while vc.is_playing():
                    #Start Playing
                    sleep(.1)            
                await vc.disconnect()
        except discord.errors.ClientException as e:
            await sendError(member.guild, e)
            
 
async def helpConnectionTune(message):
    embed = discord.Embed(
            title="Help",
            color=discord.Color.blurple())
    embed.add_field(name="-connectiontune",value="Use this command like `-connectiontune` and upload your tune in the same message. Mallows Bot can play most file types but if your file type is not playing change to one of these file types `.mp3`, `.ogg`, or `.m4a`")
    await message.channel.send(embed=embed)
 
async def connectionTune(message):
    if len(message.attachments) == 1:
        file = message.attachments[0]
        path = repoPath + r"\Video.Audio"
        filename = str(message.author.id) + str(message.guild.id) + "Tune" + file.filename[file.filename.rfind("."):]
        await file.save(os.path.join(path,filename))
        updateSong(message.guild.id,message.author.id,filename)
        await message.channel.send(":white_check_mark: " + message.author.name + " has updated their Connection Tune!!" )
    else:
        embed = discord.Embed(
                #title="Command Error",
                color=discord.Color.red())
        embed.add_field(name="Error",value="Error using command `-connectiontune`. A single file with audio file type like `.mp3` or `.m4a` must be upload with the command.")
        await message.channel.send(embed=embed)

def audioReader(guildId, memberId):
    df = pd.read_csv(repoPath + r"\DiscordVoiceUsers.csv")
    song = df[(df.Guild == guildId) & (df.Member == memberId)].Song
    
    if song.empty:
        return 'False'
    
    return song.values[0]
    
def updateSong(guildId, memberId, songname):
    df = pd.read_csv(r"C:\Users\Mebesto\Documents\Code and Shit\Discord Bots\DiscordVoiceUsers.csv")
    exists = df[(df.Guild == guildId) & (df.Member == memberId)].index
    
    if exists.empty:
        temp = {"Guild": guildId,"Member": memberId,"Song": songname}
        df = df.append(temp, ignore_index=True)
        df.to_csv(r"C:\Users\Mebesto\Documents\Code and Shit\Discord Bots\DiscordVoiceUsers.csv", index=False)
    else:
        df.at[exists[0],"Song"] = songname
        df.to_csv(r"C:\Users\Mebesto\Documents\Code and Shit\Discord Bots\DiscordVoiceUsers.csv", index=False)
    
async def sendError(guild,e):
    
    botchannel = None
    for item in guild.channels:
        if item.name.lower() == "bots" and type(item) == discord.TextChannel:
            botchannel = item
            break
            
    if botchannel == None:
        return
        
    
    embed = discord.Embed(
            #title="Command Error",
            color=discord.Color.red())
    embed.add_field(name="Error",value=str(e))
    await botchannel.send(embed=embed)
    
client.run('ODgzMTYzNjMzNjY2OTA4MTcy.YTF8Og.HGLCYZYfyGXFgSwe5TnDIjDa2ok')

##General
##715933625396494358

##Install discord ffmpeg PyNaCl?
