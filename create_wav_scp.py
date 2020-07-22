# python create_wav_scp.py <text_file> <out_file> <main_path> <digit_id>
# e.g. python create_wav_scp.py text.txt utt2spk /srv/data1/speech/public/dalnet/waves/ 8
import sys
import os


if __name__ == '__main__':
	in_file = sys.argv[1]
	out_file = sys.argv[2]
	waves_dir_path = sys.argv[3]
#	digit_id = int(sys.argv[4])

	utterances = []

	waves_file_path = {}
	for root, dirs, files in os.walk(waves_dir_path, topdown = True):
		# for curr_dir in dirs:
		# 	files = [file for file in os.listdir(os.path.join(root, curr_dir)) \
		# 		if os.path.isfile(file)]
		# 	print(os.path.join(root, curr_dir))
		for curr_file in files:
			waves_file_path[curr_file.replace('.wav', '')] = os.path.join(root, curr_file)
				# waves_file_path[curr_file.replace('.wav', '')] = os.path.join(os.path.join(root, curr_dir), curr_file)

	id_files = waves_file_path.keys()

	temp_file = open(in_file, 'r')
	for utt in temp_file:
		id_utt = utt.split()[0]
		# utterances.append(id_utt + ' ' + waves_path + '/' + id_utt + '.wav\n')
		if id_utt in id_files:
			utterances.append(id_utt + ' ' + waves_file_path[id_utt]+ '\n')
		else:
			# print(id_utt, ' not exist in wav')
			pass
			
	temp_file.close()


	utterances.sort()
	print("[INFO] Jumlah utterance pada wav.scp ", len(utterances))
	temp_file = open(out_file, 'w')
	for utt in utterances:
		temp_file.write(utt)
	temp_file.close()
