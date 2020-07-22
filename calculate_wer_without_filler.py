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

if len(sys.argv) != 2:
    print("CALCULATE WER WITHOUT <filler>")
    print("Usage: py calculate_wer.py <ops>")
    print("Input: ops generated when decoding using Kaldi")
    print("Output: %WER, %Correct, %Substituted, %Deleted, and %Inserted word")
else:
    ops_file = open(sys.argv[1], "r")
    n_corr = 0
    n_del = 0
    n_subs = 0 
    n_ins = 0
    state=''
    for line in ops_file:
        temp = line.split()

        if 'correct' in temp:
            n_corr += int(temp[3])
            state = 'correct'
        elif 'deletion' in temp:
            n_del += int(temp[3])
            state = 'deletion'
        elif 'insertion' in temp:
            n_ins += int(temp[3])
            state = 'insertion'
        elif 'substitution' in temp:
            n_subs += int(temp[3])
            state = 'substitution'

        if '<filler>' in temp:
            print(state)
            if state == 'correct':
                n_corr -= int(temp[3])
                print('n_corr ', n_corr)
            elif state == 'deletion':
                n_del -= int(temp[3])
                print('n_del ', n_del)
            elif state == 'insertion':
                n_ins -= int(temp[3])
                # n_del += int(temp[3])
                print('n_ins ', n_ins)
            elif state == 'substitution':
                n_subs -= int(temp[3])
                n_ins += int(temp[3])
                print('n_subs ', n_subs)

    print(n_corr, n_subs, n_ins, n_del)
    print(calculate_csid(n_corr, n_subs, n_ins, n_del))
