import requests

serverListUrl = "https://api.nexushub.co/wow-classic/v1/servers/full"
itemUrlBase = "https://api.nexushub.co/wow-classic/v1/items/"

configuredServer = ""
configuredFaction = ""

def getServers(region):
    response = requests.get(serverListUrl)
    responseJson = response.json()

    serverSet = set()
    for server in responseJson:
        if not region == "":
            if server["region"] == region.upper():
                serverSet.add(server["name"])
        else:
            serverSet.add(server["name"])

    return sorted(serverSet)

def getPrice(itemName):
    itemUrl = itemUrlBase + configuredServer + "-" + configuredFaction
    response = requests.get(itemUrl)
    responseJson = response.json()

    return responseJson["stats"]["current"]["minBuyout"]

def setServer(serverName):
    serverName = slugifyName(serverName)

    response = requests.get(serverListUrl)
    responseJson = response.json()
    serverSet = set()
    for server in  responseJson:
        serverSet.add(server["slug"])

    if serverName in serverSet:
        global configuredServer
        configuredServer = serverName
        return True
    else:
        return False

def setFaction(factionName):
    factionName = slugifyName(factionName)

    if factionName in ["alliance", "horde"]:
        global configuredFaction
        configuredFaction = factionName
        return True
    else:
        return False

def slugifyName(name):
    # Replace spaces with dashes, remove apostrophes and ensure lower case
    return name.replace(" ", "-").replace("'", "").lower()