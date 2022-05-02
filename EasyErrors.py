import discord

async def easyError(message, errorString):
    embed = discord.Embed(
        #title="Command Error",
        color=discord.Color.red())
    embed.add_field(name="Error",value=errorString)
    await message.channel.send(embed=embed)