import auth
import time
import discord
import psycopg2
import requests
from typing import Union
from discord.ext import commands, tasks


def refresh_vatcan():
    headers = {
        "Authorization": config["VATCAN_KEY"]
    }
    crs = db.cursor()
    crs.execute("SELECT * FROM {}".format(config["DATABASE_TABLE"]))
    for entry in crs:
        if entry[1] == 0: # User doesn't have discord linked, ignored
            continue
        else:
            data = requests.get(f"https://api.vatcan.ca/v2/user/{entry[0]}", headers=headers)
            if data.status_code == 404: # Somehow a user without a CID got committed or someone forgot to switch off the dev table
                continue
            else:
                udata = data.json()
                crs.close()
                crs = db.cursor()
                crs.execute(f"UPDATE {config['DATABASE_TABLE']} SET rating = {int(udata['data']['rating'])} WHERE cid = {entry[0]}")
                crs.close()


def find_rating(member_roles, member_rating) -> Union[int, None]:
    rids = [role.id for role in member_roles]
    for rid in rids:
        for rating, role in dev_ratings.items():
            if role == rid:
                if rating != member_rating:
                    return role
    return None


config = auth.return_auth()
ratings = {
    2: None,
    3: None,
    4: None,
    5: None,
    7: None,
    8: None,
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
    """Async task to update roles as needed"""
    with db.cursor() as dbcrs:
        guild: discord.Guild = bot.get_guild(config["GUILD_ID"])
        dbcrs.execute("SELECT * FROM {}".format(config["DATABASE_TABLE"]))
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
                        # User's rating role is up-to-date, ignore
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
    """Decorator to ensure the user is a dev"""
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
    embed = discord.Embed(title="Completed",
                          description=f"Completion time: {round(end - start, 3)}",
                          color=discord.Colour.green()
                          )
    await ctx.send(embed=embed)


@is_dev()
@bot.command()
async def starttask(ctx):
    """Starts the updater task, pending deprecation in favor of automation"""
    update_tasker.start()
    embed = discord.Embed(title="Completed", description=f"Task started", color=discord.Colour.green())
    await ctx.send(embed=embed)


@is_dev()
@bot.command()
async def dbexec(ctx, *, query):
    """Execute a given query against the db"""
    try:
        dbcrs = db.cursor()
        dbcrs.execute(query)
        if "SELECT" in query.lower():
            await ctx.author.send(list(dbcrs))
        dbcrs.close()
        db.commit()
        await ctx.send("Command completed")
    except Exception as e:
        print(e)
        await ctx.send("Command failed for reason: {}".format(e))
    finally:
        # noinspection PyBroadException
        try:
            dbcrs.close()
            db.commit()
        except Exception:
            pass


@is_dev()
@bot.command()
async def stop(ctx):
    """Panic button (closes the bot)"""
    await bot.close()


bot.run(config["TOKEN"])
