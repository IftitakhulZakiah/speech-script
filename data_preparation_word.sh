set -e

data_dir=/srv/data1/speech/public/lecture/
csv_dir=$data_dir/csv/
kaldi_kit=$data_dir/kaldi_kit/
text_path=$kaldi_kit/text
stage=3

### create wav.scp
wav_scp=$kaldi_kit/wav.scp
waves_dir_path=$data_dir/wav/
if [ $stage -le 1 ]; then
	python3 create_wav_scp.py $text_path $wav_scp $waves_dir_path 
	echo ""
fi

### create utt2spk
utt2spk=$kaldi_kit/utt2spk
if [ $stage -le 2 ]; then
	python3 create_utt2spk.py $wav_scp $utt2spk "[A-Z]*[0-9]*_[A-Z]*[0-9]*"
	echo ""
fi

### merge the kaldi_kit
kaldi_kit_imk=${data_dir}/imk_pak_dwi/kaldi_kit
if [ $stage -le 3 ]; then
	for file in $kaldi_kit_imk/*; do
		cat $file ${file/'imk_pak_dwi'/'yufid'} ${file/'imk_pak_dwi'/'tutorial_if'} > $kaldi_kit/$(basename $file).temp
		sort $kaldi_kit/$(basename $file).temp > $kaldi_kit/$(basename $file)
		rm $kaldi_kit/$(basename $file).temp
		echo "[INFO] the $(basename $file) already merge"
		echo ""
	done;
fi