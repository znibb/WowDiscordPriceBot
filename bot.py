import os
from discord.ext import commands
from dotenv import load_dotenv
from functions import *

# Command prefix
bot = commands.Bot(command_prefix='!')

# Load environment parameters
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
VERSION = os.getenv('VERSION')

# Variables
serverSet = False
factionSet = False

# Bot joins
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Command error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Error: Missing argument. Try !help.")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Error: Unknown command. Try !help.")
    else:
        raise error

# Bot commands
@bot.command(name="set_server", brief="Set server", help="Set server\nShow available servers with `!list_servers [EU/US]`", usage="<server>")
async def set_server(ctx, *arg):
    serverName = ' '.join(arg)
    if setServer(serverName):
        response = "Server setup successful: " + slugifyName(serverName)
        global serverSet
        serverSet = True
    else:
        response = "Error: Invalid server name: " + slugifyName(serverName)
    await ctx.send(response)

@bot.command(name="set_faction", brief="Set faction", help="Set faction, Alliance/Horde", usage="[Alliance/Horde]")
async def set_faction(ctx, faction):
    if setFaction(faction):
        response = "Faction setup successful: " + slugifyName(faction)
        global factionSet
        factionSet = True
    else:
        response = "Error: Invalid faction name: " + slugifyName(faction)
    await ctx.send(response)

@bot.command(name='list_servers',  brief='Show available servers', usage="EU/US")
async def list_servers(ctx, *args):
    arg = ' '.join(args)
    servers = getServers(arg)
    if len(args) > 0:
        response = "Available servers in " + arg.upper() + ":\n"
    else:
        response = "Available servers:\n"
    for server in servers:
        response += server + "\n"
    await ctx.send(response)

@bot.command(name='price', brief='AH price lookup')
async def price(ctx, *arg):
    itemName = ' '.join(arg)
    if not (serverSet and factionSet):
        response = "Must setup both server and faction first!"
    else:
        price = getPrice(itemName)
        response = itemName + " - " + price
    await ctx.send(response)

@bot.command(name='craftprice', help='Craft price lookup')
async def craftprice(ctx, arg):
    if not isSetup():
        response = "Error: Need to setup server/faction first. See !help setup"
    else:
        response = "Craft price lookup"
    await ctx.send(response)

@bot.command(name='enchantprice', help='Enchant price lookup')
async def enchantprice(ctx, arg):
    if not isSetup():
        response = "Error: Need to setup server/faction first. See !help setup"
    else:
        response = "Enchant price loopup"
    await ctx.send(response)

@bot.command(name='version', help='Show bot version')
async def version(ctx):
    response = "Running version: " + VERSION
    await ctx.send(response)

bot.run(TOKEN)
