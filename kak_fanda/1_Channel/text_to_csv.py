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

list_filler = ['<a>', '<ah>', '<aah>', '<eh>', '<euh>', '<ehem>', '<eheh>', '<em>', '<en>', '<e>', '<eb>', '<ed>', 
				'<eeh>', '<eem>', '<eg>', '<ek>', '<eng>', '<ep>', '<et>', '<ey>', '<ey>', '<heeh>', '<heueuh>', 
				'<hee>', '<heem>', '<hem>', '<he>', '<heh>', '<hu>', '<ih>', '<oh>', '<oh>', '<uh>']

chars_set = ['-', '<', '>', '.', '_', "'"]

# Indonesian letters
huruf = {
	'a': 'a',
	'b': 'b e',
	'c': 'c e',
	'd': 'd e',
	'e': 'e',
	'f': 'e f',
	'g': 'g e',
	'h': 'h a',
	'i': 'i',
	'j': 'j e',
	'k': 'k a',
	'l': 'e l',
	'm': 'e m',
	'n': 'e n',
	'o': 'o',
	'p': 'p e',
	'q': 'k i',
	'r': 'e r',
	's': 'e s',
	't': 't e',
	'u': 'u',
	'v': 'v e',
	'w': 'w e',
	'x': 'e k s',
	'y': 'y e',
	'z': 'z e t'
}

# interactions between a letter and its successor in a word
token_interactions = {
	'a': ['i', 'u'],
	'k': ['h'],
	'n': ['g', 'y'],
	'o': ['i'],
	's': ['y']
}

diphtong_transition = {
	'i': 'y',
	'u': 'w',
}

unchanged_word = ['<napas>', '<overlap>', '<op>', '<dering>', '<decak>', '<batuk>', '<desis>', '<ketawa>']

unk_tag = "<unk>"

wav_ext = '.wav'
txt_ext = '.txt'
csv_ext = '.csv'
map_ext = '.map'


def parse_arguments():
	parser = argparse.ArgumentParser()

	parser.add_argument("lexicon", help="Lexicon path/location.", type=str)
	parser.add_argument("typo_mapping", help="Typo mapping path/location.", type=str)
	parser.add_argument("text", help="Transcript track path/location.", type=str)

	args = parser.parse_args()

	return args

def adjust_path_separator(lexicon_path, label_track_path):
	if "\\" in lexicon_path or "\\" in label_track_path:
		path_separator = "\\"
	else:
		path_separator = "/"

	return path_separator

def normalize_path(some_path):
	return some_path.replace(".\\", "")

def parse_lexicon(lexicon_path):
	lexicon = {}

	entries = open(lexicon_path).read().splitlines()
	for entry in entries:
		parts = entry.strip().split(' ', 1)
		word = parts[0]
		pron = parts[1]

		if word in lexicon:
			lexicon[word].append(pron)
		else:
			lexicon[word] = [pron]

	return lexicon

def parse_typo_mapping(tm_path):
	typo_mapping = {}
	text = open(tm_path).read().splitlines()
	for line in text:
		parts = line.strip().split("\t")
		typo_mapping[parts[0]] = parts[1]
	return typo_mapping

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

def generate_fonem(word):
	if len(word) == 1:
		try:
			return huruf[word]
		except:
			return word

	if word == "<?>":
		word = "<unk>"

	if word == "<unk>":
		return "<noise>"
	
	phonemes = []
	skip = False
	for i in range(len(word)):
		char = word[i]
		if skip:
			skip = False
			continue

		if char in token_interactions and i < len(word) - 1 and word[i + 1] in token_interactions[char]:
			skip = True
			if word[i + 1] == 'i' or word[i + 1] == 'u':
				phonemes.append(char + diphtong_transition[word[i + 1]])
			else:
				phonemes.append(char + word[i + 1])
		elif char == 'v':
			phonemes.append('f')
		elif char == 'x':
			phonemes.extend(['k', 's'])
		elif char == 'q':
			phonemes.append('k')
		else:
			phonemes.append(char)

	phonemes = ' '.join(phonemes).replace('< ', '').replace(' >', '').replace(' - ', ' ')

	return phonemes

