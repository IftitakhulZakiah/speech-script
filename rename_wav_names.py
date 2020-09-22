# python rename_wav_names.py <in_dir> <out_dir> <before> <after>
# e.g. python rename_wav_names.py ..\kemenlu\waves\RM15\ ..\kemenlu\waves\temp\ 15 015

import sys
import wave
import contextlib
import os
from shutil import copyfile


in_dir = sys.argv[1]
out_dir = sys.argv[2]
# before = sys.argv[3]
# after = sys.argv[4]
prefix = sys.argv[3]

for root, dirs, files in os.walk(in_dir):
    for curr_utt in files:
        if curr_utt.endswith(".wav"):
            utt_id = curr_utt.replace('LAITB', 'LAITB01')
           if '-' in curr_utt:
               utt_id = int(curr_utt.split('-')[1].replace('.wav', ''))
               if utt_id < 10:
                   utt_id_str = '00' + str(utt_id)
               elif utt_id < 100:
                   utt_id_str = '0' + str(utt_id)
               else:
                   utt_id_str = str(utt_id)
               new_name = curr_utt.replace(str(utt_id),  utt_id_str)
           else:
               # spk_id = curr_utt.split('.wav')[0]
               utt_id_str = '001'
               new_name = curr_utt.replace('.wav',  '_'+ utt_id_str + '.wav')

            new_name = curr_utt.replace(before,after)
            new_name = curr_utt.replace(str(utt_id),  utt_id_str)
           new_name = new_name.replace('-', '_')
           new_name = prefix + new_name
           new_name = new_name.upper()
           new_name = new_name.replace('.WAV', '.wav')
            print(utt_id)
            copyfile(in_dir + curr_utt, out_dir + utt_id)
            os.rename(in_dir + curr_utt, out_dir + new_name)
