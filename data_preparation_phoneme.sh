set -e
#### Aturan pakai
#### 
# prefix=TNS
use_prefix=false

abbreviation=mk
text_version=v2.0.0
audio_version=v2.0
data_dir=/srv/data1/speech/public/mk
csv_dir=$data_dir/arsip_pelabelan/$text_version/csv
kaldi_kit=$data_dir/kaldi_kit/$text_version
text_train_dir=$kaldi_kit/text_train
text_test_dir=$kaldi_kit/text_test
log_dir=$kaldi_kit/log/
stage=4

### parse the csv files
if [ $stage -le 1 ]; then
	mkdir -p $log_dir
	mkdir -p $text_train_dir
	mkdir -p $text_test_dir

	for csv in $csv_dir/*; do
		if [ ${csv: -4} == ".csv" ]; then
			# if [[ $csv == *"RF"* ]]; then
				temp=$(basename $csv)
				curr_file=${temp/'.csv'/''}
				echo "$csv"
				python3 kak_fanda/parse_csv/main.py $abbreviation $csv $text_version > $log_dir/parse_csv_log.${curr_file}.txt
				python3 kak_fanda/parse_csv/main.py $abbreviation $csv $text_version #$audio_version
			# fi
		fi
	done;

	echo "[WARNING] Mohon mengecek log terlebih dahulu sebelum lanjut ke langkah berikutnya : $log_dir"
	echo ""
fi

### concat the train texts
text_train_all=$kaldi_kit/text_train.txt
declare -i n_lines_dir=0

if [ $stage -le 2 ]; then
	rm -f $text_train_all # remove if already exist
	files=$(ls $text_train_dir)

	for file in $files;do
		if [ $use_prefix = true ]; then
			sed -e 's/^/ILC/' -i ${text_train_dir}/${file}
		fi
		cat ${text_train_dir}/${file} >> $text_train_all
		n_lines_dir_curr=$(wc -l $text_train_dir/$file | awk -F ' ' '{print $1}')
		n_lines_dir=$((n_lines_dir_curr+n_lines_dir))
	done;

	n_lines_file=$(wc -l $text_train_all  | awk -F ' ' '{print $1}' )
	if [ "$n_lines_dir" -eq "$n_lines_file" ];then
		echo "[INFO] Jumlah baris pada kaldi kit dan text train sudah sama $n_lines_file baris"
		# rm -r $text_train_dir
	else
		echo "[INFO] Jumlah baris pada kaldi kit ($n_lines_file baris) dan text train ($n_lines_dir baris) masih berbeda"
	fi
	echo ""
fi

### concat the test texts
text_test_all=$kaldi_kit/text_test.txt
declare -i n_lines_dir=0

if [ $stage -le 3 ]; then
	rm -f $text_test_all # remove if already exist
	files=$(ls $text_test_dir)

	for file in $files;do
		if [ $use_prefix = true ]; then
			sed -e 's/^/ILC/' -i ${text_test_dir}/${file}
		fi
		cat ${text_test_dir}/${file} >> $text_test_all
		n_lines_dir_curr_file=$(wc -l $text_test_dir/$file | awk -F ' ' '{print $1}')
		n_lines_dir=$((n_lines_dir_curr_file+n_lines_dir))
	done;

	n_lines_file=$(wc -l $text_test_all  | awk -F ' ' '{print $1}' )
	if [ "$n_lines_dir" -eq "$n_lines_file" ];then
		echo "[INFO] Jumlah baris pada kaldi kit dan text test sudah sama $n_lines_file baris"
		# rm -r $text_test_dir
	else
		echo "[INFO] Jumlah baris pada kaldi kit ($n_lines_file baris) dan text test ($n_lines_dir baris) masih berbeda"
	fi
	echo ""
fi


### create wav.scp
wav_scp=$kaldi_kit/wav.scp
# waves_dir_path=$data_dir/waves/$audio_version
waves_dir_path=$data_dir/waves/
if [ $stage -le 4 ]; then

	if [ $use_prefix = true ]; then
		cp -r ${text_train_all} ${text_train_all}.temp
		sed -e 's/^ILC//' -i ${text_train_all}.temp
		python3 create_wav_scp.py ${text_train_all}.temp $wav_scp $waves_dir_path
		sed -e 's/^/ILC/' -i $wav_scp
		rm ${text_train_all}.temp
	else
		python3 create_wav_scp.py $text_train_all $wav_scp $waves_dir_path
		# cat ${kaldi_kit}/wav.*.scp >> $wav_scp
	fi
	echo ""
fi

### create utt2spk
utt2spk=$kaldi_kit/utt2spk
if [ $stage -le 5 ]; then
	

	if [ $use_prefix = true ]; then
		cp -r ${wav_scp} ${wav_scp}.temp
		sed -e 's/^ILC//' -i ${wav_scp}.temp

		python3 create_utt2spk.py ${wav_scp}.temp $utt2spk "^[A-Z]*[0-9]\d{0,3}"

		sed -e 's/^/ILC/' -i $utt2spk
		cp -r $utt2spk ${utt2spk}.temp
		awk '$2="ILC"$2' $utt2spk.temp > $utt2spk
		rm ${wav_scp}.temp
		rm ${utt2spk}.temp
	else
		# python3 create_utt2spk.py $wav_scp $kaldi_kit/utt2spk "[A-Z]*[0-9]*(_[0-1]*[A-Z]+)*"
		python3 create_utt2spk.py $wav_scp $kaldi_kit/utt2spk "[A-Z]+[0-9]+(_[A-Z]+[0-9]+)+"	
	fi
	echo ""
fi

# ### merge the kaldi_kit
# is_merge=false
# kaldi_kit_ilc=${data_dir}/ILC/kaldi_kit
# if [ $is_merge = true ]; then
# 	for file in $kaldi_kit_ilc/*; do
# 		if [[ $file == *"lexicon"* ]]; then
# 			echo "lexicon $file"
# 			cat $file ${kaldi_kit_ilc/'ILC'/'NJW'}/lexicon_train_tsnjw.txt \
# 				${kaldi_kit_ilc/'ILC'/'SSC'}/lexicon_train_tsssc.txt \
# 				${kaldi_kit_ilc/'ILC'/'TNS'}/lexicon_train_tstns.txt > $kaldi_kit/lexicon_train_ts.temp
# 			sort $kaldi_kit/lexicon_train_ts.temp > $kaldi_kit/lexicon_train_ts.txt
# 			rm $kaldi_kit/lexicon_train_ts.temp
# 			echo "[INFO] the ${kaldi_kit}/lexicon_train_ts.txt already merge"
# 			echo ""
# 		else
# 			echo "file $file"
# 			if [ -f $file ]; then
# 				cat $file ${file/'ILC'/'NJW'} ${file/'ILC'/'SSC'} ${file/'ILC'/'TNS'} > $kaldi_kit/$(basename $file).temp
# 				sort $kaldi_kit/$(basename $file).temp > $kaldi_kit/$(basename $file)
# 				rm $kaldi_kit/$(basename $file).temp
# 				echo "[INFO] the $(basename $file) already merge"
# 				echo ""
# 			fi
# 		fi;
		
# 	done;
# fi