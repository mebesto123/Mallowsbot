from email import message
import discord
from idna import check_nfc
import pandas as pd
from time import sleep
from discord.utils import find
import os

async def writeToVoiceLog(member, before, after):
    role = find(lambda x: x.name == 'Voice Log Notifications',  member.guild.roles)
    channel = find(lambda x: x.name == 'voice-channel-log',  member.guild.text_channels) 

    # Handle noneTypes
    # Todo: add error message logic
    if role is None or channel is None:
        return

    mess = role.mention + " "
    vc_before = before.channel
    vc_after = after.channel
    move = False

    if vc_after != vc_before and vc_after is not None and vc_before is None and member.bot == False:
        mess += member.name + " has join channel " + vc_after.name
        move = True
    elif vc_after != vc_before and vc_before is not None and vc_after is None and member.bot == False:
        mess += member.name + " has left channel " + vc_before.name
        move = True
    elif vc_after != vc_before and vc_before is not None and vc_after is not None and member.bot == False:
        mess += member.name + " moved to channel " + vc_after.name
        move = True

    if move:
        await channel.send(mess)