import discord
import pandas as pd
import os
import EasyErrors
from datetime import *
import sqlite3


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
        
async def helpCampfire(message: discord.Message):
    embed = discord.Embed(
            color=discord.Color.blurple())
    embed.add_field(name="Campfire Setup Help",value=f"""Mallows bot campfire is a way to send a message when a user joins a specific channel. Basic use: `-setupcampfire [action] “[channel]” “[message]” [durationHour=3hr]`. The channel needs to be a voice channel on the server.
                    Add Action
                    `add` or `new` Action is used to start a new campfire.
                    
                    Update Action
                    `update` or `edit` Action is used to update a campfire. If there is no campfire active, this command will act as an add action
                    
                    Delete Action
                    `delete` or `end` Action is used to end a campfire.
                    """)
    await message.channel.send(embed=embed)
        
async def sendCampfire(member: discord.Member, before, after, sqldb):
    vc_before = before.channel
    vc_after = after.channel
    
    if vc_after is None:
        return "False"
    
    sqliteConnection = sqlite3.connect(sqldb)
    cursor: sqlite3.Cursor = sqliteConnection.cursor()
    
    cursor.execute('''
                        SELECT * FROM campfire 
                        WHERE guild = ? 
                        AND channel = ? 
                    ''', (member.guild.id, vc_after.id))
    
    row = cursor.fetchone()
    
    if row is None:
        return 'False'
    
    #1234567890123456789
    #2025-01-08 20:25:04.625175
    strTime = row[4]
    timer = datetime.strptime(strTime[0:19], "%Y-%m-%d %H:%M:%S")
    if timer < datetime.now():
        cleanUpcampfire(sqliteConnection, cursor, member.guild.id)
        return 'False'

    if vc_after != vc_before and vc_after is not None and vc_before is None and member.bot == False:
        user = discord.utils.get(member.guild.members, id=member.id)
        channel = await user.create_dm()
        await channel.send(row[3])
        
