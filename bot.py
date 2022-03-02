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


def is_dev():
    def predicate(ctx):
        return ctx.author.id == 589477926961938443

    return discord.ext.commands.check(predicate)


@is_dev()
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


@is_dev()
@bot.command()
async def dbexec(ctx, *, query):
    try:
        out = dbcrs.execute(query)
        await ctx.author.send(out)
        await ctx.send("Command completed")
    except Exception as e:
        print(e)
        await ctx.send("Command failed for reason: {}".format(e))


bot.run(os.environ.get("BOT_TOKEN"))
