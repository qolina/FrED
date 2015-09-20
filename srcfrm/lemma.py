
import extract_word_root as rt
import sys
import os

filename = sys.argv[1]

tmpfile = file(filename)
arr = tmpfile.readlines()
for w in arr:
    w = w[:-1]
    try:
        #w = w.encode("utf", 'ignore')
        print w + "\t" + rt.word_lemma(w, None)
    except UnboundLocalError as err:
        print err
