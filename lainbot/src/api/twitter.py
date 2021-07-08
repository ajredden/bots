# rate limits: 300 tweets per 3 hours (100/hr), 1000 tweets per 24 hours

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import json, os.path, requests, sys
from requests_oauthlib import OAuth1

sys.path.append("..")

from common.common import log, countdown

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
	
	UPLOAD_ENDPOINT = "https://upload.twitter.com/1.1/media/upload.json" # returns media_id which can be used with the tweet endpoint
	TWEET_ENDPOINT  = "https://api.twitter.com/1.1/statuses/update.json"
	TIMEOUT         = 60
	
	return {
		"UPLOAD_ENDPOINT" : UPLOAD_ENDPOINT,
		"TWEET_ENDPOINT"  : TWEET_ENDPOINT,
		"OAUTH"           : OAUTH,
		"TIMEOUT"         : TIMEOUT
	}


def post(path, caption, token_path, n=1):
	consts = get_consts(token_path)
	
	def INIT(path):
		params = {
			"command"     : "INIT",
			"media_type"  : "image/jpg",
			"total_bytes" : os.path.getsize(path)
		}
		
		try:
			r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"], timeout=consts["TIMEOUT"])
			return r.json()["media_id"]
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			log(f"Connection Error! Could not upload frame {path} to Twitter!")
			log("Failed at INIT stage.")
			log(f"Trying again in {n} seconds. (Press any button to try again now.)", flush=True)
			countdown(n)
			print()
			post(path, caption, token_path, n=n*2)

	def APPEND(path, id):
		segment_id = 0
		bytes_sent = 0
		
		with open(path, "rb") as f:	
			while bytes_sent < os.path.getsize(path):
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
					r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, files=files, auth=consts["OAUTH"], timeout=consts["TIMEOUT"])
				except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
					log(f"Connection Error! Could not upload frame {path} to Twitter!")
					log("Failed at APPEND stage.")
					log(f"Trying again in {n} seconds. (Press any button to try again now.)", flush=True)
					countdown(n)
					print()
					post(path, caption, token_path, n=n*2)
				else:
					segment_id += 1
					bytes_sent = f.tell()

	def FINALIZE(id):
		params = {
			"command"  : "FINALIZE",
			"media_id" : id
		}
		
		try:
			r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"], timeout=consts["TIMEOUT"])
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			log(f"Connection Error! Could not upload frame {path} to Twitter!")
			log("Failed at FINALIZE stage.")
			log(f"Trying again in {n} seconds. (Press any button to try again now.)", flush=True)
			countdown(n)
			print()
			post(path, caption, token_path, n=n*2)
	
	def tweet(media_id, caption):
		params = {
			"media_ids" : media_id,
			"status"    : caption
		}
		
		queue = []
		
		try:
			r = requests.post(consts["TWEET_ENDPOINT"], data=params, auth=consts["OAUTH"], timeout=consts["TIMEOUT"])
			log(f"Received code {r.status_code}.")
			if r.status_code in range(500, 505): raise requests.exceptions.ConnectionError         # 500 errors are typically temporary
			if r.status_code != 200: log(f"{json.dumps(r.json(), sort_keys=True, indent=4)}")
			else: log(f"created_at {json.dumps(r.json()['created_at'], sort_keys=True, indent=4)}\n\t\t\tid {json.dumps(r.json()['id'], sort_keys=True, indent=4)}")
			print()
		except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
			log(f"Connection Error! Could not upload frame {path} to Twitter!")
			log("Failed at tweeting stage.")
			log(f"Trying again in {n} seconds. (Press any button to try again now.)", flush=True)
			countdown(n)
			print()
			post(path, caption, token_path, n=n*2)
			
	id = INIT(path)
	APPEND(path, id)
	FINALIZE(id)
	tweet(id, caption)