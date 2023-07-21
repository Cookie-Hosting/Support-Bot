import discord
import aiosqlite
import datetime
import asyncio
import yaml
import sys
from discord.ext.commands import CommandNotFound
from discord.ext import commands

with open('config.yml', 'r') as file:
    maindata = yaml.safe_load(file)

guild_id = maindata["General"]["GUILD_ID"]
activity = maindata["General"]["ACTIVITY"].lower()
doing_activity = maindata["General"]["DOING_ACTIVITY"]
streaming_activity_twitch_url = maindata["General"]["STREAMING_ACTIVITY_TWITCH_URL"]
status = maindata["General"]["STATUS"].lower()
token = maindata["General"]["TOKEN"]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if status == "online":
    _status = getattr(discord.Status, status)
elif status == "idle":
    _status = getattr(discord.Status, status)
elif status == "dnd":
    _status = getattr(discord.Status, status)
elif status == "invisible":
    _status = getattr(discord.Status, status)
else:
    sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Status: {bcolors.ENDC}{bcolors.OKCYAN}{status}{bcolors.ENDC}
{bcolors.OKBLUE}Valid Options: {bcolors.ENDC}{bcolors.OKGREEN}{bcolors.UNDERLINE}online{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}idle{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}dnd{bcolors.ENDC}{bcolors.OKGREEN}, or {bcolors.UNDERLINE}invisible{bcolors.ENDC}
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 7
""")

if activity == "playing":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Game(name=doing_activity)
elif activity == "watching":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Activity(name=doing_activity, type=discord.ActivityType.watching)
elif activity == "listening":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Activity(name=doing_activity, type=discord.ActivityType.listening)
elif activity == "streaming":
    if streaming_activity_twitch_url == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Streaming Activity Twitch URL: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 6
""")
    elif not "https://twitch.tv/" in streaming_activity_twitch_url:
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Streaming Activity Twitch URL: {bcolors.OKBLUE}It Must Be A Valid Twitch URL!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 6
""")
    else:
        _activity = discord.Streaming(name=doing_activity, url=streaming_activity_twitch_url)
else:
    sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Activity: {bcolors.ENDC}{bcolors.OKCYAN}{activity}{bcolors.ENDC}
{bcolors.OKBLUE}Valid Options: {bcolors.ENDC}{bcolors.OKGREEN}{bcolors.UNDERLINE}playing{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}watching{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}listening{bcolors.ENDC}{bcolors.OKGREEN}, or {bcolors.UNDERLINE}streaming{bcolors.ENDC}
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 4
""")

intents = discord.Intents.all()
intents.message_content = True

initial_extensions = [
                      'cogs.tickets.tickets'
                      ]

class CookieHostingBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), owner_id=503641822141349888, intents=intents, activity=_activity, status=_status)
        self.persistent_views_added = False

    async def on_ready(self):

        print(f'Signed in as {self.user}')

        print('Attempting to sync commands...')
        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(id=guild_id))
        print('Succesfully synced slash commands!')

    async def setup_hook(self):
        for extension in initial_extensions:
            await self.load_extension(extension)

client = CookieHostingBot()
client.remove_command('help')

@client.command()
@commands.is_owner()
async def sqlite(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute("""
    CREATE TABLE counter (
        month INTEGER,
        number INTEGER
    )""")
    await cursor.close()
    await db.commit()
    await db.execute('INSERT INTO counter VALUES (?,?);', (datetime.date.today().month, 000))
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await a.delete()
    await ctx.message.delete()

@client.command()
@commands.is_owner()
async def delete(ctx):
    db = await aiosqlite.connect('database.db')
    await db.execute('DROP TABLE counter;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()

@client.command()
@commands.is_owner()
async def add(ctx: commands.Context, emoji: discord.PartialEmoji = None):
    if not emoji:
        await ctx.send("You need to provide an emoji!")
    else:
        await ctx.guild.create_custom_emoji(name=emoji.name, image=await emoji.read())

#\\\\\\\\\\\\Error Handler////////////
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, commands.errors.NotOwner):
        return
    raise error

client.run(token)