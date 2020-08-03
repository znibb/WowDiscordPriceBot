#!/usr/bin/env python3

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
    elif isinstance(error, commands.CommandNotFound):
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

@bot.command(name='price', brief='AH price lookup', usage="<item name>")
async def price(ctx, *arg):
    itemName = slugifyName(' '.join(arg))
    if serverSet and not factionSet:
        response = "Missing: Faction. See `!help set_faction`."
    elif not serverSet and factionSet:
        response = "Missing: Server. See `!help set_server`."
    elif not serverSet and not factionSet:
        response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
    else:
        price = getPrice(itemName)
        if price == 0:
            response = "No match: " + itemName
        else:
            response =  "Price for: " + itemName + "\n"
            response += convertMoney(price)
    await ctx.send(response)

@bot.command(name='craftprice', brief='Craft price lookup', usage="<item name>")
async def craftprice(ctx, *arg):
    itemName = slugifyName(' '.join(arg))
    if serverSet and not factionSet:
        response = "Missing: Faction. See `!help set_faction`."
    elif not serverSet and factionSet:
        response = "Missing: Server. See `!help set_server`."
    elif not serverSet and not factionSet:
        response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
    else:
        [amountCrafted, reagents] = getCraftInfo(itemName)
        if amountCrafted == 0:
            response = "No match: " + itemName
        else:
            response =  "Craft price for: " + itemName + "\n"
            response += "Reagents:\n"
            totalCraftPrice = 0
            for reagent in reagents:
                if reagent["vendorPrice"] == None:
                    price = reagent["marketValue"]
                else:
                    price = reagent["vendorPrice"]
                totalCraftPrice += price
                response += "\t" + reagent["name"] + " x" + str(reagent["amount"]) + " á " + convertMoney(price) + "\n"
            response += "Total craft price: " + convertMoney(totalCraftPrice) + "\n"

            ahPrice = getPrice(itemName)
            if ahPrice == 0:
                response += "AH price unavailable"
            else:
                response += "AH price: " + convertMoney(ahPrice) + "\n"
                if ahPrice > totalCraftPrice:
                    response += "Craft profit: " + convertMoney(ahPrice-totalCraftPrice)
                else:
                    response += "Craft loss: " + convertMoney(totalCraftPrice-ahPrice)
    await ctx.send(response)

@bot.command(name='enchantprice', brief='Enchant price lookup', help="Enchant price lookup\nValid slot names:\nBoots\nBracers\nChest\nCloak\nGloves\nShield\nWeapon\n2H Weapon", usage="<slot> <enchant name>")
async def enchantprice(ctx, *arg):
    itemName = ' '.join(arg).title()
    if serverSet and not factionSet:
        response = "Missing: Faction. See `!help set_faction`."
    elif not serverSet and factionSet:
        response = "Missing: Server. See `!help set_server`."
    elif not serverSet and not factionSet:
        response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
    else:
        reagents = getEnchantReagents(itemName)

        if reagents == 0:
            response = "No match: " + itemName
        else:
            totalPrice = 0
            reagentMissing = False
            reagentPrices = dict()
            for reagent, amount in reagents.items():
                price = getPrice(slugifyName(reagent))
                if price == 0:
                    reagentMissing = True
                reagentPrices[reagent] = price
                totalPrice += price*amount
            
            if reagentMissing:
                response = "Missing: At least one reagent price."
            else:
                response =  "Enchant price for: " + itemName + "\n"
                response += "Reagents:\n"
                for reagent, amount in reagents.items():
                    response += "\t" + reagent + " x" + str(amount) + " á " + convertMoney(reagentPrices[reagent]) + "\n"
                response += "Total enchant price: " + convertMoney(totalPrice)
    await ctx.send(response)

@bot.command(name='version', help='Show bot version')
async def version(ctx):
    response = "Running version: " + VERSION
    await ctx.send(response)

bot.run(TOKEN)
