# Note: nama label track HARUS SAMA dengan nama folder audio wav

import re
import os
import sys
import locale
import argparse
from shutil import copyfile
from time import strftime
from time import gmtime
from random import randrange
from collections import OrderedDict

wav_ext = '.wav'
txt_ext = '.txt'
map_ext = '.map'


def parse_arguments():
	parser = argparse.ArgumentParser()

	# parser.add_argument("lexicon", help="Lexicon path/location.", type=str)
	parser.add_argument("label_track", help="Label track path/location.", type=str)

	args = parser.parse_args()

	return args

def adjust_path_separator(label_track_path):
	if "\\" in label_track_path:
		path_separator = "\\"
	else:
		path_separator = "/"

	return path_separator

def normalize_path(some_path):
	return some_path.replace(".\\", "")


def match_idx_to_utt(idx_utt, label_track_path):
	def proceed_0(num, max_length=4):
		num = str(num)
		return "0"*(max_length - len(num)) + num

	idx_utt_dict, audio_mapping, idx_ws_counter = OrderedDict(), {}, {}
	complete_idx_counter, idx_counter = {}, {}

	for item in idx_utt:
		idx = item[0]
		stripped_idx = idx.strip()
		if stripped_idx in complete_idx_counter:
			complete_idx_counter[stripped_idx] += 1
		else:
			complete_idx_counter[stripped_idx] = 1

		if idx[-1] != " ":
			if idx in idx_counter:
				idx_counter[stripped_idx] += 1
			else:
				idx_counter[stripped_idx] = 1

		lt_basename = os.path.basename(label_track_path).replace(txt_ext, "")
		new_idx = lt_basename + "_" + stripped_idx.upper() + "_" + proceed_0(complete_idx_counter[stripped_idx])

		if idx[-1] != " ":
			if idx_counter[idx] != 1:
				audio_mapping[idx + "-" + str(idx_counter[idx])] = new_idx
			else:
				audio_mapping[idx] = new_idx
		else:
			if idx not in idx_ws_counter:
				audio_mapping[idx] = new_idx
				idx_ws_counter[idx] = 1
			else:
				audio_mapping[idx + "-" + str(idx_ws_counter[stripped_idx])] = new_idx
				idx_ws_counter[idx] += 1

		idx_utt_dict[new_idx] = item[1]

	return idx_utt_dict, audio_mapping


def write_to_text(idx_utt_dict, text_path):
	file = open(text_path, 'w')
	for utt_idx in idx_utt_dict:
		line = utt_idx + ' ' + idx_utt_dict[utt_idx] + '\n'
		file.write(line)
	file.close()
	return

def write_to_audio_map(audio_mapping, mapping_path):
	with open(mapping_path, "w") as f:
		for i, j in sorted(audio_mapping.items()): f.write("{}\t{}\n".format(i, j))

if __name__ == "__main__":
	args = parse_arguments()
	path_separator = adjust_path_separator(args.label_track)
	label_track_path = normalize_path(args.label_track)

	if not os.path.isfile(label_track_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(label_track_path))
	
	items = []
	for line in open(label_track_path).read().splitlines():
		parts = line.split("\t")
		items.append(parts[-1])
	if len(items) % 2 != 0:
		print('\nJumlah baris dalam {} tidak genap. Perbaiki dulu sebelum melanjutkan.'.format(label_track_path))
		sys.exit(1)

	idx_list = items[:len(items)//2]
	utt_list = items[len(items)//2:]
	idx_utt = list(zip(idx_list, utt_list))
	idx_utt_dict, audio_mapping = match_idx_to_utt(idx_utt, label_track_path)

	text_path = label_track_path.replace(txt_ext, '_text'+ txt_ext)
	write_to_text(idx_utt_dict, text_path)

	mapping_path = label_track_path.replace(txt_ext, map_ext)
	write_to_audio_map(audio_mapping, mapping_path)