import sys
sys.path.append('/home/iftitakhul.zakiah/scripts/kak_fanda/parse_csv/ph4')

from ph4.audio import *
from ph4.utils import *
from ph4.parser import *
from ph4.writer import *
from ph4.lexicon import *
from ph4.transcript import *
import os
import argparse

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--eval", default=False, action='store_true', help="corpus_id/abbreviation")
	parser.add_argument("corpus_id", help="corpus_id/abbreviation", type=str)
	# parser.add_argument("csv_dir", help="csv path", type=str)
	parser.add_argument("csv_path", help="csv path", type=str)
	parser.add_argument("text_version", help="text version", type=str)
	# parser.add_argument("audio_version", help="audio version", type=str)
	# parser.add_argument("lexicon_master", help="lexicon master path", type=str)
	# parser.add_argument("typo_mapping", help="typo mapping path", type=str)

	args = parser.parse_args()

	return args

if __name__ == "__main__":
	args = parse_arguments()

	corpus_id = args.corpus_id.lower()
	# csv_dir_path = args.csv_dir
	text_version = args.text_version
	
	lexicon_master_path = "/home/iftitakhul.zakiah/speech-script/kak_fanda/parse_csv/resource/lexicon_master.txt"
	typo_mapping_path = "/home/iftitakhul.zakiah/speech-script/kak_fanda/parse_csv/resource/typo_mapping.txt"

	# csv_files = [file for file in os.listdir(csv_dir_path) if os.path.isfile(os.path.join(csv_dir_path, file))]
	# print(csv_files)

	# for curr_csv_path in csv_files:
	csv_path = args.csv_path
	# csv_path = csv_dir_path + '/' + curr_csv_path
	
	csv_basename = os.path.basename(csv_path)[:-4]

	lexicon_train_path = 'kaldi_kit/' + text_version + '/lexicon_train_' + corpus_id + '.txt'
	curr_project_path = os.path.dirname(csv_path).replace('arsip_pelabelan/'+ text_version + '/csv', '')
	curr_lexicon_path = curr_project_path + lexicon_train_path

	# lexicon_train_path = 'kaldi_kit/lexicon_train_' + corpus_id + '.txt'
	# curr_lexicon_path = lexicon_train_path
	print(curr_lexicon_path)

	if not os.path.isfile(curr_lexicon_path):
		open(curr_lexicon_path, 'a').close()

	# for path in ["text_train", "text_test"]:
	# 	if not os.path.isdir(path):
	# 		os.makedirs(path)

	eval_log = []
	print(csv_path)
	idx_to_cmps, skipped_idxs = parse_csv_to_per_idx(csv_path)
	lexicon_master = parse_lexicon_to_dict(lexicon_master_path)
	lexicon_train = parse_lexicon_train_to_dict(curr_lexicon_path, corpus_id)
	# for i, item in lexicon_train.items(): print(i, item)
	# print(len(lexicon_train.keys()))
	# print(skipped_idxs)
	typo_mapping = parse_typo_mapping(typo_mapping_path)
	# for i, j in typo_mapping.items(): print(i, j)
	# print(idx_to_cmps)
	# print()
	# print(lexicon_train)
	# print()
	# print(lexicon_master)
	# print()
	# print(typo_mapping)
	# print()
	# print(eval_log)
	lexicon_train, oov = get_lexicon_train(idx_to_cmps, lexicon_train, lexicon_master, typo_mapping, eval_log)
	if args.eval:
		with open("evaluasi/" + csv_basename[:2] + ".csv", "a") as f:
			for line in eval_log:
				f.write("{}\n".format(",".join([csv_basename] + list(line))))
	# # for i, j in lexicon_train.items(): print(i, j)
	# # print(len(lexicon_train.keys()))

	train_transcript = get_train_transcript(idx_to_cmps, lexicon_train, typo_mapping, corpus_id)
	# # for i, j in train_transcript.items(): print(i, j)
	text_train_path = csv_path.replace('.csv', '.txt').replace('arsip_pelabelan/' + text_version + '/csv/', \
			'kaldi_kit/' + text_version + '/text_train/')
	write_transcript_to_file(text_train_path, train_transcript)

	test_transcript = get_test_transcript(train_transcript, corpus_id)
	# for i, j in test_transcript.items(): print(i, j)
	# for i in oov: print(" ".join(i))
	text_test_path = csv_path.replace('.csv', '.txt').replace('arsip_pelabelan/' + text_version + '/csv/', \
			'kaldi_kit/' + text_version + '/text_test/')
	write_transcript_to_file(text_test_path, test_transcript)
	write_list_to_file('oov', oov, ' ')

	# wav_path = csv_path.replace('.csv', '').replace('arsip_pelabelan/csv/' + text_version, 'waves/' + args.audio_version)
	wav_path = csv_path.replace('.csv', '').replace('arsip_pelabelan/' + text_version + '/csv/', 'waves/')
	assert os.path.isdir(wav_path), "'%s' not found" % wav_path
	wavs = os.listdir(wav_path)
	check_lengths(test_transcript, wavs, skipped_idxs)

	lexicon_train = convert_lex_to_lol(lexicon_train, corpus_id)
	# for i in lexicon_train: print(i)
	write_list_to_file(curr_lexicon_path, lexicon_train, ' ', 'w')
