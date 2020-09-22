#!/usr/bin/env python3

import argparse
import subprocess
import io
import wave
import struct
import math
import os
import sys
import numpy as np
import webrtcvad

from scipy import signal as sgn
from scipy.io import wavfile as wav

# Name of the script file
script = __file__
if '/' in __file__:
    script = __file__.split('/')
    script = script[-1]
elif '\\' in __file__:
    script = script.split('\\')
    script = script[-1]

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Create VADed WAV file.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--config", type=str, help="Feature extraction configuration file to read")
    parser.add_argument("--min_silence_duration", type=float, default = 0.5,
                        help="Minimum duration of the outputted WAV file")
    parser.add_argument("wav", type=str, metavar="<wav>")
    parser.add_argument("output", type=str, metavar="<output-name>")
    return parser.parse_args()

def get_file_parser():
    """Get the arguments from the config file supplied by the user."""

    file_parser = argparse.ArgumentParser(description="Create VAD-ed output.",
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    file_parser.add_argument("--sample-frequency", type=int, default = 16000,
                             help="Waveform data sample frequency (must match the waveform file, "
                             "if specified there)")
    file_parser.add_argument("--frame-length", type=int, choices=[10, 20, 30], default = 20,
                             help="Frame length in milliseconds")
    file_parser.add_argument("--frame-shift", type=float, default = 10.0,
                             help ="Frame length in milliseconds")
    file_parser.add_argument("--channel", type=int, choices=[-1, 0, 1], default = 0,
                             help="Channel to extract (-1 -> expect mono, 0 -> left, 1 -> right)")
    file_parser.add_argument("--aggresiveness", type=int, choices=[1, 2, 3], default = 3,
                             help="Aggresiveness of the VAD detection with 1 being the least "
                             "aggresive and 3 being the most.")
    file_parser.add_argument("--allow-downsample", type=str, choices=['true', 'false'],
                             default = "false", help="If true, allow the input waveform to have a "
                             "higher frequency than the specified --sample-frequency (and we'll "
                             "downsample).")
    return file_parser

def read_wav(file_path, expected_sr, expected_channel=-1, allow_downsample=False):
    """Reads a wav file and returns a numpy array of the waveform.

    Args:
      file_path (str): Path of the WAV file.
      expected_sr (int): Expected sampling rate of the WAV file. If the expected_sr does not match
                         with the sampling rate of the file, throws an error.
      expected_channel (-1, 0, 1): If the audio is multichannel, select which channel that will be
                                   used (-1 -> expect mono, 0 -> left, 1 -> right).

    Returns:
      array: A numpy array containing the signal.
    """
    if '|' in file_path: # path contains piping
        parts = []
        cur_command = ''
        quotation = ''
        for c in file_path.strip():
            if c == '|':
                if quotation == '':
                    parts.append(cur_command)
                    cur_command = ''
                else:
                    cur_command += c
            else:
                if c == '"' or c == "'":
                    if quotation == '':
                        quotation = c
                    elif quotation == c:
                        quotation = ''
                cur_command += c

        p = subprocess.run(parts[0].strip(), shell=True, stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
        if len(parts) > 1:
            for part in parts:
                part = part.strip()
                if part:
                    p = subprocess.run(part, shell=True, input=p.stdout, stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
    else: # path does not contains piping
        file_path = file_path.strip()
        if file_path.endswith('.wav'):
            if file_path.startswith('cat '):
                p = subprocess.run(file_path, shell=True, stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
            else:
                p = subprocess.run('cat {}'.format(file_path), shell=True, stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)

    errors = []
    holder = None
    if p.returncode == 0:
        bytes = io.BytesIO(p.stdout)
        holder = wave.open(bytes, 'rb')
        meta = holder.getparams()

        if meta[1] != 2: # byte depth
            errors.append('Can read only 16-bit PCM data')
        if expected_channel == 1 and meta[0] == 1:
            errors.append('Expected number of channel to be no less than 2')
        if meta[2] != expected_sr: # sample rate
            if expected_sr < meta[2] and allow_downsample:
                p1 = subprocess.run('sox -t wav - -r {:d} -t wav -'.format(expected_sr), shell=True,
                                   input=p.stdout, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if p1.returncode == 0:
                    bytes = io.BytesIO(p1.stdout)
                    holder = wave.open(bytes, 'rb')
                    meta = holder.getparams()
                else:
                    errors.append(p1.stderr.decode('utf-8'))
            else:
                errors.append('Waveform and config sample frequency mismatch: {} vs {}'.format(
                    meta[2], expected_sr
                ))
    else:
        errors.append(p.stderr.decode('utf-8'))

    if len(errors) > 0:
        if holder is not None:
            holder.close()
        raise Exception('\n'.join(errors))

    data = holder.readframes(meta[3])
    nframe = int(len(data) / meta[1] / meta[0])
    holder.close()

    if meta[0] > 1: # nchannels
        if expected_channel < 0:
            print('WARNING (read_wav():{}:147) Channel not specified but you have data '
                  'with {:d} channels; defaulting to zero'.format(script, meta[0]),
                  file=sys.stderr)

        if expected_channel < 1:
            data = data[0:2 * nframe]
        else:
            data = data[2 * nframe:4 * nframe]
        data = struct.unpack('<{}h'.format(nframe), data)
        signal = np.array(data).astype(np.int16)
        return meta[2], signal
    else:
        data = struct.unpack('<{}h'.format(nframe), data)
        signal = np.array(data).astype(np.int16)
        return meta[2], signal

def stack_frames(signal, sampling_frequency, frame_length=20, frame_stride=10.0):
    """Frame a signal into overlapping frames, then apply hamming windowing function to them.

    Args:
      signal (array): The audio signal to frame of size (N,).
      sampling_frequency (int): The sampling frequency of the signal.
      frame_length (float): The length of the frame in ms.
      frame_stride (float): The stride between frames in ms.

    Returns:
      array: Array of stacked frames of size (num_frames x frame_width).
    """
    # Initial necessary values
    signal_length = signal.shape[0]
    frame_samples = int(np.round(sampling_frequency * frame_length / 1000))
    frame_stride = int(np.round(sampling_frequency * frame_stride / 1000))

    # Zero padding is done for allocating space for the last frame.
    # No zero padding! The last frame which does not have enough
    # samples(remaining samples <= frame_sample_length), will be dropped!
    num_frames = 1 + int(np.floor((signal_length - frame_samples) / frame_stride))

    # new length
    new_len = int(num_frames * frame_stride + frame_samples)
    padding = signal[-1] * np.ones((new_len - signal_length,), dtype=np.int16)
    signal = np.concatenate((signal, padding))

    # Getting the indices of all frames.
    indices = np.tile(np.arange(0, frame_samples), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_stride, frame_stride), (frame_samples, 1)).T
    indices = np.array(indices, dtype=np.int32)

    # Extracting the frames based on the allocated indices.
    return signal[indices]

def create_vad_wav(x, sr, voiced, step, silence_min):
    count = 0
    splice = 10
    limits = []
    while count < len(voiced) - 1:
        # initialize
        cur_x = []
        count_temp = 0
        while voiced[count] and count < len(voiced) - 1:
            if count_temp == 0: # if this is the first of the current speech segment
                limit1 = round((count - splice) * step * sr) # set start limit
                if limit1 < 0:
                    limit1 = 0

            count += 1 # increase overall counter
            count_temp += 1 # increase counter of the CURRENT speech segment

        if count_temp > 0: # if at least one segment has been found in the current loop
            limit2 = round((count + splice) * step * sr) - 1 # set end counter
            if limit2 >= x.shape[0]:
                limit2 = x.shape[0] - 1

            limits.append([limit1, limit2])

        count += 1
    
    # MERGE OVERLAPPING SEGMENTS
    run = True
    while run:
        run = False
        for i in range(len(limits) - 1): #for each segment
            if limits[i][1] >= limits[i + 1][0]:
                run = True
                limits[i][1] = limits[i + 1][1]
                del limits[i + 1]
                break

    # Get final segments
    limits = merge_gap(limits,sr,silence_min)
    audios = [x[l[0]:l[1]] for l in limits]
    
    return audios

def merge_gap(limits,sr,thr):
    merged = []
    i = 0
    new_part = True
    while i < len(limits) - 1:
        if new_part:
            parts = [limits[i][0]]
        i += 1

        if ((limits[i][0] - limits[i-1][1]) < (sr * thr)):
            new_part = False
        else:
            new_part = True

        if new_part and not (i == len(limits) - 1):
            parts.append(limits[i-1][1])
            merged.append(parts)
        elif (i == len(limits) - 1):
            parts.append(limits[i][1])
            merged.append(parts)
    
    return merged

def main():
    args = get_args()

    if not os.path.exists(args.wav):
        raise OSError('Could not find the WAV file')

    configs = []
    if args.config:
        if not os.path.exists(args.config):
            raise OSError('Could not find the config file')

        with open(args.config) as f:
            for line in f:
                if line.strip():
                    configs += line.strip().split()

    file_parser = get_file_parser()
    conf = file_parser.parse_args(configs)

    sr = conf.sample_frequency
    window_length = conf.frame_length / 1000
    step = conf.frame_shift / 1000.0

    try:
        fs, x = read_wav(args.wav, sr, conf.channel, conf.allow_downsample == 'true')
    except Exception as e:
        _, _, exc_tb = sys.exc_info()
        print('ERROR (read_wav():{}:{:d}) {}'.format(script, exc_tb.tb_lineno, e), file=sys.stderr)
        print('WARNING (main():{}:{:d}) Failed to compute VAD for '
              'utterance {}'.format(script, exc_tb.tb_lineno, args.wav), file=sys.stderr)
    else:
        try:
            vad = webrtcvad.Vad(conf.aggresiveness)
            frames = stack_frames(x, sr, conf.frame_length, conf.frame_shift)
            voiced = []
            for frame in frames:
                is_speech = vad.is_speech(frame.tobytes(), sr)
                voiced.append(is_speech)
            segments = create_vad_wav(x, sr, voiced, conf.frame_shift / 1000.0,args.min_silence_duration)
        except Exception as e:
            _, _, exc_tb = sys.exc_info()
            print('ERROR (main():{}:{:d}) {}'.format(script, exc_tb.tb_lineno, e), file=sys.stderr)
            print('WARNING (main():{}:{:d}) Failed to compute VAD for utterance {}'.format(script,
                exc_tb.tb_lineno, args.wav), file=sys.stderr)
        else:
            i = 1
            for audio in segments:
                wav.write(args.output.split(".wav")[0] + "_" + str(i) + ".wav", sr, audio)
                i += 1
            print('VLOG[2] (main():{}:354) Processed VAD for {}'.format(script, args.wav),
                    file=sys.stderr)

if __name__ == "__main__":
    main()
