# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Sort descending based on WER",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", type=str, metavar="input file : using the output from csid.py format")
    parser.add_argument("outfile", type=str, metavar="output file")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.infile, 'r')
	utts = []
	wer = []
	i = 0
	for utt in file:
		if i > 0:
			utts.append(utt)
			wer.append(float(utt.split(',')[0]))
		i += 1
	file.close()

	results = sorted(zip(wer,utts), reverse=True)
	outfile = open(args.outfile, 'w')
	sorted_utts = []
	for result in results:
		curr = result[1].split(',')
		hyp = curr[6]
		ref = curr[7]
		outfile.write(result[1].replace( ',' + hyp + ',' + ref, ',' + ' ref' + hyp) + '\n')
		outfile.write(result[1].replace(hyp + ',', ' hyp'))
	outfile.close()