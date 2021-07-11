import discord
import inspect
import json
import math
import os
import requests
from discord.ext import commands

# Dictionary of help decriptions
helpDesc = {
	"price": "AH price lookup",
	"craftprice": "Craft price lookup",
	"enchantprice": "Enchant price lookup\nValid slot names:\nBoots\nBracers\nChest\nCloak\nGloves\nShield\nWeapon\n2H Weapon",
	"craftwrit": "Craftman's Writ lookup\nOptionally add name of a writ item to get a detailed breakdown",
	"shoppinglist": "Shopping list breakdown\nDisplays the total amount of mats required to craft a certain number of an indicated item"

}

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

	def craftBreakdown(self, reagentList):
		# Setup return dict
		returnDict = dict()

		for reagent in reagentList:
			# Try to fetch craft info
			[amountCrafted, subReagentList] = self.getCraftInfo(reagent["name"])

			# If the item in question isn't craftable
			if amountCrafted == 0:
				returnDict[reagent["name"]] = dict()
				returnDict[reagent["name"]]["amount"] = reagent["amount"]
				if reagent["vendorPrice"] is None:
					returnDict[reagent["name"]]["unitPrice"] = reagent["marketValue"]
				else:
					returnDict[reagent["name"]]["unitPrice"] = reagent["vendorPrice"]
			# If it is craftable break it down further
			else:
				# Recursively call function
				recurseDict = self.craftBreakdown(subReagentList)

				# Add results to returnDict
				for key in recurseDict.keys():
					if key in returnDict:
						returnDict[key]["amount"] += recurseDict[key]["amount"]*reagent["amount"]/amountCrafted
					else:
						returnDict[key] = dict()
						returnDict[key]["amount"] = recurseDict[key]["amount"]*reagent["amount"]/amountCrafted
						returnDict[key]["unitPrice"] = recurseDict[key]["unitPrice"]

		return returnDict

	def getCraftInfo(self, itemName):
		setup = self.bot.get_cog('Setup')
		itemUrl = setup.getBaseUrl() + "crafting/" + setup.getConfiguredServer() + "-" + setup.getConfiguredFaction() + "/" + setup.slugifyName(itemName)
		response = requests.get(itemUrl)
		responseJson = response.json()

		if "error" in responseJson:
			return [0, dict()]
		elif "createdBy" not in responseJson:
			return [0, dict()]
		elif responseJson["createdBy"] == []:
			return [0, dict()]

		amountCraftedMin    = responseJson["createdBy"][0]["amount"][0]
		amountCraftedMax    = responseJson["createdBy"][0]["amount"][1]

		# Assumes the mean amount is always an integer
		amountCrafted       = int((amountCraftedMin+amountCraftedMax)/2)

		reagentList = responseJson["createdBy"][0]["reagents"]

		return [amountCrafted, reagentList]

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

		return responseJson["stats"]["current"]["marketValue"]

	# Bot commands
	@commands.command(name="price", brief="AH price lookup", help=helpDesc["price"], usage="<item name>", aliases=["p"])
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

	@commands.command(name="craftprice", brief="Craft price lookup", help=helpDesc["craftprice"], usage="<item name>", aliases=["cp"])
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

	@commands.command(name="enchantprice", brief="Enchant price lookup", help=helpDesc["enchantprice"], usage="<slot> <enchant name>", aliases=["ep"])
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

	@commands.command(name="craftwrit", brief="Craftman\'s Writ lookup", help=helpDesc["craftwrit"], usage="(writ item)", aliases=["cw"])
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

					# Item price, will only be single type of item since no breakdown
					reagentPrice = self.getPrice(itemNameSlug)
					amount = writList[writFullName]["Amount"]

					# Generate output
					response = "Price for Craftman\'s Writ - " + writFullName + ":\n"
					response += "Writ price: " + self.convertMoney(writItemPrice) + "\n"
					response += str(amount) + " x " + itemNameSlug + " á " + self.convertMoney(reagentPrice) + "\n"
					response += "Total: " + self.convertMoney(writItemPrice + amount*reagentPrice)

			# If no argument was given, show overall info
			else:
				# Create writ-price dict
				writPrices = dict()
				for item, info in writList.items():
					unitPrice = self.getPrice(str(info["ID"]))
					writPrice = self.getPrice(str(info["Writ"]))

					# Skip writs with indeterminable price
					if unitPrice == 0:
						writSkipped = True
					else:
						amount = info["Amount"]
						writPrices[item] = unitPrice*amount + writPrice

				# Results header
				response = "Prices for Craftman\'s Writs:"
				
				if writSkipped:
					response += "\n**List is incomplete due to missing price info**"

				# Sort and print dict
				for writ in sorted(writPrices, key=writPrices.get, reverse=False):
					response += "\n" + writ + ": " + self.convertMoney(writPrices[writ])

		await ctx.send(response)

	@commands.command(name="shoppinglist", brief="Shopping list breakdown", help=helpDesc["shoppinglist"], usage="<amount> <item name>", aliases=["sl"])
	async def shoppinglist(self, ctx, *arg):
		# Pass access to setup methods
		setup = self.bot.get_cog('Setup')

		# Check for valid server+faction setup and input arguments
		configuredFaction = setup.getConfiguredFaction()
		configuredServer = setup.getConfiguredServer()
		if configuredFaction == "" and configuredServer != "":
			response = "Missing: Faction. See `-help set_faction`."
		elif configuredFaction != "" and configuredServer == "":
			response = "Missing: Server. See `-help set_server`."
		elif configuredFaction == "" and configuredServer == "":
			response = "Missing: Server and Faction. See `-help set_server` and `-help set_faction` "
		elif len(arg) < 2 or arg[0].isdigit() == False:
			response = "Incorrect input: " + ' '.join(arg).title()
		
		# Function body
		else:
			# Fetch command arguments
			amountToCraft = int(arg[0])
			itemName = ' '.join(arg[1:]).title()

			# Check if indicated item is craftable
			[amountCrafted, reagentList] = self.getCraftInfo(itemName)

			if amountCrafted == 0:
				response = "Item not craftable: " + itemName
			else:
				# Breakdown of mats for 1 craft
				reagentBreakdownDict = self.craftBreakdown(reagentList)

				# Determine how many crafts is needed
				amountMultiplier = math.ceil(amountToCraft/amountCrafted)
		
				# Create chat output
				totalPrice = 0
				response = "Shopping list for " + str(amountCrafted*amountMultiplier) + "x " + itemName + ":\n"

				for item, info in reagentBreakdownDict.items():
					response += str(math.ceil(info["amount"]*amountMultiplier)) + "x " + item + " á " + self.convertMoney(info["unitPrice"]) + "\n"
					totalPrice += info["unitPrice"]*info["amount"]*amountMultiplier
				
				response += "Total price: " + self.convertMoney(totalPrice)

		await ctx.send(response)

def setup(bot):
	bot.add_cog(Usage(bot))
