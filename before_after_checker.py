# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description="Get content for each element in input",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("qa_csv", type=str, metavar="The sorted QA CSV file input with 3 columns, 'ID', 'Kata yang salah', and 'Perbaikan'")
    parser.add_argument("diff_file", type=str, metavar="The diff CSV file input with 3 columns, 'ID', 'Before', and 'After'")
    parser.add_argument("output", type=str, metavar="The text output file")
    # parser.add_argument("per_utt", type=str, metavar="The per_utt format with 'hyp' as before version and 'ref' as after version")
    
    
    return parser.parse_args()

def get_match_before(row_df_qa, df_diff):
	""" 
	Get the match row in df_diff based on "ID" and "Kata yang salah" from row_df_qa.
	:param row_df_qa: row of QA dataframe.
	:param df_diff: diff dataframe.
	:return: list of index(int) on df_diff and list of boolean
	"""
	idxs = []
	are_correct = []
	for i in range(len(df_diff)):
		if df_diff.iloc[i]['ID'] == row_df_qa['ID']:
			if df_diff.iloc[i]['Before'] == row_df_qa['Kata yang salah']:
				idxs.append(i)
				are_correct.extend([1] if df_diff.iloc[i]['After'] == row_df_qa['Perbaikan'] else [0])

	return idxs, are_correct


if __name__ == '__main__':
	args = get_args()
	qa_logs = pd.read_csv(args.qa_csv)
	df_diff = pd.read_csv(args.diff_file)

	correct_correction = {}
	incorrect_correction = {}

	with open(args.output, 'a') as f:
		for i in range(len(qa_logs)):
			curr_row = qa_logs.iloc[i]
			idxs, are_correct = get_match_before(curr_row, df_diff)

			for j in range(len(are_correct)):
				if are_correct[j] == 0:
					f.write("Incorrect correction ({}). In QA logs : {}, but in new version : {}. Please check it again\n"\
						.format(curr_row['ID'], curr_row['Perbaikan'] , df_diff.iloc[idxs[j]]['After']))
					print("Incorrect")
				else:
					f.write("Correct correction ({}). In QA logs & new version : {}\n"\
						.format(curr_row['ID'], curr_row['Perbaikan']))
					print("Correct")