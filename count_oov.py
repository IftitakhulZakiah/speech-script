# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Count the OOV words over the input text ",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", type=str, metavar="input text file")
    parser.add_argument("output", type=str, metavar="the oov tokens")
    parser.add_argument("lexicon", type=str, metavar="lexicon comparison")
    parser.add_argument("is_transcript", type=bool, metavar="is the input text used transcript format?")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.lexicon, 'r')
	lexicon_tokens = []
	for lexicon in file:
		lexicon_tokens.append(lexicon.split()[0])
	file.close()

	file = open(args.input, 'r')
	oov_tokens = []
	n_oov = 0
	n_tokens = 0
	for sent in file:
		tokens = sent.split()
		if args.is_transcript:
			tokens = tokens[1:] # exclude the utterance ID
		for token in tokens:
			n_tokens += 1
			if token not in lexicon_tokens:
				oov_tokens.append(token)
				n_oov += 1
	file.close()

	# sort_oov_tokens = oov_tokens.sort()
	# print(sort_oov_tokens)
	print(oov_tokens)
	file = open(args.output, 'w')
	for token in oov_tokens:
		file.write(token + '\n')
	file.close()

	print("Total OOV " + str(n_oov) + " dari " + str(n_tokens) + " kata")
	