def write_to_csv(idx_utt_dict, lexicon, csv_path):
	def check_transcript(idx_utt_dict):
		wrong_words = []
		for utt_idx in idx_utt_dict:
			for idx, word in enumerate(idx_utt_dict[utt_idx].strip().split()):
				if any(c not in chars_set for c in word if not c.isalnum()):
					# check char yang tidak sesuai
					wrong_words.append([utt_idx, word])

				if "<" in word or ">" in word:
					# check penggunaan "<" dan ">"
					if "<" not in word or ">" not in word:
						wrong_words.append([utt_idx, word])

		if wrong_words:
			print("\n!! Perbaiki dulu kata di bawah ini sebelum melanjutkan pembuatan csv")
			for item in wrong_words:
				print(" ".join(item))
			sys.exit(1)

	def normalize_transcript(idx_utt_dict):
		print('')
		flag = False
		for utt_idx in idx_utt_dict:
			words = idx_utt_dict[utt_idx].strip().split()
			for idx, word in enumerate(words):
				if "-" in word and len(word.strip().split("-")) == 2:
					# check penggunaan "-" yang benar
					items = word.strip().split("-")
					if items[0] == items[1]:
						new_word = " ".join(items)
						print("Mengganti kata '{}' ke '{}' karena kata depan dan belakang sama".format(word, new_word))
						flag = True
						words[idx] = new_word

				if any(c.isupper() for c in word):
					# check upper case
					new_word = word.lower()
					print("Mengganti kata '{}' ke '{}' karena mengandung huruf kapital".format(word, new_word))
					flag = True
					words[idx] = new_word

				temp = " ".join(words)
				words = temp.strip().split()

			idx_utt_dict[utt_idx] = words

		if not flag:
			print("Mantap! Sudah tidak ada pembetulan format.. Mangga dilanjutkan ^^")

	def get_delimiter():
		delimiter = ""
		locale.setlocale(locale.LC_ALL, '')
		dec_pt_chr = locale.localeconv()['decimal_point']
		if dec_pt_chr == ",":
			delimiter = ";"
		else:
			delimiter = ","

		return delimiter

	delimiter = get_delimiter()

	with open(csv_path, 'w') as f:
		f.write('{}\n'.format(delimiter.join(['Id', 'Transkrip/Kata', 'Lafal', 'Emosi/Bentuk Konsisten'])))
		check_transcript(idx_utt_dict)
		normalize_transcript(idx_utt_dict)
		for idx in idx_utt_dict:
			f.write('{}\n'.format(delimiter.join([idx, " ".join(idx_utt_dict[idx])])))
			for word in idx_utt_dict[idx]:
				consistent_form = ''
				if word in list_filler:
					consistent_form = '<filler>'

				pron = ""
				if word == unk_tag:
					pron = "<noise>"
				elif word in unchanged_word:
					pron = word
				elif word in lexicon:
					if len(lexicon[word]) > 1:
						rand_pron = randrange(len(lexicon[word]))
						pron = lexicon[word][rand_pron]
					else:
						pron = lexicon[word][0]
				else:
					pron = generate_fonem(word)
				f.write('{}\n'.format(delimiter.join(['', word, pron, consistent_form])))

			f.write('\n')
	print('\nCSV baru disimpan sebagai {}'.format(csv_path))

def write_to_audio_map(audio_mapping, mapping_path):
	with open(mapping_path, "w") as f:
		for i, j in sorted(audio_mapping.items()): f.write("{}\t{}\n".format(i, j))

if __name__ == "__main__":
	args = parse_arguments()
	path_separator = adjust_path_separator(args.lexicon, args.text)

	lexicon_path = normalize_path(args.lexicon)
	text_path = normalize_path(args.text)
	tm_path = normalize_path(args.typo_mapping)

	if not os.path.isfile(lexicon_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(lexicon_path))

	if not os.path.isfile(tm_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(tm_path))

	if not os.path.isfile(text_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(label_track_path))

	lexicon = parse_lexicon(lexicon_path)

	typo_mapping = parse_typo_mapping(tm_path)

	idx_utt_dict = OrderedDict()
	text = open(text_path).read().splitlines()
	for idx, line in enumerate(text):
		line = line.strip().split()
		new_line = []
		for word in line:
			if word in typo_mapping:
				new_line.append(typo_mapping[word])
			else:
				new_line.append(word)
		line = " ".join(new_line)
		parts = line.strip().split(" ", 1)
		if len(parts) < 2:
			print("Line {}: Baris bermasalah/transkrip kosong '{}'".format(idx, line))
			parts.append("dummy")
		else:
			idx_utt_dict[parts[0]] = parts[1]

	if text_path.endswith(txt_ext):
		csv_path = text_path.replace(txt_ext, csv_ext)
	else:
		csv_path = text_path + csv_ext
	if os.path.isfile(csv_path):
		csv_bak = csv_path + ".bak"
		copyfile(csv_path, csv_bak)
		print("\nSebagai backup, file CSV lama disimpan sebagai {}".format(csv_bak))
	write_to_csv(idx_utt_dict, lexicon, csv_path)
