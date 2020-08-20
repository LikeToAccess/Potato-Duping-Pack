#pylint:disable=C0321
#pylint:disable=C0410
#pylint:disable=C0103
#pylint:disable=W0611
#pylint:disable=W0312
"""
creates files with specific names
CREDIT: Rico Alexander, cheelo21
"""
from string import digits
from time import sleep
import os, blacklist

item_counts = {
	32:[],
	16:[],
	8:[],
	3:[]
}

#################################################

f = open("Minecraft ID List.txt", "r")
data = f.read().replace("\t", "").replace(" ", "")
f.close()
for digit in digits:
	data = data.replace(str(digit),"")
data = data.split("\n")
try: os.system("cls")
except OSError: pass

for c, line in enumerate(data):
	if not line[:11] == "(minecraft:" and line[::-1][:1] == ")":
		data.pop(c)
#running the blacklist checks in a loop was contributed by cheelo21
for i in range(100):
	for c, line in enumerate(data):
		for item in blacklist.blacklist:
			#                                                            \/ BAD
			if item == line.strip(")")[11:] and blacklist.whitelist_fuzzy[0] not in line.strip(")")[11:]:
				print("Banned: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
				print("from: \"blacklist\" and kwarg: \"{}\"".format(item))
				data.pop(c)
				break
#running the blacklist checks in a loop was contributed by cheelo21
for i in range(100):
	for c, line in enumerate(data):
		for item in blacklist.blacklist_fuzzy:
			#                                                            \/ BAD
			if item in line.strip(")")[11:] and blacklist.whitelist_fuzzy[0] not in line.strip(")")[11:]:
				print("Banned: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
				print("from: \"blacklist_fuzzy\" and kwarg: \"{}\"".format(item))
				data.pop(c)
				break
print("\n"+("#"*50+"\n")*3)

################################################

for c, line in enumerate(data):
	for item in blacklist.item_counts32:
		if "(minecraft:"+item+")" == line:
			print("Changed: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
			print("to: \"32\" from kwarg: \"{}\"".format(item))
			item_counts[32].append(item)
	for item in blacklist.item_counts16_fuzzy:
		if item in line.strip(")")[11:]:
			print("Changed: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
			print("to: \"16\" from kwarg: \"{}\"".format(item))
			item_counts[16].append(item)
	for item in blacklist.item_counts8_fuzzy:
		if item in line.strip(")")[11:]:
			print("Changed: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
			print("to: \"8\" from kwarg: \"{}\"".format(item))
			item_counts[8].append(item)
	for item in blacklist.item_counts3_fuzzy:
		if item in line.strip(")")[11:]:
			print("Changed: \"{0}\"".format(data[c].strip(")")[11:]),end=" ")
			print("to: \"3\" from kwarg: \"{}\"".format(item))
			item_counts[3].append(item)
print("\n"+("#"*50+"\n")*3)

#################################################

os.chdir("dump")
filenames = []
for c, line in enumerate(data):
	if line[:11] == "(minecraft:" and line[::-1][:1] == ")":
		line = line.strip("(").strip(")")
		if line in filenames:
			continue
		filenames.append(line)

#################################################

f = open("../template.json", "r")
template = f.read().split("\n")
f.close()

for filename in filenames:
	data = []
	for line in template:
		if "|INJECT|" in line:
			line = line.replace("|INJECT|", filename)
		if "|COUNT INJECT|" in line:
			for item_count in item_counts[32]:
				if "minecraft:"+item_count == filename:
					line = line.replace("|COUNT INJECT|", "32")
			for item_count in item_counts[16]:
				if item_count in filename:
					line = line.replace("|COUNT INJECT|", "16")
			for item_count in item_counts[8]:
				if item_count in filename:
					line = line.replace("|COUNT INJECT|", "8")
			for item_count in item_counts[3]:
				if item_count in filename:
					line = line.replace("|COUNT INJECT|", "3")

		if "|COUNT INJECT|" in line:
			line = line.replace("|COUNT INJECT|", "64")
		data.append(line)

	filename = filename.replace("minecraft:", "")+".json"
	f = open(filename, "w")
	f.write("\n".join(data))
	f.close()
	print("Created: \"{}\"".format(filename))
