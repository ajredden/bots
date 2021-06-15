# this module acquires the next file and its caption, and passes them to api/facebook.py, api/twitter.py and api/telegram.py

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful
# 4: Invalid website supplied for upload

import os, os.path, sys, time, requests

import api.facebook, api.twitter, api.telegram

FRAMES_DIR = r"D:\lainbot"
TOKEN_PATH = r"api\tokens.json"
SITES_POSTED_TO = ["facebook", "twitter", "telegram"]
DELAY_SECONDS = 60

class Upload:
	def __init__(self):
		self.dir_tree = os.walk(FRAMES_DIR)

	def get_next_frame(self):
		for dir in self.dir_tree:
			if dir[1]:
				continue

			lastFile = dir[2][-1]
			for file in os.scandir(dir[0]):
				yield (file.path, file.name, lastFile)

def check_queued_frames(confirm=False):
	with open(".continue_from", "r") as f:
		restart_frame = ":".join(f.readline().split(":")[1:]).strip()
		if not confirm:
			print(f"Continue from frame {restart_frame}? (Y / N)")
		else:
			print(f"Start from the beginning? (Y / N)")
		
		choice = input("> ").lower()
		
		while choice != "y" and choice != "n":
			return check_queued_frames(confirm=confirm)
			
		if choice == "y":
			if not confirm:
				print(f"Continuing from frame {restart_frame}.")
				f.seek(0)
				lines = f.readlines()
				return {k.split(":")[0] : (":".join(k.split(":")[1:]).strip()) for k in lines}
			else:
				return { "facebook" : "D:\lainbot\Layer 01; Weird\00000001.jpg",
						 "twitter"  : "D:\lainbot\Layer 01; Weird\00000001.jpg",
						 "telegram" : "D:\lainbot\Layer 01; Weird\00000001.jpg"
					   }
		else:
			if not confirm:
				return check_queued_frames(confirm=True)
			else:
				sys.exit(0)

def post_to(site, frame_dir, frame, msg, token_path):
	print("Posting frame", frame_dir, frame, "to", site.capitalize())
	if site == "facebook":
		api.facebook.post(frame_dir, frame, msg, token_path)
	elif site == "twitter":
		api.twitter.post(frame_dir, frame, msg, token_path)
	elif site == "telegram":
		api.telegram.post(frame_dir, frame, msg, token_path)
	else:
		print("Error: website not recognised.")
		sys.exit(4)

def post_all(frame_path, token_path, delay=DELAY_SECONDS):
	frame_dir = "\\".join(frame_path.split("\\")[:-1])
	frame = frame_path.split("\\")[-1]

	if frame_dir.startswith("z_"):
		episode_name = frame_dir.split("\\")[-1].replace("z_", "") + "\\" + frame_dir.split("\\")[-1].replace(";", ":")
	else:
		episode_name = frame_dir.split("\\")[-1].replace(";", ":")
	
	current_frame = frame.lstrip('0').rstrip(".jpg")
	final_frame   = os.listdir(frame_dir)[-1].lstrip('0').rstrip(".jpg")

	msg = f"{episode_name}, frame {current_frame} / {final_frame}"

	print(msg)
	
	post_to("facebook", frame_dir, frame, msg, token_path)
	post_to("twitter", frame_dir, frame, msg, token_path)
	post_to("telegram", frame_dir, frame, msg, token_path)

def main():
	try:
		check_queued_frames()
		UploadObj = Upload()
		
		with open(".continue_from") as q:
			for line in q.readlines():
				site = line.split("|")[0]
				current_path = line.split("|")[1].strip()
				current_frame_dir = "\\".join(current_path.split("\\")[:-1])
				current_frame = line.split("\\")[-1]
				 
				ext = ".jpg\n"
				bs = "\\"
				next_frame = f"{(int(current_frame.rstrip(ext)) + 1):0>8}.jpg"
				next_path = f"{current_frame_dir}\\{next_frame}"
				msg = f"{current_frame_dir.split(bs)[-1].replace(';', ':')}, frame {current_frame.lstrip('0').rstrip('.jpg')} / {os.listdir(current_frame_dir)[-1].lstrip('0').rstrip('.jpg')}"
				print(f"Uploading {next_path} to {site.capitalize()}.")
				
				post_to(site, current_frame_dir, next_frame, msg, TOKEN_PATH)
				latest = f"{current_frame_dir}\\{next_frame:0>8}"
			
		flag_skip = True
		for frame_iter in UploadObj.get_next_frame():
			if frame_iter[0] != latest and flag_skip:
				continue
			flag_skip = False
			time.sleep(1)
			post_all(frame_iter[0], TOKEN_PATH)
			print("-"*50)
			time.sleep(DELAY_SECONDS)
	except StopIteration as e:
		print("Success! Posted all SEL frames!")
	#except Exception as e:
	#	print("An unspecified error occurred.")
	#	print(e)
	#	sys.exit(-1)

main()