# python create_combine_text.py <in_dir> <out_file>
# e.g. python create_combine_text.py ..\dalnet\QA-done\transcripts .\text.txt
import os
import sys


if __name__ == '__main__':
	in_dir = sys.argv[1]
	out_file = sys.argv[2]

	utterances = []
	for root, dirs, files in os.walk(in_dir):
		for file in files:
			temp_file = open(root + '\\' + file, 'r')
			for utt in temp_file:
				utterances.append(utt)

	temp_file.close()

	utterances.sort()
	print(len(utterances))
	temp_file = open(out_file, 'w')
	i = 0
	for utt in utterances:
		temp_file.write(utt + '\n')
		i += 1
		print(i)	
	print(len(utterances))
	temp_file.close()
