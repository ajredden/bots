# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import json, requests, time, sys, msvcrt

def get_consts(token_path):
	raw = json.load(open(token_path, "rb"))
	API_KEY = raw["tokens"]["telegram"]["http_api_key"]
	
	return f"https://api.telegram.org/bot{API_KEY}/sendPhoto"

def post(frame_dir, frame, msg, token_path, n=1):
	IMG_SEND_ENDPOINT = get_consts(token_path)
	print(IMG_SEND_ENDPOINT)
	
	params = {
		"chat_id" : "@LainBot13",
		"caption" : msg
	}
	
	files = {
		"photo" : open(f"{frame_dir}\\{frame}", "rb")
	}

	queue = []
	
	try:
		r = requests.post(IMG_SEND_ENDPOINT, files=files, data=params)
		print(f"\t[{time.strftime('%d/%m/%y %H:%M:%S')}] OK? {json.dumps(r.json()['ok'], sort_keys=True, indent=8)}\n")
	except requests.exceptions.ConnectionError as e:	
		print(f"Connection Error! Could not upload frame {frame_dir}\\{frame} to Telegram!")
		with open(".continue_from", "a") as f: f.write(f"\ntelegram|{frame_dir}\\{frame}")
		print(f"Trying again in {n} seconds. (Press any button to try again now.)", end="", flush=True)
		for s in range(n, 0, -1):
			countdown = f"Trying again in {s} seconds. (Press any button to try again now.)"
			print("\b" * len(countdown), end="", flush=True)
			print(countdown, end="", flush=True)
			if msvcrt.kbhit():
				msvcrt.getch()
				break
			time.sleep(1)
		print()
		post(frame_dir, frame, msg, token_path, n=n*2)