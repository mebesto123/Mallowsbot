import discord
import pandas as pd
from time import sleep
import os
import configparser
import connectionTune

client = discord.Client()
##Setting For Bot itself
config = configparser.ConfigParser()
config.read('.'+ os.path.sep + 'settings'+ os.path.sep + 'botsettings.ini')

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
        await connectionTune.createConnectionTune(message, config["DEFAULT"]["path"])
        
    
    if message.content.lower().startswith("-help connectiontune") or message.content.lower().startswith("-help mallowsbot"):
        await connectionTune.helpConnectionTune(message)
    
    if message.content.lower().startswith("-playconnectiontune") or message.content.lower().startswith("-playconnection"):
        await connectionTune.playConnection(message, config["DEFAULT"]["path"])
    
    
@client.event
async def on_voice_state_update(member, before, after):
    path = config["DEFAULT"]["path"] + '/Video.Audio'
    vc_before = before.channel
    vc_after = after.channel
        
    song = connectionTune.audioReader(member.guild.id,member.id, config["DEFAULT"]["path"])
    if vc_after != vc_before and vc_after is not None and member.bot == False:
        try:
            if song != 'False':
                vc = await vc_after.connect()
                path += "/" + song
                vc.play(discord.FFmpegPCMAudio(path,executable= config["DEFAULT"]["ffmpeg"]))
                while vc.is_playing():
                    #Start Playing
                    sleep(.1)            
                await vc.disconnect()
            else:
                vc = await vc_after.connect()
                path += r"/teamspeak2.mp3"
                vc.play(discord.FFmpegPCMAudio(path,executable= config["DEFAULT"]["ffmpeg"]))
                while vc.is_playing():
                    #Start Playing
                    sleep(.1)            
                await vc.disconnect()
        except discord.errors.ClientException as e:
            await sendError(member.guild, e)

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
    
client.run(config["KEY"]["clientkey"])
