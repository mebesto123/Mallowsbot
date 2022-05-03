from operator import imod
import discord
import os
import platform
import random
from EasyErrors import easyError


async def CreateTeams(message,client):
    if message.author.voice is not None:
        channel = message.author.voice.channel
        members = [message.guild.get_member(x) for x in list(channel.voice_states.keys())]
        if len(message.content.split(" ")) > 1:
            try:
                numTeams = int(message.content.split(" ")[1])
            except:
                await easyError(message,"Incorrect use of comand, format as follows `-newTeams #`, ie `-newTeams 2`")
            else:
                #Floor Dividing to make the smallest Max team size
                maxTeam = len(members)//numTeams
                teams = [[]] * numTeams
                for x in members:
                    teamCounter = True
                    while(teamCounter):
                        team = random.randint(0,numTeams-1)
                        print(team)
                        print(teams)
                        if len(teams[team]) < maxTeam:
                            teams[team].append(x.name)
                            teamCounter = False
                await printTeams(message, teams)
        else:
            await easyError(message,"You need to specify the number of teams, ie `-newTeams 2`")
    else:
        await easyError(message,"Error user of command is not in a Voice Channel. You need to be a voice channel to use the command.")

async def printTeams(message, teams):
    embed = discord.Embed(
        #title="Command Error",
        color=discord.Color.green())
    embed.add_field(name="Created Teams",value="Teams were created as folows",inline=False)
    counter = 1
    for team in teams:
        for member in team:
            embed.add_field(name="Team" + counter, value=member, inline=True)
        counter += 1
    await message.channel.send(embed=embed)