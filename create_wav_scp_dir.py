# How to run
# python create_wav_scp_dir.py ..\\test-QA\\wavs ..\\wav.scp
# ..\\test-QA\\wavs is the directory which contain wav files per speaker

import os
import sys

waves_path = sys.argv[1]
wav_scp = sys.argv[2]

wav_pair = []
for root, dirs, files in os.walk(waves_path):
	for file in files:
		if '.wav' in file:
			wav_pair.append(file.replace('.wav','') + ' ' + root+'//' + file)

with open(wav_scp, 'w') as f:
	for wav in wav_pair:
		f.write(wav + '\n')