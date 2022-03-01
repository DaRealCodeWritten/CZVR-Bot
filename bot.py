import discord
from discord.ext import commands


bot = commands.Bot(command_prefix=["!"], case_insensitive=True)


@bot.command()
async def fupdate(ctx):
    """Force a complete recall of the database"""
    if ctx.author.id != 589477926961938443:
        await ctx.send("You cannot use this command!")

    else:
        #awaiting DB module
        pass
