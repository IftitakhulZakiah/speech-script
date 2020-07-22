# Copyright Prosa.ai by Rizky Elzandi Barik

from __future__ import division
import pandas as pd
import sys

def calculate_csid(c,s,i,d):
    result = {}
    result["%WER"] = round((s+i+d)/(s+d+c)*100,2)
    result["%C"] = c
    result["%S"] = s
    result["%I"] = i
    result["%D"] = d
    return result

if len(sys.argv) != 3:
    print("CALCULATE WER")
    print("Usage: py calculate_wer.py <per_utt> <out_file>")
    print("Input: per_utt generated when decoding using Kaldi")
    print("Output: %WER, %Correct, %Substituted, %Deleted, and %Inserted word for each sentence")
else:
    per_utt = open(sys.argv[1], "r")
    per_utt = per_utt.read().split("\n")
    csid_all = []
    for i, val in enumerate(per_utt):
        if (i%4 == 0):
            csid = {}
            line = val.split("ref")
            try:
                csid["ref"] = line[1]
            except IndexError:
                break
        if (i%4 == 1):
            line = val.split("hyp")
            csid["hyp"] = line[1]
        if (i%4 == 3):
            line = val.split(" ")
            csid["ID"] = line[0]
            c = int(line[2])
            s = int(line[3])
            i = int(line[4])
            d = int(line[5])
            calc_csid = calculate_csid(c,s,i,d)
            csid["%WER"] = calc_csid["%WER"]
            csid["%C"] = calc_csid["%C"]
            csid["%S"] = calc_csid["%S"]
            csid["%I"] = calc_csid["%I"]
            csid["%D"] = calc_csid["%D"]
            csid_all.append([
                csid["%WER"],
                csid["%C"],
                csid["%S"],
                csid["%I"],
                csid["%D"],
                csid["ID"],
                csid["ref"],
                csid["hyp"],  
            ])
    csid_all = pd.DataFrame(csid_all,columns=["%WER","C","S","I","D","ID","ref","hyp"])

    csid_all.to_csv(sys.argv[2],index=False,line_terminator="\n")
    print(csid_all.to_csv(index=False,line_terminator="\n"))
