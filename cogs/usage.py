import discord
import inspect
import json
import math
import os
import requests
from discord.ext import commands

class Usage(commands.Cog):

	# Constructor
	def __init__(self, bot):
		self.bot = bot

	# Support methods
	@staticmethod
	def convertMoney(copperAmount):
		gold =      math.floor(copperAmount/10000)
		silver =    math.floor(copperAmount%10000/100)
		copper =    copperAmount%100

		result = ""
		if not gold:
			if not silver:
				result = "{}c".format(copper)
			else:
				result = "{}s{:02}c".format(silver, copper)
		else:
			result = "{}g{:02}s{:02}c".format(gold, silver, copper)

		return result

	def getCraftInfo(self, itemName):
		setup = self.bot.get_cog('Setup')
		itemUrl = setup.getBaseUrl() + "crafting/" + setup.getConfiguredServer() + "-" + setup.getConfiguredFaction() + "/" + setup.slugifyName(itemName)
		response = requests.get(itemUrl)
		responseJson = response.json()

		if "error" in  responseJson:
			return [0, dict()]

		amountCraftedMin    = responseJson["createdBy"][0]["amount"][0]
		amountCraftedMax    = responseJson["createdBy"][0]["amount"][1]
		amountCrafted       = round((amountCraftedMin+amountCraftedMax)/2, 2)

		reagents = responseJson["createdBy"][0]["reagents"]

		return [amountCrafted, reagents]

	@staticmethod
	def getEnchantReagents(enchantName):
		currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
		parentdir = os.path.dirname(currentdir)
		with open("" + parentdir + "/data/enchanting.json", 'r') as f:
			formulas = json.load(f)

		if enchantName in formulas:
			return formulas[enchantName]["Reagents"]
		else:
			return 0

	def getPrice(self, itemName):
		setup = self.bot.get_cog('Setup')
		itemUrl = setup.getBaseUrl() + "items/" + setup.getConfiguredServer() + "-" + setup.getConfiguredFaction() + "/" + itemName
		response = requests.get(itemUrl)
		responseJson = response.json()

		if "stats" not in responseJson:
			return 0

		return responseJson["stats"]["current"]["minBuyout"]

	# Bot commands
	@commands.command(name='price', brief='AH price lookup', usage="<item name>", aliases=['p'])
	async def price(self, ctx, *arg):
		setup = self.bot.get_cog('Setup')
		itemName = setup.slugifyName(' '.join(arg))

		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `!help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `!help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
		else:
			price = self.getPrice(itemName)
			if price == 0:
				response = "No match: " + itemName
			else:
				response =  "Price for: " + itemName + "\n"
				response += self.convertMoney(price)
		await ctx.send(response)

	@commands.command(name='craftprice', brief='Craft price lookup', usage="<item name>", aliases=['cp'])
	async def craftprice(self, ctx, *arg):
		setup = self.bot.get_cog('Setup')
		itemName = setup.slugifyName(' '.join(arg))

		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `!help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `!help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
		else:
			[amountCrafted, reagents] = self.getCraftInfo(itemName)
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
					totalCraftPrice += reagent["amount"]*price
					response += "\t" + reagent["name"] + " x" + str(reagent["amount"]) + " á " + self.convertMoney(price) + "\n"
				response += "Total craft price: " + self.convertMoney(totalCraftPrice) + "\n"

				ahPrice = self.getPrice(itemName)
				if ahPrice == 0:
					response += "AH price unavailable"
				else:
					response += "AH price: " + self.convertMoney(ahPrice) + "\n"
					if ahPrice > totalCraftPrice:
						response += "Craft profit: " + self.convertMoney(ahPrice-totalCraftPrice)
					else:
						response += "Craft loss: " + self.convertMoney(totalCraftPrice-ahPrice)
		await ctx.send(response)

	@commands.command(name='enchantprice', brief='Enchant price lookup', help="Enchant price lookup\nValid slot names:\nBoots\nBracers\nChest\nCloak\nGloves\nShield\nWeapon\n2H Weapon", usage="<slot> <enchant name>", aliases=['ep'])
	async def enchantprice(self, ctx, *arg):
		setup = self.bot.get_cog('Setup')
		itemName = ' '.join(arg).title()

		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `!help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `!help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
		else:
			reagents = self.getEnchantReagents(itemName)

			if reagents == 0:
				response = "No match: " + itemName
			else:
				totalPrice = 0
				reagentMissing = False
				reagentPrices = dict()
				for reagent, amount in reagents.items():
					price = self.getPrice(setup.slugifyName(reagent))
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
						response += "\t" + reagent + " x" + str(amount) + " á " + self.convertMoney(reagentPrices[reagent]) + "\n"
					response += "Total enchant price: " + self.convertMoney(totalPrice)
		await ctx.send(response)

def setup(bot):
	bot.add_cog(Usage(bot))
