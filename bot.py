import os
import discord
import psycopg2
from discord.ext import commands

bot = commands.Bot(command_prefix=["!"], case_insensitive=True)
db = psycopg2.connect(
    database="dekd8sq403uspf",
    user="tpgzyglxzdlzgq",
    host="ec2-34-231-183-74.compute-1.amazonaws.com",
    password=os.environ.get("DB_PASS"),
    port="5432"
)
dbcrs = db.cursor()


@bot.command()
async def fupdate(ctx):
    """Force a complete recall of the database"""
    if ctx.author.id != 589477926961938443:
        await ctx.send("You cannot use this command!")

    else:
        ret = dbcrs.execute("SELECT cid, did, rat FROM users")
        rows = ret.fetchall()
        for user in rows:
            print(user)
