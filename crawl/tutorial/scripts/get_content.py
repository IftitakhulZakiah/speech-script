# Copyright Prosa.ai by Iftitakhul Zakiah

import argparse
import json

def get_args():
    parser = argparse.ArgumentParser(description="Get content for each element in input",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", type=str, metavar="The JSON Input")
    parser.add_argument("output", type=str, metavar="The Text Output")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	file = open(args.input, 'r')
	all_json = []
	all_contents = []

	for curr_obj in file:
		if curr_obj[-2:-1] == ',':
			curr_obj = curr_obj[:-2]

		try:
			curr_json = json.loads(curr_obj)
			all_json.append(curr_json)
		except Exception as e:
			# print(curr_obj)
			pass
		finally:
			if len(all_json) > 0:
				curr_content = all_json[-1]['content']
				all_contents.append(' '.join(curr_content).encode('utf-8').strip())
	file.close()


	file = open(args.output, 'w')
	for content in all_contents:
		content = content.strip()
		file.write("{}\n".format(content))
	file.close()
