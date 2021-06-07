# rate limits: 300 tweets per 3 hours (100/hr), 1000 tweets per 24 hours

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import json, os.path, requests, sys, time
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


def post(frame, msg, token_path):
	consts = get_consts(token_path)
	
	def INIT(frame):
		params = {
			"command" : "INIT",
			"media_type" : "image/jpg",
			"total_bytes" : os.path.getsize(frame)
		}
		
		r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"])
		return r.json()["media_id"]

	def APPEND(frame, id):
		segment_id = 0
		bytes_sent = 0
		
		try:
			with open(frame, "rb") as f:	
				while bytes_sent < os.path.getsize(frame):
					chunk = f.read(4*1024*1024)

					params = {
						"command"       : "APPEND",
						"media_id"      : id,
						"segment_index" : segment_id
					}
				
					files = {
						"media" : chunk
					}
				
					r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, files=files, auth=consts["OAUTH"])
				
					segment_id += 1
					bytes_sent = f.tell()
		except requests.HTTPError as e:
			print("Error! Chunk upload unsuccessful!")
			print(e)
			sys.exit(3)

	def FINALIZE(id):
		params = {
			"command" : "FINALIZE",
			"media_id" : id
		}
		
		r = requests.post(consts["UPLOAD_ENDPOINT"], data=params, auth=consts["OAUTH"])
	
	def tweet(media_id, msg):
		params = {
			"media_ids" : media_id,
			"status"    : msg
		}

		r = requests.post(consts["TWEET_ENDPOINT"], data=params, auth=consts["OAUTH"])
		print(f"\t[{time.strftime('%d/%m/%y %H:%M:%S')}] created_at {json.dumps(r.json()['created_at'], sort_keys=True, indent=4)} / id {json.dumps(r.json()['id'], sort_keys=True, indent=8)}\n")
	
	id = INIT(frame)
	APPEND(frame, id)
	FINALIZE(id)
	tweet(id, msg)