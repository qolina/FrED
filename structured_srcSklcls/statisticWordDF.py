#! /usr/bin/env python
#coding=utf-8
# function: for calculating similarity between two segments/skeletons when clustering them
import time
import re
import os
import cPickle

wordDFHash = {}
wordAppHash = {}
for tStr in xrange(1, 16):
    tStr = str(tStr).zfill(2)
    textFile = file(r"../data/201301_preprocess/text_2013-01-"+tStr)
    print "Processing " + textFile.name
    idx = 0
    while True:
        lineStr = textFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        if len(lineStr) <= 0:
            break

        tid = tStr + str(idx)
        arr = lineStr.split(" ")
        for w in arr:
            if w in wordAppHash:
                wordAppHash[w].update(dict([(tid, 1)]))
            else:
                wordAppHash[w] = dict([(tid, 1)])
                wordDFHash[w] = 0
        idx += 1
        if idx % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(idx) + " tweets are processed!"

    print "## loading done. " + str(time.asctime()) + textFile.name
    textFile.close()

for w in wordDFHash:
    wordDFHash[w] = len(wordAppHash.pop(w))

wordDFFile = file(r"../Tools/wordDF", "w")
cPickle.dump(wordDFHash, wordDFFile)
wordDFFile.close()

print "Program ends. " + str(time.asctime()) + " " + str(len(wordDFHash)) + " words are obtained! Writen into " + wordDFFile.name
