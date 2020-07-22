import argparse
import locale
import sys
import os

allowed_phones = ['a', 'aw', 'ay', 'b', 'c', 'd', 'e', '@', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 
					'ng', 'ny', 'o', 'p', 'r', 's', 'sy', 't', 'u', 'w', 'y', 'z', '<noise>', '<napas>', '<decak>', 
					'<desis>', '<batuk>', '<ketawa>']

deleted_phones = ["'", 'q', 'kh', 'v', 'oy', 'ow', 'ey', 'ew']

allowed_noise = ['<noise>', '<dering>', '<ketawa>', '<musik>', '<tepuk_tangan>', '<ketikan>', '<siul>', '<road>',
				'<suara_burung>', '<suara_anjing>', '<suara_kucing>', '<bayi_nangis>', '<teriakan_anak>', '<mic>',
				'<napas>', '<angin>', '<bip>', '<babble>', '<klakson>', '<stat>', '<nonstat>', '<decak>', '<batuk>']

list_filler = ['<a>', '<ah>', '<aah>', '<eh>', '<eh>', '<ehem>', '<eheh>', '<em>', '<en>', '<e>', '<eb>', '<ed>', 
				'<eeh>', '<eem>', '<eg>', '<ek>', '<eng>', '<ep>', '<et>', '<ey>', '<ey>', '<heeh>', '<heeh>', 
				'<hee>', '<heem>', '<hem>', '<he>', '<heh>', '<hu>', '<ih>', '<oh>', '<oh>', '<uh>']

acceptable_tags = ['<filler>', '<repetisi>', '<jawa>', '<sunda>', '<inggris>', '<arab>', '<asing>', '<daerah>', '<email>']

unchanged_word = ['<napas>', '<overlap>', '<op>', '<dering>', '<decak>', '<batuk>', '<desis>', '<ketawa>', '<unk>']

edit_tags = ['<hapus>', '<sisip>']

deleted_tags = ['<napas>']

def parse_arguments():
	parser = argparse.ArgumentParser()

	parser.add_argument("lexicon", help="Lexicon path/location.", type=str)
	parser.add_argument("csv", help="CSV path/location.", type=str)
	parser.add_argument("audio_dir", help="Audio directory path/location.", type=str)

	args = parser.parse_args()

	return args

def adjust_path_separator(lexicon_path, label_track_path):
	if "\\" in lexicon_path or "\\" in label_track_path:
		path_separator = "\\"
	else:
		path_separator = "/"

	return path_separator

def parse_lexicon(lexicon_path):
	lexicon = {}

	entries = open(lexicon_path).read().splitlines()
	for entry in entries:
		parts = entry.strip().split(' ', 1)
		word = parts[0]
		pron = parts[1]

		if word in lexicon:
			lexicon[word].append(pron)
		else:
			lexicon[word] = [pron]

	return lexicon

def normalize_path(some_path):
	return some_path.replace(".\\", "")

def strip_elmts(_list):
	return [item.strip() for item in _list]

def normalize(_list):
	return [item.replace("'@", "@").lower() for item in _list]

def parse_csv_to_per_idx(csv_path):
	def pad_with_empty_string(_list, target_len=6):
		return _list[:target_len] + ['']*(target_len - len(_list))

	idx = ''
	idx_to_cmps = {}
	
	lines = open(csv_path).read().splitlines()
	for line_num, line in enumerate(lines[1:]):
		line_num = line_num + 2
		if ';' in line:
			delimiter = ';'
		elif ',' in line:
			delimiter = ','

		parts = line.strip().split(delimiter)
		parts = strip_elmts(parts)
		parts = pad_with_empty_string(parts)

		if parts[0] != '' and parts[0].lower() not in edit_tags:
			idx = parts[0].strip().upper()
			if idx not in idx_to_cmps:
				idx_to_cmps[idx] = []
			else:
				correction_log.append("> Line {}: {} -> Id berulang".format(line_num, idx))
			# TODO: cek jenis noise
		elif parts[0] != "<hapus>" and parts[1] != "":
			idx_to_cmps[idx].append([str(line_num)] + normalize(parts[1:]))

	return idx_to_cmps

def check_pron(idx, parts, oov):
	def assert_pron(line_num, pron):
		if pron and pron not in unchanged_word:
			for item in pron.strip().split():
				if item not in allowed_phones:
					correction_log.append("> Line {}: {} -> Lafal terlihat tidak sesuai".format(line_num, pron))
					if item in deleted_phones:
						correction_log.append("  Mungkin lafal berisi fonem berikut yang tidak diperbolehkan {}".format("/".join(deleted_phones)))

	parts = strip_elmts(parts)
	parts = normalize(parts)
	line_num = parts[0]

	word = parts[1]
	pron = parts[2]

	if parts[4] != "" and parts[5] != "": # salah kata
		word = parts[4]
		pron = parts[5]
	elif parts[4] != "" and parts[5] == "" and parts[3] != "<repetisi>":
		# if ' ' not in parts[4] and parts[4].strip().split()[-1] not in allowed_phones: # bentuk baku
		# 	word = parts[4] # perbaikan kata
		if parts[4].strip().split()[-1] in allowed_phones:
			pron = parts[4] # salah lafal

	if parts[3] == "<filler>":
		word = "<filler>"

	if word == "<?>":
		word = "<unk>"

	if word == "<unk>":
		pron = "<noise>"

	if "=" in word or "=" in pron:
		if "=" not in word or "=" not in pron:
			correction_log.append("> Line {}: Penggunaan pemisah '=' harus ada di dalam kata dan pelafalan".format(line_num))

	if "<" in word or ">" in word:
		if "<" not in word or ">" not in word:
			correction_log.append("> Line {}: {} -> Salah ketik".format(line_num, word))

	if "-" in word and len(word.strip().split("-")) == 2:
		items = word.strip().split("-")
		if items[0] == items[1]:
			correction_log.append("> Line {}: {} -> Tanda '-' tidak perlu digunakan".format(line_num, word))

	if " " in word:
		correction_log.append("> Line {}: {} -> Kata yang dikenali mengandung spasi".format(line_num, word))

	words = word.split('=')
	prons = pron.split('=')

	for i, word in enumerate(words):
		if word not in deleted_tags:
			pron = normalize_pron(prons[i])

			assert_pron(line_num, pron)

			if word not in lexicon or pron not in lexicon[word]:
				if word not in oov:
					oov[word] = {}
					oov[word][pron] = [idx]
				elif pron not in oov[word]:
					oov[word][pron] = [idx]
				else:
					oov[word][pron].append(idx)


