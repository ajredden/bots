# rate limits: 300 tweets per 3 hours (100/hr), 1000 tweets per 24 hours

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import json, os.path, requests, sys, time, msvcrt
from requests_oauthlib import OAuth1

def get_consts(token_path):
	TOKENS = json.load(open(token_path, "rb"))

	KEYS = {
		"api_key"             : TOKENS["tokens"]["twitter"]["api_key"],
		"api_secret"          : TOKENS["tokens"]["twitter"]["api_secret"],
		"access_token"        : TOKENS["tokens"]["twitter"]["access_token"],
		"access_token_secret" : TOKENS["tokens"]["twitter"]["access_token_secret"]
	}

	OAUTH = OAuth1(KEYS["api_key"], client_secret=KEYS["api_secret"], resource_owner_key=KEYS["access_token"], \
	        resource_owner_secret=KEYS["access_token_secret"])
	
	return {
		"UPLOAD_ENDPOINT" : "https://upload.twitter.com/1.1/media/upload.json", # returns media_id which can be used with the tweet endpoint
		"TWEET_ENDPOINT"  : "https://api.twitter.com/1.1/statuses/update.json",
		"OAUTH"           : OAUTH
	}


def post(frame_dir, frame, msg, token_path, n=1):
	consts = get_consts(token_path)
	
	def INIT(frame_dir, frame):
		params = {
			"command"     : "INIT",
			"media_type"  : "image/jpg",
			"total_bytes" : os.path.getsize(f"{frame_dir}\\{frame}")
		}
		
		try:
			r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"])
			return r.json()["media_id"]
		except requests.exceptions.ConnectionError as e:
			print(f"Connection Error! Could not upload frame {frame_dir}\\{frame} to Twitter!")
			print("Failed at INIT stage.")
			with open(".continue_from", "a") as f: f.write(f"\ntwitter|{frame_dir}\\{frame}")
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

	def APPEND(frame_dir, frame, id):
		segment_id = 0
		bytes_sent = 0
		
		with open(f"{frame_dir}\\{frame}", "rb") as f:	
			while bytes_sent < os.path.getsize(f"{frame_dir}\\{frame}"):
				chunk = f.read(4*1024*1024)

				params = {
							"command"       : "APPEND",
							"media_id"      : id,
							"segment_index" : segment_id
						}
				
				files = {
							"media" : chunk
						}
				
				try:
					r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, files=files, auth=consts["OAUTH"])
				except requests.exceptions.ConnectionError as e:
					print(f"Connection Error! Could not upload frame {frame_dir}\\{frame} to Twitter!")
					print("Failed at APPEND stage.")
					with open(".continue_from", "a") as f: f.write(f"\ntwitter|{frame_dir}\\{frame}")
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
				else:
					segment_id += 1
					bytes_sent = f.tell()

	def FINALIZE(id):
		params = {
			"command"  : "FINALIZE",
			"media_id" : id
		}
		
		try:
			r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"])
		except requests.exceptions.ConnectionError as e:
			print(f"Connection Error! Could not upload frame {frame_dir}\\{frame} to Twitter!")
			print("Failed at FINALIZE stage.")
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
	
	def tweet(media_id, msg):
		params = {
			"media_ids" : media_id,
			"status"    : msg
		}
		
		queue = []
		
		try:
			r = requests.post(consts["TWEET_ENDPOINT"], data=params, auth=consts["OAUTH"])
			print(f"\t[{time.strftime('%d/%m/%y %H:%M:%S')}] created_at {json.dumps(r.json()['created_at'], sort_keys=True, indent=4)} / id {json.dumps(r.json()['id'], sort_keys=True, indent=8)}\n")
		except requests.exceptions.ConnectionError as e:
			print(f"Connection Error! Could not upload frame {frame_dir}\\{frame} to Twitter!")
			print("Failed at tweeting stage.")
			with open(".continue_from", "a") as f: f.write(f"\ntwitter|{frame_dir}\\{frame}")
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
			
	id = INIT(frame_dir, frame)
	APPEND(frame_dir, frame, id)
	FINALIZE(id)
	tweet(id, msg)