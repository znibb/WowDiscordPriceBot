import os
from discord.ext import commands
from dotenv import load_dotenv
from functions import *

# Variables
server = ""

# Load Discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Command prefix
bot = commands.Bot(command_prefix='!')

# Bot joins
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
'''
# Command error
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'Invalid command. Try !help')
'''
# Bot commands
@bot.command(name='setup', help='Setup server/faction')
async def price(ctx, arg):
    response = "Price lookup"
    await ctx.send(response)

@bot.command(name='price', help='Simple item price lookup')
async def price(ctx, *arg):
    name = "{}".format(' '.join(arg))
    #response = str(getItemID(arg))
    response = "testing one two"
    await ctx.send(response)

@bot.command(name='craftprice', help='Craft price lookup')
async def craftprice(ctx, arg):
    response = "Craft price lookup"
    await ctx.send(response)

@bot.command(name='enchantprice', help='Enchant price lookup')
async def enchantprice(ctx, arg):
    response = "Enchant price loopup"
    await ctx.send(response)

bot.run(TOKEN)
