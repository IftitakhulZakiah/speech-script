# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description="Get content for each element in input",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("qa_csv", type=str, metavar="The sorted QA CSV file input with 3 columns, 'ID', 'Kata yang salah', and 'Perbaikan'")
    parser.add_argument("diff_file", type=str, metavar="The diff file format")
    # parser.add_argument("per_utt", type=str, metavar="The per_utt format with 'hyp' as before version and 'ref' as after version")
    # parser.add_argument("output", type=str, metavar="The text output file")
    
    return parser.parse_args()

def read_per_utt(filename):
	i = 1
	bef_aft_objs = {} # the before after objects
	curr_obj = {}

	file = open(filename, 'r')
	for line in file:
		curr_id = line.split()[0]
		if i % 4 == 1:
			curr_obj['ref'] = line.replace(curr_id + ' ref', '').strip()
		elif i % 4 == 2:
			curr_obj['hyp'] = line.replace(curr_id + ' hyp', '').strip()
		elif i % 4== 3:
			curr_obj['op'] = line.replace(curr_id + ' op', '').strip()
		else:
			curr_obj['csid'] = line.replace(curr_id + ' #csid', '').strip()
			bef_aft_objs[curr_id] = curr_obj
			curr_obj = {}
		i += 1

	file.close()

	return bef_aft_objs

def get_indexes(elmt, curr_list):
	idxs = []
	try:
		idxs = [i for i, token in enumerate(curr_list) if token == elmt]	
	except:
		pass
	return idxs

# def read_diff_file(filename):
# 	file = open(filename, 'r')
	# diff = {}
	# for line in file:
	# 	diff_key = diff.keys()
	# 	temp = line.split('|').strip()

	# 	if temp[0] in diff_key:
	# 		diff[temp[0]]['before'].append(temp[1])
	# 		diff[temp[0]]['after'].append(temp[2])
	# 	else:
	# 		diff[temp[0]] = {'before': [temp[1]], 
	# 						'after' : [temp[2]]}

	return diff

if __name__ == '__main__':
	args = get_args()
	qa_results = pd.read_csv(args.qa_csv)
	diff = pd.read_csv(args.diff_file)
	# print(qa_results['ID'][0])
	# print(qa_results.iloc[0]['ID'])

	# bef_aft_objs = read_per_utt(args.per_utt)
	# diff = read_diff_file(args.diff_file)

	for i in range(len(qa_results)):
		curr_id = qa_results.iloc[i]['ID']
		curr_bef = qa_results.iloc[i]['Kata yang salah']
		curr_aft = qa_results.iloc[i]['Perbaikan']

		# curr_obj = bef_aft_objs[curr_id]
		# curr_hyp = curr_obj['hyp'].split().strip()
		# curr_ref = curr_obj['ref'].split().strip()

		# idxs_hyp = get_indexes(curr_bef, curr_hyp)
		# idxs_ref = get_indexes(curr_aft, curr_ref)

		# for j in range(len(idxs_hyp)):
		# 	id_hyp = idxs_hyp[j]
		# 	id_ref = idxs_ref[j]
		#############################################	
		# diff_bef = diff[curr_id]['before']
		# diff_aft = diff[curr_id]['after']

		# idxs_hyp = get_indexes(curr_bef, diff_bef)
		# idxs_ref = get_indexes(curr_aft, diff_aft)

		
		for 
		if curr_bef == diff_bef