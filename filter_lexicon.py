# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Filter the current lexicon which not exist in the reference lexicon",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("curr_lex", type=str, metavar="The current lexicon")
    parser.add_argument("ref_lex", type=str, metavar="The reference lexicon")
    parser.add_argument("out_lex", type=str, metavar="The output lexicon")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.ref_lex, 'r')
	ref_tokens = []
	for pron in file:
		ref_tokens.append(pron.split()[0])
	file.close()

	file = open(args.curr_lex, 'r')
	filtered_prons = []
	for pron in file:
		token = pron.split()[0]
		if token not in ref_tokens:
			filtered_prons.append(pron)
	file.close()

	file = open(args.out_lex, 'w')
	for pron in filtered_prons:
		file.write(pron)
	file.close()

	print('Total lexicon which not exist in reference is ', len(filtered_prons))

