from ph4.utils import *
from ph4.lexicon import *
import sys
import os

def get_test_transcript(train_transcript, corpus_id):
	test_transcript = {}
	for idx, utt in train_transcript.items():
		new_utt = []
		for word in utt.strip().split():
			word = word.strip().split("_" + corpus_id)[0]
			new_utt.append(word)

		test_transcript[idx] = " ".join(new_utt)

	return test_transcript

def get_train_transcript(idx_to_cmps, lexicon_train, typo_mapping, corpus_id):
	def _normalize_pron(pron):
		pron = ' '.join(pron.strip().split())
		return pron

	def _transform_idx(num):
		return str(num)

	utt_per_id = {}
	for idx in idx_to_cmps:
		utt = []
		for parts in idx_to_cmps[idx]:

			words, prons, parts = get_word_and_pron(idx, parts)

			for i, word in enumerate(words):
				if word not in deleted_tags:
					pron = _normalize_pron(prons[i].strip())
					pron = pron.replace("ow", "o w").replace("oy", "o y").replace("ey", "e y").replace("ew", "e w").replace("kh", "k")
					if word in typo_mapping:
						word = typo_mapping[word]

					word = word + "_" + corpus_id + _transform_idx(lexicon_train[word][pron])
					utt.append(word)

		utt_per_id[idx] = ' '.join(utt)

	return utt_per_id