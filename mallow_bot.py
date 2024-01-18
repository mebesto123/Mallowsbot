import discord
import pandas as pd
from time import sleep
from discord.utils import find
import os
import configparser
import connectionTune
import voicechatlog
import Teams
import voiceChannelNotification

intents = discord.Intents.default()
intents.members = True
intents.members = True
intents.reactions = True
intents.voice_states = True
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

##Setting For Bot itself
config = configparser.ConfigParser()
config.read('.'+ os.path.sep + 'settings'+ os.path.sep + 'botsettings.ini')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}! I am Mallows Bot. Try `-help connectiontune` for Mallow Bot uses'.format(guild.name))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    #User name comes in like <@!#######>
    #also there is Get_All_Members
    #print("Author: ",message.author," Message: ",message.content)
    if message.content.lower().startswith("-vcsub"):
        await voiceChannelNotification.setupVoiceChannelSubcriber(message, config["DEFAULT"]["path"], config["DEFAULT"]["voicechannelnotifcsv"]) 

    if message.content.lower().startswith("-vcunsub"):
        await voiceChannelNotification.setupVoiceChannelUnsubcriber(message, config["DEFAULT"]["path"], config["DEFAULT"]["voicechannelnotifcsv"])
    
    if message.content.lower().startswith("-connectiontune"):
        await connectionTune.createConnectionTune(message, config["DEFAULT"]["path"], config["DEFAULT"]["connectioncsv"], "con")

    if message.content.lower().startswith("-disconnectiontune"):
        await connectionTune.createConnectionTune(message, config["DEFAULT"]["path"], config["DEFAULT"]["disconnectioncsv"], "dis")

    if message.content.lower().startswith("-help connectiontune") or message.content.lower().startswith("-help mallowsbot"):
        await connectionTune.helpConnectionTune(message)

    if message.content.lower().startswith("-help disconnectiontune") or message.content.lower().startswith("-help mallowsbot"):
        await connectionTune.helpDisconnectionTune(message)
    
    if message.content.lower().startswith("-playconnectiontune") or message.content.lower().startswith("-playconnection") or message.content.lower().startswith("-intro"):
        await connectionTune.playConnection(message.guild.id, message.author, config["DEFAULT"]["path"])

    if message.content.lower().startswith("-playdisconnectiontune") or message.content.lower().startswith("-playdisconnection") or message.content.lower().startswith("-outro"):
        await connectionTune.playDisconnection(message.guild.id, message.author, config["DEFAULT"]["path"])

    if message.content.lower().startswith("-teams") or message.content.lower().startswith("-newteams"):
        await Teams.CreateTeams(message)
    
# @client.event
# async def on_reaction_add(reaction, user):   
    
@client.event
async def on_voice_state_update(member, before, after):
    path = config["DEFAULT"]["path"] + os.path.sep + 'Video.Audio'
    vc_before = before.channel
    vc_after = after.channel

    #Send Voice Channel Log updates
    await voicechatlog.writeToVoiceLog(member, before, after)
    await voiceChannelNotification.sendNotifications(member, before, after, config["DEFAULT"]["path"] + os.path.sep + config["DEFAULT"]["voicechannelnotifcsv"])

    if vc_after != vc_before and vc_after is not None and member.bot == False:
        try:
            await connectionTune.playConnection(member.guild.id, member, config["DEFAULT"]["path"])
        except discord.errors.ClientException as e:
            await sendError(member.guild, e)
    elif vc_after != vc_before and vc_after is None and member.bot == False:
        try:
            await connectionTune.playDisconnection(member.guild.id, member, config["DEFAULT"]["path"], before)
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