async def setupCampfire(message: discord.Message, sqldb: str):
    #-setupcampfire action "channel" "message" durationHour=3hr
    sqliteConnection = sqlite3.connect(sqldb)
    cursor: sqlite3.Cursor = sqliteConnection.cursor()
    cleanUpcampfire(sqliteConnection, cursor, message.guild.id)
    msParSplit = message.content.split('"')
    if len(msParSplit) == 1:
        embed = discord.Embed(
                color=discord.Color.red())
        embed.add_field(name="Check Parentheses",value="Check your parentheses use \" not `""` ")
        await message.channel.send(embed=embed)
        sqliteConnection.close()
        return
    msSpSplit = message.content.split(' ')
    try:
        
        if len(msSpSplit) >= 3:
            action = msSpSplit[1]
            if (action.lower() == "new" or  action.lower() == "add") and len(msSpSplit) > 3 and len(msSpSplit) >= 4:
                channel = msParSplit[1]
                id = await channelCheck(message, channel)
                if id is not None:
                    endTime = campfireInUseCheck(cursor, message.guild.id, id)
                    if endTime is None:
                        t = (int(msParSplit[4].lstrip()) if msParSplit[4].lstrip().isdigit() else 3) if len(msParSplit) >= 5 else 3
                        saveTime = str(datetime.now() + timedelta(hours=t)) 
                        cursor.execute('''
                            INSERT INTO campfire (guild, channel, message, endTime) 
                            VALUES (?, ?, ?, ?)
                        ''', (message.guild.id, id, msParSplit[3], saveTime))
                        
                        embed = discord.Embed(
                                color=discord.Color.blurple())
                        embed.add_field(name="Added Message for Channel",value=f":white_check_mark: Message will now send on join to {channelName(message, id)}. It will free up at " + saveTime)
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                                color=discord.Color.red())
                        embed.add_field(name="Channel in Use",value="Voice Channel is in use. It will free up at " + endTime)
                        await message.channel.send(embed=embed)
                
            if action.lower() == "edit" or  action.lower() == "update" and len(msSpSplit) > 3 and len(msSpSplit) >= 4:
                channel = msParSplit[1]
                id = await channelCheck(message, channel)
                if id is not None:
                    endTime = campfireInUseCheck(cursor, message.guild.id, id)
                    if endTime is not None:
                        t = (int(msParSplit[4].lstrip()) if msParSplit[4].lstrip().isdigit() else 3) if len(msParSplit) >= 5 else 3
                        saveTime = str(datetime.now() + timedelta(hours=t)) 
                        cursor.execute('''
                            SELECT * FROM campfire 
                            WHERE guild = ? 
                            AND channel = ? 
                        ''', (message.guild.id, id))
                        
                        row = cursor.fetchone()
                        
                        cursor.execute('''UPDATE campfire 
                                       SET endTime = ?, message = ? 
                                       WHERE id = ?''',(saveTime, msParSplit[3], row[0]))
                        
                        embed = discord.Embed(
                                color=discord.Color.blurple())
                        embed.add_field(name="Update Message for Channel",value=f":white_check_mark: Message will now send on join to {channelName(message, id)}. It will free up at " + saveTime)
                        await message.channel.send(embed=embed)
                    else:
                        t = (int(msParSplit[4].lstrip()) if msParSplit[4].lstrip().isdigit() else 3) if len(msParSplit) >= 5 else 3
                        saveTime = str(datetime.now() + timedelta(hours=t)) 
                        cursor.execute('''
                            INSERT INTO campfire (guild, channel, message, endTime) 
                            VALUES (?, ?, ?, ?)
                        ''', (message.guild.id, id, msParSplit[3], saveTime))
                        embed = discord.Embed(
                                color=discord.Color.yellow())
                        embed.add_field(name="Channel was not in use. Added Message for Channel",value=f":white_check_mark: Message will now send on join to {channelName(message, id)}. It will free up at " + saveTime)
                        await message.channel.send(embed=embed)
                        
            if action.lower() == "end" or  action.lower() == "delete" and len(msSpSplit) >= 3 and len(msSpSplit) >= 2:  
                channel = msParSplit[1]
                id = await channelCheck(message, channel)
                if id is not None:
                    endTime = campfireInUseCheck(cursor, message.guild.id, id)
                    if endTime is not None:
                        cursor.execute('''
                            DELETE FROM campfire WHERE guild = ? AND channel = ? 
                        ''', (message.guild.id, id))
                        
                        embed = discord.Embed(
                                color=discord.Color.blurple())
                        embed.add_field(name="Delete Message for Channel",value=f":white_check_mark: Message deleted!")
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                                color=discord.Color.yellow())
                        embed.add_field(name="Channel is Free",value="Voice Channel is not in use. Use `-setupcampfire add` to set up a campfire")
                        await message.channel.send(embed=embed)
    except Exception as e:
        await EasyErrors.easyError(message, f"Error trying to create campfire: {e} ")
                      
        
    sqliteConnection.commit()
    sqliteConnection.close()
    
    
def channelName(message: discord.Message, id):
    result = next((obj for obj in message.guild.voice_channels if obj.id == id), None)
    
    if result:
        return result.name
    else:
        return ""
        
async def channelCheck(message: discord.Message, channel: str):
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
 
def campfireInUseCheck(cursor: sqlite3.Cursor, guild: int, channel):
    
    cursor.execute('''
        SELECT * FROM campfire 
        WHERE guild = ? 
        AND channel = ? 
    ''', (guild, channel))
    
    record = cursor.fetchall()
    if len(record) == 0 : 
        return None
    else:
        time = record[0][4]
        return datetime.strptime(time[0:19], "%Y-%m-%d %H:%M:%S")
    
def cleanUpcampfire(conn: sqlite3.Connection, cursor: sqlite3.Cursor, guild: int):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #clean up
    cursor.execute('''
        SELECT * FROM campfire 
        WHERE guild = ? 
        AND endTime < ?
    ''', (guild, current_time))
    
    clean = cursor.fetchall()
    if len(clean) > 0 :
        for row in clean:
            cursor.execute("DELETE FROM users WHERE id = ?", (row[0],))
            conn.commit()    
            
def vcCsvExist(guildId, memberId, subId, repoPath):
    df = pd.read_csv(repoPath)
    exist = df[(df.Guild == guildId) & (df.Member == memberId) & (df.Sub == subId)].Sub
    
    if exist.empty:
        return False
    
    return True
        
