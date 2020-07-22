# python get_silent_in_dir.py /srv/data1/speech/public/menlu/master/RM /srv/data1/speech/public/menlu/silent/RM 1.5

import os
import sys

if __name__ == "__main__":
	in_dir = sys.argv[1]
	out_dir = sys.argv[2]
	min_duration = sys.argv[3]

	### RM
	# acc_files = ['AH01_Menlu_Menyapa_RI_tgl_22_Sept_dari_SMU_PBB_ke_72.wav',
	# 			'AH02_Menlu_Menyapa_RI_tgl_22_Sept_dari_SMU_PBB_ke_72.wav',
	# 			'AH03_Press_Statement_BDF_12_oleh_Menlu_Retno_Marsudi.wav',
	# 			'AH04_Press_Statements_11th_BALI_DEMOCRACY_FORUM.wav',
	# 			'AH05_Menlu_RI_WNI_di_Wuhan_siap_di_Evakuasi.wav',
	# 			'AH06_Press_Statement_Menlu_RI_Terpilihnya_Indonesia_sebagai_Anggota_Dewan_HAM_2020_-_2022.wav',
	# 			'AH07_Wawancara_Eksklusif_Bersama_Menteri_Luar_Negeri_Ibu_Retno_Lestari_Priansari_Marsudi.wav',
	# 			'AH09_Retno_Marsudi_Dansa_dan_Diplomasi__In_Frame.wav',
	# 			'15_Cerita_di_Balik_Gaya_Modis_Menlu_Retno_Marsudi_Bak_Anak_Muda_Part_01_-_Alvin_and_Friends_0209.wav']

	### MA
	# acc_files = ['AH02_Maruf_Amin_Saya_Dipilih_Sebagai_Penghargaan_Pada_Ulama_Maruf_Amin_Cawapres_Jokowi.wav',
	# 			'AH04_Politik_Sarung_Maruf_Amin_Maruf_Amin_Soal_Abu_Bakar_Baasyir_Part_2__Mata_Najwa.wav']

	### MS
	# acc_files = ['ET02_IMS_-_Talkshow_APEC_bersama_Mahendra_Siregar.wav',
	# 			'ET03_Presiden_Jokowi_Minta_Wamenlu_Mahendra_Siregar_Rampungkan_GSP.wav',
	# 			'ET05_Diskriminasi_Sawit_Indonesia_Sampaikan_Keberatan_ke_Uni_Eropa.wav']

	### JW
	acc_files = ['AH02_FULL_Pidato_Presiden_Terpilih_Joko_Widodo_VISI_Indonesia.wav',
				'AH03_Full_-_Pidato_Kenegaraan_Presiden_RI_di_DPR_RI.wav',
				'ET09_VISI_INDONESIA_JOKOWI-AMIN__Anti_Pungli_Janji_Copot_Pejabat_Butuh_Menteri_Berani.wav']

	for root, _, files in os.walk(in_dir, topdown = False):
		for file in files:
			if file in acc_files:
				print(file)
				in_file = root + '/' + file
				out_temp = out_dir + '_' + min_duration + '/'
				os.system("python get_silent_sample.py --min-output-duration {} {} {} {}"\
						.format(min_duration, in_file, out_temp, file[:4]))

	
	# waves = {}
	# path = '/srv/data1/speech/public/menlu/silent/'
	# for root, dirs, files in os.walk(path, topdown = False):
	# 	for file in files:
	# 		path_temp = root + '/' + file
	# 		waves[file] = path_temp

	# sorted_waves = [(k, waves[k]) for k in sorted(waves)]

	# out_file = open('utt2spk_noise', 'w')
	# for utt in sorted_waves:
	# 	out_file.write(utt[0].replace('.wav', '') + ' ' + utt[0][:11] + '\n')
	# out_file.close()
