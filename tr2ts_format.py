# Convert from 
# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Convert train to test text format",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", type=str, metavar="input file : Kaldi text format")
    parser.add_argument("outfile", type=str, metavar="output file : Kaldi text format w/o suffix in each words")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.infile, 'r')
	utts = []
	for line in file:
		tokens = line.split()
		utt = tokens[0] + " "
		for token in tokens:
			if token != tokens[0]:
				curr_token = token.split('_')[0]
				utt = utt + curr_token + " "
		utts.append(utt)
		print(utt)

	outfile = open(args.outfile, 'w')
	for utt in utts:
		outfile.write(utt + '\n')
	outfile.close()

	print('Total utterance : ', len(utts))