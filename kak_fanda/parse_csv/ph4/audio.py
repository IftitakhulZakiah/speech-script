import sys
import os

def check_lengths(transcripts, wavs, skipped_idxs):
	wavs = sorted([wav.strip().replace(".wav", "") for wav in wavs])
	
	not_in_wavs = []
	for item in transcripts:
		if item not in wavs:
			not_in_wavs.append(item)
		
	not_in_transcripts = []
	for item in wavs:
		if item not in transcripts and item not in skipped_idxs:
			not_in_transcripts.append(item)

	if not_in_wavs or not_in_transcripts:
		print("Lengths missmatch wavs:{} transcripts:{}".format(len(wavs), len(transcripts)))

	if not_in_wavs:
		print("Items not in wavs are {} items\n{}".format(len(not_in_wavs), "\n".join([item + ": " + transcripts[item] for item in not_in_wavs])))

	if not_in_transcripts:
		print("Items not in transcripts are {} items\n- {}".format(len(not_in_transcripts), " ".join(not_in_transcripts)))