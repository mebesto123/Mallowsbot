from operator import imod
import discord
import os
import platform
import random
from EasyErrors import easyError


async def CreateTeams(message):
    if message.author.voice is not None:
        channel = message.author.voice.channel
        members = [message.guild.get_member(x) for x in list(channel.voice_states.keys())]
        if len(message.content.split(" ")) > 1:
            try:
                numPerTeams = int(message.content.split(" ")[1])
            except:
                await easyError(message,"Incorrect use of comand, format as follows `-newTeams #`, ie `-newTeams 2`")
            else:
                if numPerTeams > len(members):
                    await easyError(message,"Team size to larger. There is only " + str(len(members)) + " members in the chanel.")
                else:
                    teams = []
                    memberUsed = []
                    numTeams = len(members)//numPerTeams
                    numTeams = numTeams if len(members) % numPerTeams == 0 else numTeams + 1
                    for x in range(0,numTeams):
                        print(x)
                        teams.append([])
                        for m in range(0 , numPerTeams):
                            counter = True
                            if len(members) == len(memberUsed):
                                break
                            while(counter):
                                member = random.randint(0, len(members)-1)
                                if member not in memberUsed:
                                    teams[x].append(members[member].name)
                                    memberUsed.append(member)
                                    counter = False
                    await printTeams(message, teams)
        else:
            await easyError(message,"You need to specify the number of members per teams, ie `-newTeams 2`")
    else:
        await easyError(message,"Error user of command is not in a Voice Channel. You need to be a voice channel to use the command.")

async def printTeams(message, teams):
    embed = discord.Embed(
        #title="Command Error",
        color=discord.Color.green())
    embed.add_field(name="Created Teams",value="Teams were created as followed",inline=False)
    counter = 1
    teamMembers = ""
    for team in teams:
        for member in team:
            teamMembers += member + " "
        embed.add_field(name="Team " + str(counter), value=teamMembers, inline=True)
        teamMembers = ""
        counter += 1
    await message.channel.send(embed=embed)