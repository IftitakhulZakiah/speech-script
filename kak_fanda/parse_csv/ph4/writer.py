import sys
import os

def write_list_to_file(file_path, _list, delimiter='|', overwrite='a'):
	# input 	: list of list
	with open(file_path, overwrite) as f:
		for entry in _list:
			if entry[0] != '' and entry[0] != ' ':
				f.write('{}\n'.format(delimiter.join(entry)))

def write_transcript_to_file(file_path, _dict, delimiter=' '):
	with open(file_path, 'w') as f:
		for idx in _dict:
			f.write('{}\n'.format(delimiter.join([idx.upper(), _dict[idx]])))

def write_lexicon_dict_tofile(file_path, lexicon_dict):
	with open(file_path, 'w') as f:
		for entry in lexicon_dict:
			prons = list(set(lexicon_dict[entry]))
			for pron in prons:
				f.write('{} {}\n'.format(entry, pron))