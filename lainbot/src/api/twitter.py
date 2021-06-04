# rate limits: 300 tweets per 3 hours (100/hr), 1000 tweets per 24 hours

import requests, json, base64, urllib.parse, os.path, time, sys

sys.path.append("..")

from requests_oauthlib import OAuth1
import common.common

raw = json.load(open("tokens.json"))
api_key = raw["tokens"]["twitter"]["api_key"]
api_secret = raw["tokens"]["twitter"]["api_secret"]
access_token = raw["tokens"]["twitter"]["access_token"]
access_token_secret = raw["tokens"]["twitter"]["access_token_secret"]

tweet_endpoint = "https://api.twitter.com/1.1/statuses/update.json"
img_upload_endpoint = "https://upload.twitter.com/1.1/media/upload.json" # returns media_id which can be used with the tweet endpoint

oauth = OAuth1(api_key, client_secret=api_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)

class ImageUpload:
	def __init__(self, img_path):
		self.img = img_path
		self.total_bytes = os.path.getsize(img_path)
		self.media_id = None
		self.processing_info = None
		
	def upload_init(self):
		print("INIT")

		request_data = {
			"command" : "INIT",
			"media_type" : "image/png",
			"total_bytes" : self.total_bytes,
			"media_category" : "tweet_image"
		}

		r = requests.post(url=img_upload_endpoint, data=request_data, auth=oauth)
		self.media_id = r.json()["media_id"]
		print(self.media_id)

	def upload_append(self):
		seg_id = 0
		bytes_sent = 0
		f = open(self.img, "rb")
		
		while bytes_sent < self.total_bytes:
			chunk = f.read(4*1024*1024)
			
			print("APPEND")
			
			request_data = {
				"command" : "APPEND",
				"media_id" : self.media_id,
				"segment_index" : seg_id
			}
			
			files = {
				"media" : chunk
			}
			
			r = requests.post(url=img_upload_endpoint, data=request_data, files=files, auth=oauth)
			
			if r.status_code not in range (200, 300):
				print(r.status_code)
				print(r.text)
				sys.exit(0)
			
			seg_id += 1
			bytes_sent = f.tell()
			
			print(f"{bytes_sent} of {self.total_bytes} uploaded.")
		
		print("Upload chunks complete.")
			
	def upload_finalize(self):
		print("FINALIZE")
		
		request_data = {
			"command" : "FINALIZE",
			"media_id" : self.media_id
		}
		
		r = requests.post(url=img_upload_endpoint, data=request_data, auth=oauth)
		print(r.json())
		
		self.processing_info = r.json().get("processing_info", None)
		
	def check_status(self):
		if self.processing_info is None:
			return
		
		state = self.processing_info["state"]
		
		print(f"Media processing status is {state}")
		
		if state == u'Succeeded':
			return
			
		if state == u'failed':
			sys.exit(0)
			
		check_after_secs = self.processing_info["check_after_secs"]
		print(f"Checking after {check_after_secs} seconds.")
		time.sleep(check_after_secs)
		
		print("STATUS")
		
		request_params = {
			"command" : "STATUS"
		}
		
		r = requests.get(url=img_upload_endpoint, params=request_params, auth=oauth)
		
		self.processing_info = r.json().get("processing_info", None)
		check_status()
		
	def tweet(self):
		request_data = {
			"status" : common.common.msg,
			"media_ids" : self.media_id
		}
		
		r = requests.post(url=tweet_endpoint, data=request_data, auth=oauth)
		print(r.json())

if __name__ == "__main__":
	Tweet = ImageUpload(common.common.filename)
	Tweet.upload_init()
	Tweet.upload_append()
	Tweet.upload_finalize()
	#Tweet.tweet()