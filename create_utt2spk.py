# python create_utt2spk.py <text_file> <out_file> <digit_id>
# e.g. python create_utt2spk.py text.txt utt2spk 5
import sys
import os
import re


if __name__ == '__main__':
	in_file = sys.argv[1]
	out_file = sys.argv[2]
	# digit_id = int(sys.argv[3])
	id_regex = sys.argv[3]

	utterances = []
	temp_file = open(in_file, 'r')
	for utt in temp_file:
		id_utt = utt.split()[0]
		# utterances.append(id_utt + ' ' + id_utt[:digit_id] + '\n')
		spk_id = re.search(id_regex, id_utt).group()
		utterances.append(id_utt + ' ' + spk_id + '\n')

	temp_file.close()

	utterances.sort()
	print("[INFO] Jumlah utterance pada utt2spk ", len(utterances))
	temp_file = open(out_file, 'w')
	for utt in utterances:
		temp_file.write(utt)
	temp_file.close()
