import auth
import time
import discord
import psycopg2
from typing import Union
from discord.ext import commands, tasks


def find_rating(member_roles, member_rating) -> Union[int, None]:
    rids = [role.id for role in member_roles]
    for rid in rids:
        for rating, role in dev_ratings.items():
            if role == rid:
                if rating != member_rating:
                    return role
    return None


config = auth.return_auth()
dev_opts = {
    "GUILD_ID": 947764065118335016,
    "VATCAN_RQST": None,
    "VATSIM_OAUTH": "https://auth-dev.vatsim.net",
    "DB_TABLE": "dev"
}
ratings = {
    10: None,
    11: None,
    12: None
}
dev_ratings = {
    2: 948854540994744330,
    3: 948854399810285588,
    4: 948854291676942336,
    5: 948853954840776764,
    7: 948853678788460564,
    8: 948853042814517299,
    10: 948508009783525377,
    11: 948516513810358302,
    12: 948766506735509534
}
bot = commands.Bot(command_prefix=["!"], case_insensitive=True)
db = psycopg2.connect(
    database=config["DATABASE"],
    user=config["USER"],
    host=config["HOST"],
    password=config["PASS_DEV"],
    port="5432"
)


@tasks.loop(hours=24)
async def update_tasker():
    with db.cursor() as dbcrs:
        guild: discord.Guild = bot.get_guild(dev_opts["GUILD_ID"])
        dbcrs.execute("SELECT CID, DCID, RATING FROM {}".format(dev_opts["DB_TABLE"]))
        print("Executed query, doing loop")
        for record in dbcrs:
            print("Got guild!")
            member: discord.Member = await guild.fetch_member(record[1])
            print("Got member!")
            if member is None:
                print("No member object")
                # User is not part of the server or a null record was committed, ignore
                continue
            for role in member.roles:
                utd = False
                try:
                    if role.id == dev_ratings[record[2]]:
                        # User's rating role is up to date, ignore
                        utd = True
                        print("Member up to date")
                        continue
                    else:
                        continue
                except KeyError:
                    # User does not have a rating entry, this is erroneous
                    owner = await bot.fetch_user(703104766632263730)
                    await owner.send("WARN: Erroneous DB entry")
            if not utd:
                role = guild.get_role(dev_ratings[record[2]])
                await member.add_roles(role, reason="Automatic role update")
                not_matching = find_rating(member.roles, record[2])
                if not_matching is None:
                    continue
                else:
                    role = guild.get_role(not_matching)
                    await member.remove_roles(role, reason="Automatic update")


def is_dev():
    async def predicate(ctx):
        if ctx.author.id in [
            703104766632263730,
            212654520855953409,
            715758796059967498,
            160534932970536960
        ]:
            return True
        else:
            embed = discord.Embed(title="Access denied",
                                  description="This command is available to devs only",
                                  color=discord.Colour.red()
                                  )
            await ctx.send(embed=embed)
            return False

    return discord.ext.commands.check(predicate)


@is_dev()
@bot.command()
async def fupdate(ctx):
    """Force a complete recall of the database"""
    start = time.time()
    await update_tasker()
    await ctx.author.send("Completed database recall")
    end = time.time()
    embed = discord.Embed(title="Completed", description=f"Completion time: {round(end - start, 3)}")
    await ctx.send(embed=embed)


@is_dev()
@bot.command()
async def starttask(ctx):
    update_tasker.start()
    embed = discord.Embed(title="Completed", description=f"Task started")
    await ctx.send(embed=embed)


@is_dev()
@bot.command()
async def dbexec(ctx, *, query):
    try:
        dbcrs = db.cursor()
        dbcrs.execute(query)
        if "SELECT" not in query.lower():
            await ctx.author.send(list(dbcrs))
        dbcrs.close()
        db.commit()
        await ctx.send("Command completed")
    except Exception as e:
        print(e)
        await ctx.send("Command failed for reason: {}".format(e))
    finally:
        try:
            dbcrs.close()
            db.commit()
        except Exception:
            pass


@is_dev()
@bot.command()
async def stop(ctx):
    await bot.close()


bot.run(config["TOKEN"])
