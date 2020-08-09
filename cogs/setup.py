import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv

class Setup(commands.Cog):
	load_dotenv()
	baseUrl = os.getenv('BASEURL')
	serverListUrl = baseUrl + "servers/full"
	
	configuredFaction = ""
	configuredServer = ""

	# Constructor
	def __init__(self, bot):
		self.bot = bot

	# Support methods
	def getConfiguredFaction(self):
		return self.configuredFaction

	def getConfiguredServer(self):
		return self.configuredServer

	@staticmethod
	def getServers(region, url):
		response = requests.get(url)
		responseJson = response.json()

		availableServers = set()
		for server in responseJson:
			if not region == "":
				if server["region"] == region.upper():
					availableServers.add(server["name"])
			else:
				availableServers.add(server["name"])

		return sorted(availableServers)

	def setFaction(self, factionName):
		factionName = self.slugifyName(factionName)

		if factionName in ["alliance", "horde"]:
			self.configuredFaction = factionName
			return True
		else:
			return False

	def setServer(self, serverName):
		serverName = self.slugifyName(serverName)

		response = requests.get(self.serverListUrl)
		responseJson = response.json()
		availableServers = set()
		for server in responseJson:
			availableServers.add(server["slug"])

		if serverName in availableServers:
			self.configuredServer = serverName
			return True
		else:
			return False

	@staticmethod
	def slugifyName(name):
		# Replace spaces with dashes, remove apostrophes and ensure lower case
		return name.replace(" ", "-").replace("'", "").lower()

	# Bot commands
	@commands.command(name='list_servers', brief='List available servers', usage='[EU|US]')
	async def list_servers(self, ctx, *args):
		region = ' '.join(args)
		servers = self.getServers(region, self.serverListUrl)
		if len(args) > 0:
			response = "Available servers in " + region.upper() + ":\n"
		else:
			response = "Available servers:\n"
		for server in servers:
			response += server + "\n"
		await ctx.send(response)

	@commands.command(name='set_faction', brief='Set faction', usage='[horde|alliance]')
	async def set_faction(self, ctx, faction):
		if self.setFaction(faction):
			response = "Faction setup successful: " + self.slugifyName(faction)
		else:
			response = "Error: Invalid faction name: " + self.slugifyName(faction)
		await ctx.send(response)

	@commands.command(name='set_server',  brief='Set server', usage='<server>')
	async def set_server(self, ctx, *arg):
		serverName = ' '.join(arg)
		if self.setServer(serverName):
			response = "Server setup successful: " + self.slugifyName(serverName)
		else:
			response = "Error: Invalid server name: " + self.slugifyName(serverName)
		await ctx.send(response)

	@commands.command(name='version', brief='Show running version')
	async def version(self, ctx):
		response = "Running version: " + str(os.getenv('VERSION'))
		await ctx.send(response)

def setup(bot):
	bot.add_cog(Setup(bot))