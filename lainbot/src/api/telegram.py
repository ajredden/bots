# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import json, requests, time

def get_consts(token_path):
	raw = json.load(open(token_path, "rb"))
	API_KEY = raw["tokens"]["telegram"]["http_api_key"]
	
	return f"https://api.telegram.org/bot{API_KEY}/sendPhoto"

def post(frame, msg, token_path):
	IMG_SEND_ENDPOINT = get_consts(token_path)
	print(IMG_SEND_ENDPOINT)
	
	params = {
		"chat_id" : "@LainBot13",
		"caption" : msg
	}
	
	files = {
		"photo" : open(frame, "rb")
	}

	try:
		r = requests.post(IMG_SEND_ENDPOINT, files=files, data=params)
		print(f"\t[{time.strftime('%d/%m/%y %H:%M:%S')}] OK? {json.dumps(r.json()['ok'], sort_keys=True, indent=8)}\n")
	except requests.ConnectionError as e:
		print("Error! Connection failed!")
		sys.exit(2)