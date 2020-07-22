# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Filter the hyp from per_utt file",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", type=str, metavar="input file : using per_utt from decode Kaldi")
    parser.add_argument("outfile", type=str, metavar="output file")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.infile, 'r')
	hyps = []
	i = 0 
	for line in file:
		if (i % 4) == 1:
			idx = line.split()[0]
			temp = line.replace(idx + ' ' + 'hyp ', idx)
			temp = temp.replace('***', '')
			hyps.append(temp)
		i += 1
	
	outfile = open(args.outfile, 'w')
	for hyp in hyps:
		outfile.write(hyp)
	outfile.close()
	print(hyps)