import discord
import requests
from discord.ext import commands

version="2.0.2"

class Setup(commands.Cog):
	baseUrl="https://api.nexushub.co/wow-classic/v1/"
	serverListUrl = baseUrl + "servers/full"

	# Variables
	configuredFaction = ""
	configuredServer = ""

	# Constructor
	def __init__(self, bot):
		self.bot = bot
		self.version = version

	# Support methods
	def getBaseUrl(self):
		return self.baseUrl

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
		# Replace spaces with dashes
		name = name.replace(" ", "-")
		# Remove apostrophes
		name = name.replace("'", "")
		# Remove colons
		name = name.replace(":", "")
		# Remove brackets
		name = name.replace("[", "")
		name = name.replace("]", "")
		# Force lower case
		name = name.lower()

		return name

	# Bot commands
	@commands.command(name='list_servers', brief='List available servers', usage='[EU|US]', aliases=["ls"])
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

	@commands.command(name='set_faction', brief='Set faction', usage='[horde|alliance]', aliases=["sf"])
	async def set_faction(self, ctx, faction):
		if self.setFaction(faction):
			response = "Faction setup successful: " + self.slugifyName(faction)
		else:
			response = "Error: Invalid faction name: " + self.slugifyName(faction)
		await ctx.send(response)

	@commands.command(name='set_server',  brief='Set server', usage='<server>', aliases=["ss"])
	async def set_server(self, ctx, *arg):
		serverName = ' '.join(arg)
		if self.setServer(serverName):
			response = "Server setup successful: " + self.slugifyName(serverName)
		else:
			response = "Error: Invalid server name: " + self.slugifyName(serverName)
		await ctx.send(response)

	@commands.command(name='version', brief='Show running version', aliases=["v"])
	async def version(self, ctx):
		response = "Running version: " + str(self.version)
		await ctx.send(response)

def setup(bot):
	bot.add_cog(Setup(bot))
