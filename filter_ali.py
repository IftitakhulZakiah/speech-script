ali_file = open('temp\\ali.all.txt', 'r')
idxs = []
for line in ali_file:
	if 'WARNING (gmm-align-compiled' in line and ' Retrying utterance' in line:
		token = line.split()
		idxs.append(token[-4:-3][0])
for idx in idxs:
	print(idx)
