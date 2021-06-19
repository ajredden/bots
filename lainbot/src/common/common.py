import time, sys, msvcrt

def check_cw(ep, frame):
	ret = ""
	frame = int(frame)
	if ep == "Layer 01: Weird":
		if frame in range(5773, 5866) or frame in range(5933, 5942):
			ret = "sui"
		if frame in range(6171, 6246) or frame in range(6330, 6450):
			ret = "sui, blood"
		if frame in range(11791, 11831) or frame in range(20381, 20453):
			ret = "sui mention"
		if frame in range(13273, 13457):
			ret = "body horror"
	elif ep == "Layer 02: Girls":
		if frame in range(24954, 24992) or frame in range(25560, 25854) or frame in range(26873, 26902) \
				or frame in range(27633, 27653) or frame in range(27821, 28117) or frame in range(28165, 28257) \
				or frame in range(28329, 28405):
			ret = "gun violence"
		if frame in range(25390, 25481) or frame in range(26514, 26541) or frame in range(28587, 28641) \
				or frame in range(28758, 28866):
			ret = "blood"
		if frame in range(28507, 28581) or frame in range(28641, 28687) or frame in range(28867, 29154):
			ret = "gun violence, sui"
		if frame in range(28687, 28758):
			ret = "sui, blood"
	elif ep == "Layer 03: Psyche":
		pass
	elif ep == "Layer 04: Religion":
		pass
	elif ep == "Layer 05: Distortion":
		pass
	elif ep == "Layer 06: KIDS":
		pass
	elif ep == "Layer 07: SOCIETY":
		pass
	elif ep == "Layer 08: RUMORS":
		pass
	elif ep == "Layer 09: PROTOCOL":
		pass
	elif ep == "Layer 10: LOVE":
		pass
	elif ep == "Layer 11: Infornography":
		pass
	elif ep == "Layer 12: Landscape":
		pass
	elif ep == "Layer 13: Ego":
		pass
	elif ep.split("\\")[-2] == "Layer 00: Auxiliary":
		pass
	
	if ret: ret = f"(cw: {ret})\n\n"
	return ret

def log(msg, file=sys.stdout):
	print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}]\t{msg}", file=file)

def countdown(n):
	for s in range(n, 0, -1):
		countdown = f"Trying again in {s} seconds. (Press any button to try again now.)"
		print("\b" * len(countdown), end="", flush=True)
		print(countdown, end="", flush=True)
		if msvcrt.kbhit():                                   # essentially acts as non-blocking input, allowing me to have a countdown
			msvcrt.getch()                                   # whilst still allowing the user to forcefully retry a connection
			break
		time.sleep(1)

if __name__ == "__main__":
	print(check_cw("Layer 01: Weird", 5774), end="")
	log("Foobar")