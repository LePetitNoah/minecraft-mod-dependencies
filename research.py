from dotenv import dotenv_values
import requests

BASE_URL = "https://api.curseforge.com"
MOD_URL = BASE_URL + "/v1/mods/search"

MINECRAFT_GAME_ID = 432
MOD_NAME = "Tom's Simple Storage"
GAME_VERSION = "1.21.1"
MOD_LOADER = 6  # NeoForge

env = dotenv_values(".env")

headers = {
    "Accept": "application/json",
    "x-api-key": env.get("API_KEY"),
}

params = {
    "gameId": MINECRAFT_GAME_ID,
    "searchFilter": MOD_NAME,
    "index": 0
}

response = requests.get(MOD_URL, headers=headers, params=params)
data = response.json()

for mod in data.get("data", []):
    printable = False
    
    for idx in mod.get("latestFilesIndexes", []):
        if idx.get("gameVersion") == GAME_VERSION and idx.get("modLoader") == MOD_LOADER:
            printable = True

    if printable:
        infos = {
            "id": mod.get("id"),
            "name": mod.get("name"),
            "slug": mod.get("slug"),
            "summary": mod.get("summary"),
        }
        print(infos)
        print("------------------------------------------------------------------------")