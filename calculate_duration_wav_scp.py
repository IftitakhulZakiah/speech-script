# How to run
# python calculate_duration.py wav.scp


import wave
import contextlib
import os
import datetime
import sys

wav_file = open(sys.argv[1],'r')
path_files = []
for line in wav_file:
	path_files.append(line.split()[1])
wav_file.close()

# path_files=[]
# for root, dirs, files in os.walk(path):
# 	for file in files:
# 		path_files.append(root+'//'+file)


total_duration = 0
for fname in path_files:
	print(fname)
	with contextlib.closing(wave.open(fname,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	    total_duration += duration

print('Duration ' + str(datetime.timedelta(seconds=total_duration)) + ' with ' + str(len(path_files)) + ' files')