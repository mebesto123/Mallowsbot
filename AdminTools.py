import discord

async def AdminTools(message):

    cmd = message.content.split(" ", 1 )

    # if message.content.lower().startswith("-help admin") or cmd is None:
    #     await AdminHelp(message)


async def AdminHelp(message):
    embed = discord.Embed(
        title="Help",
        color=discord.Color.blurple())
    embed.add_field(name="Admin Tools",value="Here is options for the admin tools. Please use all commands like `-admin <command>`")
    await message.channel.send(embed=embed)