# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Remove the ID in each utterance",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", type=str, metavar="The input transcript path file")
    parser.add_argument("outfile", type=str, metavar="The output transcript w/o ID path file")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.infile, 'r')

	without_id = []
	for line in file:
		idx = line.split(' ')[0]
		temp = line.replace(idx, '').strip()
		without_id.append(temp)
	file.close()

	file = open(args.outfile, 'w')
	for line in without_id:
		file.write(line + '\n')
	file.close()