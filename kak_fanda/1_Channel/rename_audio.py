import argparse
import sys
import os

wav_ext = ".wav"

def parse_arguments():
	parser = argparse.ArgumentParser()

	parser.add_argument("wav", help="Wav dir location.", type=str)
	parser.add_argument("mapping", help="Mapping path.", type=str)

	args = parser.parse_args()

	return args

def normalize_path(some_path):
	return some_path.replace(".\\", "")

if __name__ == "__main__":
	args = parse_arguments()

	wav_dir = normalize_path(args.wav)
	mapping_path = normalize_path(args.mapping)

	if not os.path.isdir(wav_dir):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(wav_dir))

	if not os.path.isfile(mapping_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(mapping_path))

	audio_num = len(os.listdir(wav_dir))

	mapping = open(mapping_path).read().splitlines()

	assert len(mapping) == audio_num, "\nJumlah audio dengan transkrip di label track tidak sama.\n#Audio: {}\n#Transkrip: {}".format(audio_num, len(mapping))

	mapping_dict = {}
	for line in mapping:
		parts = line.strip().split("\t", 1)
		mapping_dict[parts[0]] = parts[1]

	for source in mapping_dict:
		source_path = os.path.join(wav_dir, source + wav_ext)
		if not os.path.isfile(source_path):
			print("\nFile {} tidak ditemukan atau sudah pernah di-rename sebelumnya..\nSilakan cek lagi folder audio potongan".format(source_path))
			sys.exit(1)

	for source in mapping_dict:
		source_path = os.path.join(wav_dir, source + wav_ext)
		target_path = os.path.join(wav_dir, mapping_dict[source] + wav_ext)
		try:
			os.rename(source_path, target_path)
		except Exception as e:
			print(e)
			sys.exit(1)

	print("\nAudio di folder {} berhasil diganti nama".format(wav_dir))