def check_format(parts):
	line_num = parts[0]
	if parts[2] == '':
		correction_log.append('> Line {}: {} -> Pelafalan kosong'.format(line_num, parts[1]))
	if parts[3] != "" and parts[3] not in acceptable_tags:
		correction_log.append('> Line {}: {} -> kolom 4 hanya boleh berisi <filler> <repetisi> <daerah> <asing> <jawa> <sunda> <arab> \
			<inggris> atau <email>'.format(line_num, parts[3]))
	if parts[4] != '' and parts[5] == '':
		# perbaikan fonem atau perbaikan kata yang salah ucap
		if not is_disfluencies(parts[1]) and " " not in parts[4] and parts[4] not in allowed_phones:
			correction_log.append('> Line {}: {} -> ada sesuatu yang salah dengan kolom 5.. Boleh berisi perbaikan kata, perbaikan fonem, serta perbaikan salah ucap'.format(line_num, parts[4]))
	if parts[1] in list_filler and parts[3] != "<filler>":
		correction_log.append("> Line {}: {} masuk kategori <filler>. Tambahkan keterangan di kolom C".format(line_num, parts[1]))

def check_audio(keys, audio_list):
	if len(keys) != len(audio_list):
		correction_log.append("\n!! Jumlah audio tidak sama dengan transkrip. #audio: {} - #transkrip: {}".format(len(audio_list), len(keys)))
		for idx in keys:
			if idx not in audio_list:
				correction_log.append("Id {} tidak ditemukan di daftar audio".format(idx))

		for idx in audio_list:
			if idx not in keys:
				correction_log.append("Id {} tidak ditemukan di csv".format(idx))
		correction_log.append("Pastikan tidak ada id yang tertukar..")

def get_delimiter():
	delimiter = ""
	locale.setlocale(locale.LC_ALL, '')
	dec_pt_chr = locale.localeconv()['decimal_point']
	if dec_pt_chr == ",":
		delimiter = ";"
	else:
		delimiter = ","

	return delimiter

def normalize_pron(pron):
	if pron not in unchanged_word:	
		pron = ' '.join(pron.strip().split())
	return pron

def is_disfluencies(word):
	return ("<" in word or ">" in word) and word not in allowed_phones and word not in allowed_noise

if __name__ == '__main__':
	args = parse_arguments()
	csv_path = normalize_path(args.csv)
	lexicon_path = normalize_path(args.lexicon)
	audio_path = normalize_path(args.audio_dir)

	if not csv_path.endswith('.csv'):
		print('{} bukan berkas csv. Keluar...'.format(csv_path))
		sys.exit(1)
	if not (os.path.exists(csv_path) and os.path.isfile(csv_path)):
		print('{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.'.format(csv_path))
		sys.exit(1)
	if not os.path.isfile(lexicon_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(lexicon_path))
	if not os.path.isdir(audio_path):
		print("{} tidak ditemukan... pastikan path yang dimasukkan sudah benar.".format(audio_path))

	lexicon = parse_lexicon(lexicon_path)
	audio_list = os.listdir(audio_path)
	audio_list = [os.path.basename(audio).replace(".wav", "") for audio in audio_list]

	csv_basename = os.path.basename(csv_path)
	print("\nMemeriksa csv {} ...".format(csv_basename))

	csv_input = open(csv_path).read().splitlines()
	csv_input = list(filter(None, csv_input))[1:]

	correction_log = []
	disfluencies = []
	oov = {}
	idx_to_cmps = parse_csv_to_per_idx(csv_path)

	for idx, cmps in idx_to_cmps.items():
		for parts in cmps:		
			line_num = parts[0]

			check_format(parts)

			if is_disfluencies(parts[1]) and parts[4] == "":
				if parts[1] not in unchanged_word and parts[3] != "<filler>":
					disfluencies.append(parts[1])

			check_pron(idx, parts, oov)

	check_audio(idx_to_cmps.keys(), audio_list)

	oov_path = csv_path.replace(".csv", "_oov.csv")
	delimiter = get_delimiter()
	with open(oov_path, "w") as f:
		for word in sorted(oov):
			for pron in oov[word]:
				f.write("{}\n".format(delimiter.join([word, pron, " ".join(oov[word][pron])])))

	if disfluencies:
		print("\nCek lagi kata-kata dengan tag berikut barangkali masih ada yang belum diperbaiki")
		print(" - ".join(sorted(disfluencies)))

	if not correction_log:
		print('\nMantul.. Lanjutkan periksa file {}!'.format(oov_path))
	else:
		print("")
		for item in correction_log:
			print(item)
		print("\n!! Perbaiki dulu ketidaksesuaian di atas sebelum melanjutkan ^^")