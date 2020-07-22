from ph4.utils import *
import sys
import os

def get_word_and_pron(idx, parts, eval_log=[]):
	parts = strip_elmts(parts)
	parts = normalize(parts)

	word = parts[0]
	pron = parts[1]

	if parts[3] != "" and parts[4] != "": # salah kata
		word = parts[3]
		pron = parts[4]
	elif parts[3] != "" and parts[4] == "" and parts[2] != "<repetisi>":
		if ' ' not in parts[3] and parts[3].strip().split()[-1] not in allowed_phones: # bentuk baku
			word = parts[3] # perbaikan kata
		elif parts[3].strip().split()[-1] in allowed_phones:
			pron = parts[3] # salah lafal

	if parts[2] == "<filler>":
		word = "<filler>"

	if word == "<?>":
		word = "<unk>"

	if word == "<unk>":
		pron = "<noise>"

	if word in unchanged_word:
		pron = word

	if "=" in word or "=" in pron:
		if "=" not in word or "=" not in pron:
			eval_log.append(idx, word, pron)
			print("get_train_transcript: Wrong format {} {}".format(idx, " ".join(parts)))

	if "<" in word or ">" in word:
		if "<" not in word or ">" not in word:
			print("[ERROR] " + idx + " " + word)
			eval_log.append(idx, word)
			print("get_train_transcript: Wrong word format {} {}".format(idx, word))

	if "-" in word and len(word.strip().split("-")) == 2:
		items = word.strip().split("-")
		if items[0] == items[1]:
			print("[ERROR] " + idx + " " + word)
			eval_log.append(idx, word)
			print("get_train_transcript: Wrong word format {} {}".format(idx, word))

	if " " in word:
		eval_log.append((idx, "ada spasi di dalam kata? " + word))
		print("get_train_transcript: Wrong word format {} {}".format(idx, word))

	words = word.split('=')
	words = clean_word(words)
	prons = pron.split('=')

	return words, prons, parts

def get_lexicon_train(idx_to_cmps, lexicon_train, lexicon_master, typo_mapping, eval_log):
	def _normalize_pron(pron):
		pron = ' '.join(pron.strip().split())
		return pron

	oov = []
	for idx, cmps in idx_to_cmps.items():
		for parts in cmps:
			
			words, prons, parts = get_word_and_pron(idx, parts, eval_log)

			for i, word in enumerate(words):
				if word not in deleted_tags:
					pron = _normalize_pron(prons[i])
					pron = pron.replace("ow", "o w").replace("oy", "o y").replace("ey", "e y").replace("ew", "e w").replace("kh", "k")
					for char in pron:
						if char not in pron:
							print("{}: {} pron is wrong..".format(idx, pron))

					try:
						assert_pron(idx, pron)
					except Exception as e:
						print(e)

					if word in typo_mapping:
						new_word = typo_mapping[word]
						eval_log.append((idx, word, new_word))
						if " " in new_word:
							print("get_lexicon_train: word {} {} is wrong, but cannot be automatically corrected. \
								Please correct it manually..".format(idx, word))
						word = new_word

					if word not in lexicon_master and ("<" not in word and "<" not in parts[0] and parts[2] != "<email>"):
						if not (parts[3] != "" and parts[4] == "" and word == parts[3]):
							oov.append([word, pron, idx])

					if word not in lexicon_train:
						lexicon_train[word] = {}
						lexicon_train[word][pron] = 1
					else:
						if pron not in lexicon_train[word]:
							# add pron to existing list
							idxs = sorted(list(lexicon_train[word].values()))

							prev_prons = list(lexicon_train[word].keys())
							prev_idx = idxs[-1]

							curr_idx = prev_idx + 1
							lexicon_train[word][pron] = curr_idx

	return lexicon_train, oov

def convert_lex_to_lol(lexicon_train, corpus_id):
	lexicon_list = []
	for word in lexicon_train:
		for pron in lexicon_train[word]:
			idx = lexicon_train[word][pron]
			new_word = word + "_" + corpus_id + str(idx)

			lexicon_list.append([new_word, pron])
	return lexicon_list

