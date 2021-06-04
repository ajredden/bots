# this module acquires the next file and its caption, and passes them to api/facebook.py and api/twitter.py

# Exit codes:
#	-1: Generic error code
#	0: All clear
#	1: Invalid argument supplied

#filename = "..\\testing\\test.png"
#msg = None

import os, os.path, sys, re

FRAMES_DIR = r"D:\Not Mods\lainbot"

def print_error():
	print("Unspecified error")
	sys.exit(-1)

def parse_args():
	switches = {
		"--help"          : False,
		"--quiet"         : False,
		"--silent"        : False,
		"--verbose"       : False,
		"--episode-start" : 1,
		"--frame-count"   : 1
	}
	
	short_names = {
		"--help"          : "-h",
		"--quiet"         : "-q",
		"--silent"        : "-s",
		"--verbose"       : "-v",
		"--episode-start" : "-e",
		"--frame-count"   : "-f"
	}
	
	for arg in sys.argv[1:]:
		if arg.startswith("-") and (arg not in switches and arg not in short_names.values()):
			print(f"Error: Unrecognised argument {arg}")
			sys.exit(1)
				
	# matches patterns such as {--xyz a}, {--foo-bar 13} and {-x 3}
	pattern = r"--[\w-]+ [\w-]+|-\w [\w-]+"
	
	# matches patterns such as {--spam -} (the trailing hyphen indicates a new argument), {-t -}, 
	# and {--eggs} followed by a new line
	pattern_flags = r"--[\w-]+ -|--[\w-]+$|-\w -|-\w$"
	
	switches.update({k.split()[0]: k.split()[1] for k in re.findall(pattern, " ".join(sys.argv[1:]))})
	switches.update({k.replace(" -", ""): True for k in re.findall(pattern_flags, " ".join(sys.argv[1:]))})
	
	# assign the values of short-named switches (-h, -f, -e) to their corresponding long-named switches, and delete
	# the short-named switches
	# TODO this doesn't work when passing -e --frame-count 13 (--frame-count set to 1)
	# but it does work when just passing --frame-count 13 for some reason
	for key in list(switches):
		switches[key] = (switches.get(short_names.get(key))) or switches[key]
	if key in short_names.values():
		del switches[key]
	
	return switches

#parse_args()

class Upload:
	def __init__(self, fd, start_frame=1, start_episode=1):
		self.fd = fd
	def main(self):
		pass

dir_tree = os.walk(FRAMES_DIR)