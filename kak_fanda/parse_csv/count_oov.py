import sys
import os
from ph4.parser import parse_lexicon_to_dict

if len(sys.argv) != 3:
	print("Usage: python count_oov.py <transcript> <lexicon>")
	sys.exit(1)

transcript_path = sys.argv[1]
lexicon_path = sys.argv[2]

if __name__ == "__main__":
	lexicon_dict = parse_lexicon_to_dict(lexicon_path)

	text = open(transcript_path).read().splitlines()
	try:
		text_test = []
		for line in text:
			text_test.append(line.strip().split(" ", 1)[1])
	except Exception as e:
		print(e, line)
	else:
		word_test = [word.strip() for line in text_test for word in line.strip().split()]
		# word_test = list(set(word_test))
		print(len(word_test))

		oov_counter = 0
		oov_arr = []
		for word in word_test:
			if word not in lexicon_dict and word not in oov_arr:
				oov_counter += 1
				oov_arr.append(word)

		for item in oov_arr:
			print(item)

		print(len(oov_arr))
