from ph4.utils import *
import inspect
import sys
import os
import re

def parse_csv_to_per_idx(csv_path):
	idx = ''
	idx_to_cmps = {}
	skipped_idxs = []
	skip = False
	lines = open(csv_path, encoding='utf-8').read().splitlines()
	for line in lines[1:]:
		if ';' in line:
			delimiter = ';'
		elif ',' in line:
			delimiter = ','

		parts = line.strip().split(delimiter)
		parts = strip_elmts(parts)
		parts = pad_with_empty_string(parts)

		if parts[0] != '' and parts[0].lower() not in edit_tags:
			idx = parts[0].strip().upper()
			if "NOISE" not in parts[0] and ("<op>" not in parts[1] and "overlap" not in parts[1]):
				skip = False
				if idx not in idx_to_cmps:
					idx_to_cmps[idx] = []
			else:
				skip = True
				if ("<op>" in parts[1] or "overlap" in parts[1]) or "NOISE" in parts[0].upper():
					skipped_idxs.append(idx)
		elif parts[0] != "<hapus>" and parts[1] != "" and not skip:
			if parts[1] == "<overlap>":
				del idx_to_cmps[idx]
				continue

			idx_to_cmps[idx].append(normalize(parts[1:]))

	return idx_to_cmps, skipped_idxs

def parse_lexicon_to_dict(lexicon_path):
	lexicon_dict = {}

	entries = open(lexicon_path).read().splitlines()
	for entry in entries:
		parts = entry.strip().split(' ', 1)
		if len(parts) == 2:
			word = parts[0]
			pron = parts[1]
			if word not in lexicon_dict:
				lexicon_dict[word] = [pron]
			else:
				lexicon_dict[word].append(pron)
		else:
			print("parse_lexicon_to_dict: error entry {}".format(entry))
			sys.exit(1)

	return lexicon_dict

def parse_typo_mapping(typo_mapping_path):
	typo_dict = {}

	entries = open(typo_mapping_path)
	for entry in entries:
		parts = entry.strip().split("\t", 1)
		parts = strip_elmts(parts)
		parts = normalize(parts)
		if len(parts) == 2:
			old_word = parts[0]
			new_word = parts[1]
			typo_dict[old_word] = new_word
		else:
			print("parse_typo_mapping: error entry {}".format(entry))
			sys.exit(1)

	return typo_dict

def parse_lexicon_train_to_dict(lexicon_path, corpus_id):
	def _get_base_word(word):
		delimiter = "_" + corpus_id
		return word.strip().split(delimiter)

	lexicon_dict = {}
	entries = open(lexicon_path).read().splitlines()
	if entries:
		for entry in entries:
			parts = entry.strip().split(' ', 1)

			if len(parts) == 2:
				word = parts[0]
				pron = parts[1]
				base_word = _get_base_word(word)
				if base_word is not None:
					if len(base_word) == 2:
						if base_word[0] not in lexicon_dict:
							lexicon_dict[base_word[0]] = {}
						lexicon_dict[base_word[0]][pron] = int(base_word[1])
				else:
					print("Something wrong with this entries {}...".format(entry))
					sys.exit(1)

	return lexicon_dict
	