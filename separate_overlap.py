# python separate_overlap.py <in_file> <out_file> <out_file_overlap>
# e.g. python separate_overlap.py ..\dalnet\QA-done\text.txt ..\dalnet\QA-done\text_non_overlap.txt ..\dalnet\QA-done\text_overlap.txt

import os
import sys


if __name__ == '__main__':
	in_file = sys.argv[1]
	out_file = sys.argv[2]
	overlap_file = sys.argv[3]

	overlap = []
	non_overlap = []

	file = open(in_file, 'r')
	for utt in file:
		idx = utt.split()[0]
		if ('CS' in idx) and ('CL' in idx):
			overlap.append(utt)
		elif ('NOISE' in idx):
			overlap.append(utt)
		else:
			non_overlap.append(utt)
	file.close()

	outfile = open(out_file, 'w')
	for utt in non_overlap:
		outfile.write(utt)
	outfile.close()

	outfile = open(overlap_file, 'w')
	for utt in overlap:
		outfile.write(utt)
	outfile.close()

	print(len(overlap))
	print(len(non_overlap))
