# rate limits: 4800 * engagements per hour (DON'T BE LAZY. ACCOUNT FOR THIS)
# percentage used of allocated quota per hour may be in a header X-App-Usage if I use enough; check that

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

# 1. POST to /app/uploads
# 2. POST to /upload:{unique_identifier}
# 3. Repeatedly POST to this endpoint until the file finishes uploading; check status by sending a GET request to it
# 4. Use the file handler obtained from the POST in other areas of the Graph API
# 
# UPLOAD_SESSION_ENDPOINT = f"https://graph.facebook.com/v10.0/app/uploads"
# def get_upload_session(filename):
	# params = {
		# "access_token" : ACCESS_TOKEN,
		# "file_length"  : os.path.getsize(filename),
		# "file_type"    : "image/png"
	# }
	# r = requests.post(f"{UPLOAD_SESSION_ENDPOINT}", data=params)
	# return r.json()["id"]

# def upload(session, offset, filename):
	# fh = open(filename, "rb")
	# headers = {
		# "file_offset"   : str(offset),
		# "Authorization" : f"OAuth {ACCESS_TOKEN}",
		# "Host"          : "graph.facebook.com",
		# "Connection"    : "close"
	# }
	# files = {
		# "file" : fh
	# }
	
	# r = requests.post(f"https://graph.facebook.com/v10.0/{session}", files=files, headers=headers) # "upload:" included in session id
	# q = requests.get(f"https://graph.facebook.com/v10.0/{session}", headers=headers)
	
	# print(q.json())
	# return r.json()

# def main():
	# offset = 0
	
	# session = get_upload_session(FILENAME)
	# response = upload(session, offset, FILENAME)

	# headers = {
		# "Authorization": f"OAuth {ACCESS_TOKEN}",
		# "Host"         : "graph.facebook.com",
		# "Connection"   : "close"
	# }

	# while "h" not in response:
		# offset += 4*1024
		# print(offset)
		# response = upload(session, offset, FILENAME)

	# file_handle = response["h"]
	# print(f"file_handle: {file_handle}")
	# return file_handle

# file_handle = main()
# r = requests.post(f"{IMG_POST_ENDPOINT}?access_token={ACCESS_TOKEN}&link={file_handle}")
# print(r.json())

import requests, json

def get_consts(token_path):
	raw = json.load(open(token_path, "rb"))
	ALBUM_ID                = "313864630294862"
	
	return {
		"ACCESS_TOKEN"      : raw["tokens"]["facebook"]["page"]["token"],
		"IMG_POST_ENDPOINT" : f"https://graph.facebook.com/v10.0/{ALBUM_ID}/photos"
	}

def post(frame, msg, token_path):
	consts = get_consts(token_path)

	files = {
		"file" : open(frame, "rb")
	}

	params = {
		"access_token" : consts["ACCESS_TOKEN"],
		"caption"      : msg
	}
	
	try:
		r = requests.post(f"{consts['IMG_POST_ENDPOINT']}", data=params, files=files)
		print(r.json())
	except requests.ConnectionError as e:
		print(f"Connection error! Could not upload {frame}!")
		print(e)
		sys.exit(2)