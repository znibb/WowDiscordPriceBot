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

		if "error" in responseJson:
			return [0, dict()]
		elif "createdBy" not in responseJson:
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
		elif responseJson["stats"]["current"] is None:
			return 0

		return responseJson["stats"]["current"]["minBuyout"]

	# Bot commands
	@commands.command(name="price", brief="AH price lookup", usage="<item name>", aliases=["p"])
	async def price(self, ctx, *arg):
		# Pass access to setup methods
		setup = self.bot.get_cog('Setup')

		# Fetch command arguments
		itemName = setup.slugifyName(' '.join(arg))

		# Check for valid server+faction setup
		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `!help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `!help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
		
		# Function body
		else:
			price = self.getPrice(itemName)
			if price == 0:
				response = "No match: " + itemName
			else:
				response =  "Price for: " + itemName + "\n"
				response += self.convertMoney(price)
		await ctx.send(response)

	@commands.command(name="craftprice", brief="Craft price lookup", usage="<item name>", aliases=["cp"])
	async def craftprice(self, ctx, *arg):
		# Pass access to setup methods
		setup = self.bot.get_cog('Setup')

		# Fetch command arguments
		itemName = setup.slugifyName(' '.join(arg))

		# Check for valid server+faction setup
		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `!help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `!help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `!help set_server` and `!help set_faction` "
		
		# Function body
		else:
			[amountCrafted, reagents] = self.getCraftInfo(itemName)
			if amountCrafted == 0:
				response = "No match: " + itemName
			else:
				# If amountCrafted is X.0 cast to int
				if amountCrafted%1 == 0.0:
					amountCrafted = int(amountCrafted)
				# Else round to 1 decimal place
				else:
					amountCrafted = round(amountCrafted, 1)

				response =  "Craft price for: " + str(amountCrafted) + "x " + itemName + "\n"
				response += "Reagents:\n"
				totalCraftPrice = 0
				for reagent in reagents:
					if reagent["vendorPrice"] == None:
						price = reagent["marketValue"]
					else:
						price = reagent["vendorPrice"]
					totalCraftPrice += reagent["amount"]*price
					response += "\t" + reagent["name"] + " x" + str(reagent["amount"]) + " á " + self.convertMoney(price) + "\n"
				pricePerItem = round(totalCraftPrice/amountCrafted)
				response += "Total craft price: " + self.convertMoney(pricePerItem)
				if amountCrafted > 1:
					response += " (per item)"
				response += "\n"

				ahPrice = self.getPrice(itemName)
				if ahPrice == 0:
					response += "AH price unavailable"
				else:
					response += "AH price: " + self.convertMoney(ahPrice) + "\n"
					if ahPrice > pricePerItem:
						response += "Craft profit: " + self.convertMoney(ahPrice-pricePerItem)
					else:
						response += "Craft loss: " + self.convertMoney(pricePerItem-ahPrice)
		await ctx.send(response)

	@commands.command(name="enchantprice", brief="Enchant price lookup", help="Enchant price lookup\nValid slot names:\nBoots\nBracers\nChest\nCloak\nGloves\nShield\nWeapon\n2H Weapon", usage="<slot> <enchant name>", aliases=["ep"])
	async def enchantprice(self, ctx, *arg):
		# Pass access to setup methods
		setup = self.bot.get_cog('Setup')

		# Fetch command arguments
		itemName = ' '.join(arg).title()

		# Check for valid server+faction setup
		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `-help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `-help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `-help set_server` and `-help set_faction` "
		
		# Function body
		else:
			reagents = self.getEnchantReagents(itemName)

			if reagents == 0:
				response = "No match: " + itemName + ". Try -help enchantprice if you're unsure what went wrong."
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

	@commands.command(name='craftwrit', brief='Craftman\'s Writ lookup', help="Craftman\'s Writ lookup", usage="TBD", aliases=["cw"])
	async def craftwrit(self, ctx, *arg):
		# Pass access to setup methods
		setup = self.bot.get_cog('Setup')

		# Fetch command arguments
		itemName = ' '.join(arg).title()

		# Check for valid server+faction setup
		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `-help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `-help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `-help set_server` and `-help set_faction` "
		
		# Function body
		else:
			currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
			parentdir = os.path.dirname(currentdir)
			with open("" + parentdir + "/data/craftmansWrit.json", 'r') as f:
				writList = json.load(f)

			# If user supplied a specific writ as argument, show detailed breakdown of said writ
			if itemName != "":
				# Check that a valid writ was supplied
				itemNameSlug = setup.slugifyName(itemName)
				validWrit = False
				for writ in writList.keys():
					if itemNameSlug == setup.slugifyName(writ):
						validWrit = True
						writFullName = writ
				
				if validWrit == False:
					response = "Invalid writ: " + itemName
				else:
					# Price for the writ item itself
					writItemPrice = self.getPrice(str(writList[writFullName]["Writ"]))

					# Breakdown compound material list
					

					response = "Price for Craftman\'s Writ - " + writFullName + ":\n"
					response += "Writ price: " + self.convertMoney(writItemPrice) + "\n"

			# If no argument was given, show overall info
			else:
				# Create writ-price dict
				writPrices = dict()
				for item, info in writList.items():
					unitPrice = self.getPrice(str(info["ID"]))

					# Skip writs with indeterminable price
					if unitPrice == 0:
						writSkipped = True
					else:
						amount = info["Amount"]
						writPrices[item] = unitPrice*amount

				# Results header
				response = "Prices for Craftman\'s Writs:"
				
				if writSkipped:
					response += "\n**List is incomplete due to missing price info**"

				# Sort and print dict
				for writ in sorted(writPrices, key=writPrices.get, reverse=False):
					response += "\n" + writ + ": " + self.convertMoney(writPrices[writ])

		await ctx.send(response)

def setup(bot):
	bot.add_cog(Usage(bot))
