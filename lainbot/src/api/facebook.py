# rate limits: 4800 * engagements per hour (DON'T BE LAZY. ACCOUNT FOR THIS)
# percentage used of allocated quota per hour may be in a header X-App-Usage if I use enough; check that

import requests, sys, json

sys.path.append("..")

import common.common

raw = json.load(open("tokens.json", "rb"))

ACCESS_TOKEN = raw["tokens"]["facebook"]["page"]["token"]

IMG_POST_ENDPOINT = (f"https://graph.facebook.com/v10.0/me/photos?access_token={ACCESS_TOKEN}")

r = requests.post(f"{IMG_POST_ENDPOINT}", files = {"file" : open("..\\testing\\test.png", "rb")})
print(r.json())