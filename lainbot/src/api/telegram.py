import requests, sys, json

sys.path.append("..")

import common.common

raw = json.load(open("tokens.json", "rb"))

API_KEY = raw["tokens"]["telegram"]["http_api_key"]
IMG_SEND_ENDPOINT = f"https://api.telegram.org/bot{API_KEY}/sendPhoto"

params = {
	"chat_id" : "@LainBot13",
	"caption" : "Close the world, ƚxɘᴎ ɘʜƚ ᴎɘqO"
}

r = requests.post(url=f"{IMG_SEND_ENDPOINT}", files={"photo" : open(r"..\testing\test.png", "rb")}, data=params)
print(r.json())