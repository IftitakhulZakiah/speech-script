# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Comparing the previous and current version of text",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("per_utt", type=str, metavar="Per_utt format with the prev version as hyp and current version as ref ")
    parser.add_argument("out_text", type=str, metavar="The output diff text")
    
    return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	file = open(args.per_utt, 'r')

	diff_utts = {}
	i = 1
	curr_ref, curr_hyp, curr_ops = '', '', ''
	
	for utt in file:
		if i % 4 == 1:
			curr_ref = utt
		elif i % 4 == 2:
			curr_hyp = utt
		elif i % 4 == 3:
			curr_ops = utt
		elif i % 4 == 0:
			tokens = utt.split()
			if (int(tokens[3]) != 0) or (int(tokens[4]) != 0) or (int(tokens[5]) != 0):
				ops = curr_ops.split()
				ref = curr_ref.split()
				hyp = curr_hyp.split() 
				for j in range(2, len(ops)):
					if ops[j].strip() != 'C':
						temp_idxs = diff_utts.keys()

						text = "{},{}".format(hyp[j], ref[j])
						if tokens[0] in temp_idxs:
							diff_utts[tokens[0]].append(text)
						else: 
							diff_utts[tokens[0]] = [text]
		i += 1
	file.close()
	
	file = open(args.out_text, 'w')
	idxs = diff_utts.keys()
	file.write("ID,Before,After\n")
	for idx in idxs:
		# file.write(idx + '\n')
		temp = diff_utts[idx]
		for diff in temp:
			file.write("{},{}\n".format(idx,diff))
		# file.write('\n')
	file.close()

	print("[INFO] The difference before after version already written on {}".format(args.out_text))
