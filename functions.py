import math
import requests

baseUrl = "https://api.nexushub.co/wow-classic/v1/"
serverListUrl = baseUrl + "servers/full"

configuredServer = ""
configuredFaction = ""

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

def getCraftInfo(itemName):
    itemUrl = baseUrl + "crafting/" + configuredServer + "-" + configuredFaction + "/" + slugifyName(itemName)
    response = requests.get(itemUrl)
    responseJson = response.json()

    if "error" in  responseJson:
        return 0
    
    amountCraftedMin    = responseJson["createdBy"][0]["amount"][0]
    amountCraftedMax    = responseJson["createdBy"][0]["amount"][1]
    amountCrafted       = round((amountCraftedMin+amountCraftedMax)/2, 2)

    reagents = responseJson["createdBy"][0]["reagents"]

    return [amountCrafted, reagents]

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
    itemUrl = baseUrl + "items/" + configuredServer + "-" + configuredFaction + "/" + itemName
    response = requests.get(itemUrl)
    responseJson = response.json()

    if "stats" not in responseJson:
        return 0

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