# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Get the unique wordlist from text",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", type=str, metavar="The text path file")
    parser.add_argument("outfile", type=str, metavar="The wordlist path file")
    parser.add_argument("--is_transcript", type=bool, metavar="Is the infile transcript formatted?")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.infile, 'r')
	all_text = ''
	for line in file:
		if (args.is_transcript == 1):
			idx = line.split()[0] # get the id audio
			text = line.replace(idx, '').strip() + ' '
		else:
			text = line + ' '
		all_text += text
	file.close()
	
	tokens = all_text.split()
	unique_tokens = set(tokens)
	sorted_tokens = sorted(unique_tokens)

	file = open(args.outfile, 'w')
	for token in sorted_tokens:
		file.write(token + '\n')
	file.close()

	print("Total unique tokens " + str(len(sorted_tokens)))

