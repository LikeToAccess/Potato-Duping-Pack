from string import digits

f = open("Minecraft ID List.txt", "r")
data = f.read()
f.close()
old_data = data.replace("\t", "").replace(" ", "")
for digit in digits:
	old_data = old_data.replace(str(digit),"")
old_data = old_data.split("\n")
new_data = []

for line in old_data:
	print(line,end=" ")
	if line[:11] == "(minecraft:" and line[::-1][:1] == ")":
		print("IS GOLD")
		new_data.append(line)
	else:
		#data.pop(c)
		print("IS GONE")

f = open("Minecraft ID List OLD.txt", "w")
f.write("\n".join(data.split("\n")))
f.close()

f = open("Minecraft ID List.txt", "w")
f.write("\n".join(new_data))
f.close()
