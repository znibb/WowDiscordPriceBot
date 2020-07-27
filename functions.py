import json
import requests

baseUrl = "https://api.nexushub.co/wow-classic/v1/items/"

def getItemID(name):
    with open("data/itemID.json", 'r') as f:
        itemIDs = json.load(f)

    return itemID[name]
