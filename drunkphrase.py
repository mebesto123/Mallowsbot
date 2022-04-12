import discord
import pandas as pd
from time import sleep
from gtts import gTTS
import os


async def addDrunkPhrase(message):
    
    cmd = message.content.split(" ", 1 )
    if len(cmd) < 2:
        commandError(message.channel, "Incorrect use of the command. Try -help drunkphrase to see correct uses")
        return
    
    text = cmd[1]   
    
    
    await message.channel.send(":white_check_mark: " + message.author.name + " has added a Drunk Phrase for" )
    print(message.content)

async def playDrunkPhrase(message, repoPath):
    
    cmd = message.content.split(" ", 1 )[1][1:].split('"', 1 )
    if len(cmd) < 2:
        await commandError(message.channel, "Incorrect use of the command. Try -help drunkphrase to see correct uses")
        return
    
    text = cmd[0]
    if not cmd[1].isspace() and cmd[1] is not "":
        args = cmd[1].split(" ")
        langs = drunkPhraseLangs()
        key_list = list(langs.keys())
        val_list = list(langs.values())
        region = None
        language = None
        for x in args:
            if "region:" in x:
                region = x.split(":")[1]
                if region not in key_list:
                    await commandError(message.channel, "Region is not recongized the bot. Please use `-help drunkphrase langs` for full list")
                    return

            if "language:" in x:
                language = x.split(":")[1]
                if language not in val_list:
                    await commandError(message.channel, "Language is not recongized the bot. Please use `-help drunkphrase langs` for full list")
                    return


        if region is None and language is not None:
            region = key_list[val_list.index(language)]
        elif region is not None and language is None:
            language = val_list[key_list.index(region)]
        elif region is None and language is None:
            language = 'en'
            region = 'com'
        else:
            pass
    else:
        language = 'en'
        region = 'com'
    
    myobj = gTTS(text=text, lang=language, slow=False, tld=region)    
    myobj.save("DrunkPhrase.mp3")
    await playfile("DrunkPhrase.mp3", message.author, repoPath)

async def playUserPhrase(message):
    print('Test')
    
async def helpDrunkPhrase(message):
    if message.content.lower().startswith("-help drunkphrase langs"):
        command = "-help drunkphrase langs"
        text = "Listed is all the possible languages and regions to use with the Drunk Phrases: \n"
        dpl = drunkPhraseLangs()
        for x in dpl:
            text += "language:" + dpl[x] + " region:" + x +  " \n"

    else:
        command = message.content
        text = "This is an unknown command, please try something like `-help drunkphrase` or `-help drunkphrase add`"

    await sendHelp(message, command, text)
    
async def playfile(song, member, repoPath):
    path = repoPath + '\Video.Audio'
    if member.voice.channel is not None and member.bot == False:
        vc = await member.voice.channel.connect()
        path += "\\" + song
        vc.play(discord.FFmpegPCMAudio(path, executable= repoPath + r"\ffmpeg\bin\ffmpeg.exe"))
        while vc.is_playing():
            #Start Playing
            sleep(.1)            
        await vc.disconnect()

def drunkPhraseLangs():
    d = {
        "co.uk":"en",
        "com":"en",
        "ca":"en",
        "co.in":"en",
        "ie":"en",
        "co.za":"en",
        "ca":"fr",
        "fr":"fr",
        "cn":"zh-CN",
        "com.hk":"zh-TW",
        "com.br":"pt",
        "pt":"pt",
        "com.mx":"es",
        "es":"es"
    }
    return d

        
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
    
async def commandError(channel,error):
    embed = discord.Embed(
            color=discord.Color.red())
    embed.add_field(name="Error",value=str(error))
    await channel.send(embed=embed)
        
async def sendError(guild,e):
    
    botchannel = None
    for item in guild.channels:
        if item.name.lower() == "bots" and type(item) == discord.TextChannel:
            botchannel = item
            break
            
    if botchannel == None:
        return
        
    
    embed = discord.Embed(
            color=discord.Color.red())
    embed.add_field(name="Error",value=str(e))
    await botchannel.send(embed=embed)

async def sendHelp(message, command, text):
    embed = discord.Embed(
            title="Help",
            color=discord.Color.blurple())
    embed.add_field(name=command,value=text)
    await message.channel.send(embed=embed)