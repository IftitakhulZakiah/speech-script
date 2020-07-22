# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(description="Get the lexicon based from wordlist",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("wordlist", type=str, metavar="The list of words")
    parser.add_argument("lexicon", type=str, metavar="The reference lexicon")
    parser.add_argument("out_lex", type=str, metavar="The output lexicon")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.wordlist, 'r')
	wordlist = []
	for word in file:
		wordlist.append(word.strip())
	file.close()

	file = open(args.lexicon, 'r')
	reff_lex = {}
	for lex in file:
		curr_word = lex.split()[0]
		temp_words = reff_lex.keys()
		if curr_word in temp_words:
			reff_lex[curr_word].append(re.sub(r'^' + curr_word + ' ', '', lex))
		else:
			reff_lex[curr_word] = [re.sub(r'^' + curr_word + ' ', '', lex)]
	file.close()

	lexicon = {}
	reff_words = reff_lex.keys()
	n_oov = 0
	n_word = 0
	for word in wordlist:
		if word in reff_words:
			lexicon[word] = reff_lex[word]
			n_word += 1
		else:
			n_oov += 1
			continue
	
	file = open(args.out_lex, 'w')
	for lex in lexicon:
		for pron in lexicon[lex]:
			file.write(lex + ' ' + pron)
	file.close()

	print("[INFO] Total words that exist in the lexicon ", n_word)
	print("[INFO] Total OOV ", n_oov)