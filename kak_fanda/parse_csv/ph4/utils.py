edit_tags = ["<hapus>", "<sisip>"]

deleted_tags = ['<napas>']

allowed_phones = ['a', 'aw', 'ay', 'b', 'c', 'd', 'e', 'eu', '@', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ng', 'ny', 
	'o', 'p', 'r', 's', 'sy', 't', 'u', 'w', 'y', 'z', "'", "<noise>", "<decak>", "<desis>", "<ketawa>", "<sil>", "<batuk>"]

unchanged_word = ['<napas>', '<overlap>', '<op>', '<dering>', '<decak>', '<batuk>', '<desis>', '<ketawa>']

def clean_word(_list):
	def _complete_bracket(word):
		if word:
			if word[0] == "<" and word[-1] != ">":
				if word[-1].isalpha():
					word += ">"
				elif word[-1] == "<":
					word[-1] = ">"
			if word[-1] == ">" and word[0] != "<":
				if word[0].isalpha():
					word = "<" + word
				elif word[0] == ">":
					word[0] = "<"
		return word

	_list = [item.replace(']', '').replace('[', '') for item in _list]
	_list = [_complete_bracket(item) for item in _list]
	return _list

def strip_elmts(_list):
	return [item.strip() for item in _list]

def remove_empty_elmts(_list):
	return list(filter(None, _list))

def pad_with_empty_string(_list, target_len=6):
	return _list[:target_len] + ['']*(target_len - len(_list))

def normalize(_list):
	return [item.replace("'@", "@").lower() for item in _list]

def assert_pron(idx, pron):
	if pron and pron not in unchanged_word:
		for item in pron.strip().split():
			if item not in allowed_phones:
				raise Exception("Pronunciation {} in {} seems not right".format(pron, idx))