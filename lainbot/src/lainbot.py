# this module acquires the next file and its caption, and passes them to api/facebook.py, api/twitter.py and api/telegram.py

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful
# 4: Invalid website supplied for upload

import os, sys, time

import api.telegram, api.facebook, api.twitter
from common.common import log, check_cw

FRAMES_DIR    = r"D:\lainbot"
TOKEN_PATH    = r"api\tokens.json"
DELAY_SECONDS = 60

class Upload:
	def __init__(self):
		self.dir_tree = os.walk(FRAMES_DIR)
	
	def get_next_frame(self):
		for tup in self.dir_tree:                              # tuple is of the form (dirpath, directories, files)
			if tup[1]:                                         # if the current directory has other directories in it
				continue                                       # advance the iterator (explore the next directory)
				
			lastFile = tup[2][-1]
			for file in os.scandir(tup[0]):                    # iterator returns a DirEntry object, but I'm only interested in two attributes of the object, so...
				yield (file.path, tup[0], file.name, lastFile) # yield a tuple containing the attributes I need (plus a little bit more information)

def check_queued_frame(frame, confirm=False):
	# this function could be better. it's pretty confusing
	
	if not confirm:
		print(f"Continue from frame {frame}? (Y / N)")
	else:
		print(f"Start from the beginning? (Y / N)")
	
	choice = input("> ").lower()
	
	while choice not in "yn":
		return check_queued_frame(frame, confirm=confirm)
	
	if choice == "y":
		if not confirm:
			print(f"Continuing from frame {frame}.")
			return frame
		else:
			return r"D:\lainbot\Layer 01; Weird\00000001.jpg"
	else:
		if not confirm:
			return check_queued_frame(frame, confirm=True)
		else:
			sys.exit(0)

def post_all(frame_path, frame_head, frame_tail, last_frame):
	# encapsulates the three calls to the APIs
	caption = get_caption(frame_head, frame_tail, last_frame)
	print(caption)
	post_to("telegram", frame_path, caption)
	post_to("facebook", frame_path, caption)
	post_to("twitter",  frame_path, caption)

def post_to(site, path, caption):
	# calls the appropriate .post() function depending on the passed site
	log(f"Posting frame {path} to {site.capitalize()}.")
	if site == "telegram":
		api.telegram.post(path, caption, TOKEN_PATH)
	elif site == "facebook":
		api.facebook.post(path, caption, TOKEN_PATH)
	elif site == "twitter":
		api.twitter.post(path, caption, TOKEN_PATH)
	else:
		log("Error: website not recognised.")
		sys.exit(4)

def get_caption(frame_head, frame_tail, last_frame):
	# create and return the message posted alongside each photo, including any CWs
	episode_name = get_episode_name(frame_head)
	frame_number = frame_tail.lstrip("0").rstrip(".jpg")
	
	return f"{check_cw(episode_name, frame_number)}{episode_name}, frame {frame_number} / {last_frame}{' (nice)' if int(frame_number) == 69 or int(frame_number) == 6969 else ''}"

def get_episode_name(path):
	# usually, the episode name is just a directory name with any semi-colons replaced with colons.
	# however, there is an edge case, entirely created by myself for stylistic reasons, where an "episode name"
	# can actually consist of two elements: "first_directory_name/second_directory_name"
	# this edge case is made more complex by first_directory_name starting with "z_", because I wanted the frames in this directory 
	# to be posted AFTER the rest of the episodes, but with an episode number 00, which would usually place it BEFORE the other episodes
	# (as I said, completely my doing)
	# this function just deals with that edge case without making everything else look ugly
	if path.split("\\")[-2].startswith("z_"):
		return (path.split("\\")[-2] + "/" + path.split("\\")[-1]).replace("z_", "").replace(";", ":")
	else:
		return (path.split("\\")[-1]).replace(";", ":")

def main():
	try:
		UploadObj          = Upload()                                          # perhaps this class and object could be named more clearly
		flag_skip          = True
		continue_from_path = check_queued_frame(open(".continue_from").read()) # .continue_from is a simple text file containing the path to the frame to be continued from and nothing else
		                                                                       # eventually I'll probably implement this as a command-line argument instead
		
		for frame_properties_iter in UploadObj.get_next_frame():
			current_frame_path    = frame_properties_iter[0]                   # clearer variable names
			current_frame_head    = frame_properties_iter[1]
			current_frame_tail    = frame_properties_iter[2]
			last_frame_in_episode = frame_properties_iter[3].lstrip("0").rstrip(".jpg\n")
			
			if current_frame_path != continue_from_path and flag_skip:        # this part of the loop quickly skips through any frames that have already been uploaded
				print(f"Skipping frame {current_frame_path}...")              # (without uploading them a second time)
				continue
			flag_skip = False
			
			post_all(current_frame_path, current_frame_head, current_frame_tail, last_frame_in_episode)
			print("-"*50)
			
			time.sleep(DELAY_SECONDS)
	except StopIteration:                                                    # all synchronous iterators raise this exception when they contain no more elements
		print("Success! Posted all SEL frames!")                             # (in this case the iterator runs out when it has no more frames to post)

if __name__ == "__main__":
	main()