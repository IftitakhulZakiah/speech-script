# -*- coding: utf-8 -*-
# Copyright Prosa.ai by Fanda YP

import sys
import requests
import os
import re

if len(sys.argv) != 2:
    print("Usage: python sentence_splitter.py <corpus-path>")
    sys.exit()

url_tokenizer = "http://10.181.131.244:8778/tokenizer"

corpus_path = sys.argv[1]

output_path = corpus_path.replace(".txt", "_sent.txt")

if os.path.isfile(output_path):
    os.remove(output_path)

with open(corpus_path, "r") as f:
    raw_corpus = f.read().splitlines()


if __name__ == "__main__":
    for line in raw_corpus:
        # line = line.replace("“", '').replace("”", '')
        line = line.encode('ascii', 'ignore').decode()
        
        # if len(line) > 3: ## handle utf-8 prefix 
        #     temp = ''
        #     temp = line[2:-1] if line[:2] == 'b\'' else line
        #     line = temp

        r = requests.post(url_tokenizer,json={"text":line, "type":"sentence"}, headers={"x-api-key":"nIkp6XNaEOAkbGxqRKsoWBhqS7Hz56QGBb0bOO7P"})
        rkyes = r.json().keys()
        if "sentences" in rkyes:
            if r.json()["sentences"] is not None:
                splitted_corpus = r.json()["sentences"]
        else:
            print("response error")
            with open("re_lines", "a") as f:
                f.write("{}\n".format(line))

        with open(output_path, "a") as f:
            for item in splitted_corpus:
                f.write("{}\n".format(item))