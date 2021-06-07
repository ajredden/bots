# this module acquires the next file and its caption, and passes them to api/facebook.py, api/twitter.py and api/telegram.py

# Exit codes:
# -1: Unspecified error
# 0: All clear
# 1: Invalid argument
# 2: Connection error
# 3: Chunk upload unsuccessful

import os, os.path, sys, re, time, asyncio

import api.facebook, api.twitter, api.telegram

FRAMES_DIR = r"D:\lainbot"
TOKEN_PATH = r"api\tokens.json"

# def parse_args():
	# switches = {
		# "--help"          : False,
		# "--quiet"         : False,
		# "--silent"        : False,
		# "--verbose"       : False,
		# "--episode-start" : 1,
		# "--frame-count"   : 1
	# }
	
	# short_names = {
		# "--help"          : "-h",
		# "--quiet"         : "-q",
		# "--silent"        : "-s",
		# "--verbose"       : "-v",
		# "--episode-start" : "-e",
		# "--frame-count"   : "-f"
	# }
	
	# for arg in sys.argv[1:]:
		# if arg.startswith("-") and (arg not in switches and arg not in short_names.values()):
			# print(f"Error: Unrecognised argument {arg}")
			# sys.exit(1)
				
	# # matches patterns such as {--xyz a}, {--foo-bar 13} and {-x 3}
	# pattern = r"--[\w-]+ [\w-]+|-\w [\w-]+"
	
	# # matches patterns such as {--spam -} (the trailing hyphen indicates a new argument), {-t -}, 
	# # and {--eggs} followed by a new line
	# pattern_flags = r"--[\w-]+ -|--[\w-]+$|-\w -|-\w$"
	
	# switches.update({k.split()[0]: k.split()[1] for k in re.findall(pattern, " ".join(sys.argv[1:]))})
	# switches.update({k.replace(" -", ""): True for k in re.findall(pattern_flags, " ".join(sys.argv[1:]))})
	
	# # assign the values of short-named switches (-h, -f, -e) to their corresponding long-named switches, and delete
	# # the short-named switches
	# # TODO this doesn't work when passing -e --frame-count 13 (--frame-count set to 1)
	# # but it does work when just passing --frame-count 13 for some reason
	# for key in list(switches):
		# switches[key] = (switches.get(short_names.get(key))) or switches[key]
	# if key in short_names.values():
		# del switches[key]
	
	# return switches

class Upload:
	def __init__(self, start_episode=1, start_frame=1):
		self.dir_tree = os.walk(FRAMES_DIR)
		
	def get_next_frame(self):
		for dir in self.dir_tree:
			if dir[1]:
				continue
			
			lastFile = dir[2][-1]
			for file in os.scandir(dir[0]):
				yield (file.path, file.name, lastFile)

async def post_fb(frame, msg, token_path):
	print(f"Posting frame", frame[0].split("\\")[-2], frame[0].split("\\")[-1], "to Facebook")
	api.facebook.post(frame[0], msg, token_path)

async def post_twitter(frame, msg, token_path):
	print(f"Posting frame", frame[0].split('\\')[-2], frame[0].split("\\")[-1], "to Twitter")
	api.twitter.post(frame[0], msg, token_path)

async def post_telegram(frame, msg, token_path):
	print(f"Posting frame", frame[0].split('\\')[-2], frame[0].split("\\")[-1], "to Telegram")
	api.telegram.post(frame[0], msg, token_path)

async def post_all(frame, token_path):
	if frame[0].split("\\")[-2].startswith("z_"):
		episode_name = frame[0].split("\\")[-2].replace("z_", "") + "\\" + frame[0].split("\\")[-2].replace(";", ":")
	else:
		episode_name  = frame[0].split("\\")[-2].replace(";", ":")
	current_frame = frame[1].lstrip('0').rstrip(".jpg")
	final_frame   = frame[2].lstrip('0').rstrip(".jpg")
	
	msg = (f"{episode_name}, frame {current_frame} / {final_frame}")
	
	try:
		L = asyncio.gather(
			post_fb(frame, msg, token_path),
			post_twitter(frame, msg, token_path),
			post_telegram(frame, msg, token_path),
		)
		pass
	except requests.ConnectionError as e:
		print("Error! Connection failed!")
		print(e)
		sys.exit(2)

def check_start_frame(do_continue="", definitely_restart=""):
		with open(".continue_from", "r") as f:
			restart_frame = f.read()
			print(f"Continue from frame {restart_frame}? (Y / N)")
			while do_continue.lower() != "y" and do_continue.lower() != "n":
				do_continue = input("> ")
				if do_continue.lower() == "y":
					print(f"Continuing from frame {restart_frame}.")
					f.seek(0)
					return f.read()
				elif do_continue.lower() == "n":
					print("Start from the beginning? (Y / N)")
					while definitely_restart.lower() != "y" and definitely_restart.lower() != "n":
						definitely_restart = input("> ")
						if definitely_restart == "y":
							return r"D:\lainbot\Layer 01; Weird\00000001.jpg"
						elif definitely_restart.lower() == "n":
							return check_start_frame()

def main():
	try:
		U = Upload()
		start_frame = r"D:\lainbot\Layer 01; Weird\00000001.jpg"
		flag_skip_frames = True
		if os.path.exists(".continue_from"):
			start_frame = check_start_frame()
		for frame in U.get_next_frame():
			print(frame[0])
			if frame[0] != start_frame and flag_skip_frames:
				continue
			flag_skip_frames = False
			asyncio.run(post_all(frame, TOKEN_PATH))
			time.sleep(60)
	except StopIteration as e:
		print("Success! Posted all SEL frames!")
	except Exception as e:
		print("An unspecified error occurred.")
		print(e)
		sys.exit(-1)
	finally:
		with open(".continue_from", "w") as f:
			f.write(frame[0])

main()