# this script is dedicated to handle the lexicon, i.e. extract salah_lafal, extract salah_eja
# def get_saltik(idx_to_cmps):
# 	saltik_entries = []
# 	for idx in idx_to_cmps:
# 		cmps = idx_to_cmps[idx]
# 		# for cmps in values:
# 		for entry in cmps:
# 			entry = clean_word(entry)
# 			entry = strip_elmts(entry)
# 			if entry[3] != '' and entry[4] != '':
# 				del entry[2]
# 				cleaned_entry = remove_empty_elmts(entry)
# 				if cleaned_entry not in saltik_entries:
# 					cleaned_entry.append(idx)
# 					saltik_entries.append(cleaned_entry)

# 	return saltik_entries

# def get_salfal(idx_to_cmps):
# 	salfal_entries = []
# 	for idx in idx_to_cmps:
# 		cmps = idx_to_cmps[idx]
# 		# for cmps in values:
# 		for entry in cmps:
# 			entry = clean_word(entry)
# 			entry = strip_elmts(entry)
# 			if entry[3] != '' and entry[4] == '':
# 				if entry[3] not in edit_tags and entry[3].strip().split(" ")[0] in allowed_phones:
# 					del entry[2]
# 					cleaned_entry = remove_empty_elmts(entry)
# 					if cleaned_entry not in salfal_entries:
# 						if entry[1] != entry[2]:
# 							cleaned_entry.append(idx)
# 							salfal_entries.append(cleaned_entry)

# 	return salfal_entries

# def get_repetisi(idx_to_cmps):
# 	repetisi_entries = []
# 	for idx in idx_to_cmps:
# 		cmps = idx_to_cmps[idx]
# 		# for cmps in values:
# 		for entry in cmps:
# 			entry = clean_word(entry)
# 			entry = strip_elmts(entry)
# 			if entry[2] == '<repetisi>' and entry[3] != '<hapus>':
# 				if entry[3] != '' and entry[4] != '':
# 					entry[0] = entry[3] # change old_word to new_word
# 					entry[1] = entry[4] # change old_pron to new_pron
# 				elif entry[3] != '' and entry[4] == '':
# 					if entry[3].strip().split(" ")[0] in allowed_phones:
# 						entry[1] = entry[3]	# change old_pron to new_pron

# 				if [entry[0], entry[1]] not in repetisi_entries:
# 					repetisi_entries.append([entry[0], entry[1], idx])

# 	return repetisi_entries

# def get_filler(idx_to_cmps):
# 	filler_entries = []
# 	for idx in idx_to_cmps:
# 		cmps = idx_to_cmps[idx]
# 		# for cmps in values:
# 		for entry in cmps:
# 			entry = clean_word(entry)
# 			entry = strip_elmts(entry)
# 			if entry[2] == '<filler>' and entry[3] != '<hapus>':
# 				if entry[3] != '' and entry[4] != '':
# 					entry[0] = entry[3] # change old_word to new_word
# 					entry[1] = entry[4] # change old_pron to new_pron
# 				elif entry[3] != '' and entry[4] == '':
# 					if entry[3].strip().split(" ")[0] in allowed_phones:
# 						entry[1] = entry[3]	# change old_pron to new_pron

# 				if [entry[0], entry[1]] not in filler_entries:
# 					filler_entries.append([entry[0], entry[1], idx])

# 	return filler_entries

# def get_daerah(idx_to_cmps):
# 	daerah_entries = []
# 	for idx in idx_to_cmps:
# 		cmps = idx_to_cmps[idx]
# 		# for cmps in values:
# 		for entry in cmps:
# 			entry = clean_word(entry)
# 			entry = strip_elmts(entry)
# 			if entry[2] == '<daerah>' and entry[3] != '<hapus>':
# 				if entry[3] != '' and entry[4] != '':
# 					entry[0] = entry[3] # change old_word to new_word
# 					entry[1] = entry[4] # change old_pron to new_pron
# 				elif entry[3] != '' and entry[4] == '':
# 					if entry[3].strip().split(" ")[0] in allowed_phones:
# 						entry[1] = entry[3]	# change old_pron to new_pron

# 				if [entry[0], entry[1]] not in daerah_entries:
# 					daerah_entries.append([entry[0], entry[1], idx])

# 	return daerah_entries
