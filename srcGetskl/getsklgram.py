#! /usr/bin/env python
# -*- coding: utf-8 -*-
#author: qolina
#Function: extract structured or string version of skeleton from parsed tweets

import os
import re
import time
import sys
import cPickle

########################################################
## Load users and tweets from files in directory dirPath
def extractGramfromSubtree(filepath, outdirPath):
    subFile = file(filepath)
    print "Processing file: " + filepath
    day = filepath[-2:]

    idx = 0
    wordarr = []
    tweetNum = 0
    while True:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', "", lineStr)
        if len(lineStr) <= 0:
            break

        arr = lineStr.split("\t")
        stArr = arr[1].split(" ")
        for st in stArr:
            grams = {}
            wArr = st.split("_")
            if len(wArr) == 1: # no more unigram
                continue
            else:
                for i in range(0, len(wArr)):
                    gram1 = "_".join(wArr[0:i+1])
                    if i < 5:
                        insertHash(gram1)
                    for j in range(0, i):
                        if (i-j) <= 5:
                            gram2 = "_".join(wArr[0+j+1:i+1])
                            insertHash(gram2)
            #print st + ": " + str(grams.keys())

        tweetNum += 1
        if tweetNum % 100000 == 0:
            print "# tweets processed: " + str(tweetNum) + " gramNum: " + str(len(gramHash)) + " at " + str(time.asctime())
            #print "# lexNum: " + str(len(lexHash)) + " twocharNum: " + str(len(twocharHash)) + " markNum: " + str(len(markHash))
    subFile.close()

def mark(w):
    if re.search(r"[:;,.+?!\"\\/\[\]{}<>()*&^%$#@|~]", w):
        return True
    return False

## load stop words
def loadStopword(stopwordsFilePath):
    global stopwordHash
    stopFile = file(stopwordsFilePath)
    while True:
        lineStr = stopFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        stopwordHash[lineStr] = 1
    stopFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(stopwordHash)) + " stop words are loaded from " + stopwordsFilePath

def insertToHash(hashname, item):
    if item not in hashname:
        hashname[item] = 1

########################################################
def insertHash(item):
    global gramHash
    global lexHash
    global markHash
    global twocharHash
    global stopHash, digitHash, avglenHash, fstcharHash
    if (item.find("_") > 0) and (item.find("@usr") < 0): # at least 2-gram | no mention
        arr = item.split("_")
        #''' # one word in 1-length letter -> lexHash/delete
        lexArr = list([1 for w in arr if len(w)==1])
        if len(lexArr) >= 1:
            #insertToHash(lexHash, item)
            return
        #'''
        #''' # one word contains mark -> markHash/delete
        markArr = list([1 for w in arr if mark(w) is True])
        if len(markArr) >= 1:
            #insertToHash(markHash, item)
            return
        #'''
        #''' # one word in 2-length letter -> twocharHash/delete
        lexArr = list([1 for w in arr if len(w)==2])
        if len(lexArr) >= 1:
            #insertToHash(twocharHash, item)
            return
        #'''
        #''' # first character of one word is not \w (a-zA-Z0-9) -> delete
        matchArr = list([1 for w in arr if (len(re.findall(r"\w", w[0]))==0)])
        if len(matchArr) >= 1:
            #insertToHash(fstcharHash, item)
            #print "#first char: " + item
            return
        #'''
        #''' # stop words -> delete
        matchArr = list([1 for w in arr if w in stopwordHash])
        if len(matchArr) >= 1:
            #insertToHash(stopHash, item)
            #print "#stop: " + item
            return
        #'''
        #''' # all words are digits --> delete
        matchArr = list([1 for w in arr if w.isdigit() is True])
        if len(matchArr) == len(arr):
            #insertToHash(digitHash, item)
            #print "#digit: " + item
            return
        #'''
        #''' # average length of words less than 4 --> delete
        matchArr = list([len(w) for w in arr])
        if sum(matchArr)/len(arr) < 4:
            #insertToHash(avglenHash, item)
            #print "#avglen: " + item
            return
        #'''

        #''' # repeated for more than 3 times -> 3 times version
        for match in re.findall(r"(((\w)+)\2{3,})", item):
            item = re.sub(match[0], match[1]*3, item)
            #print "#repeat: " + item
        #'''
        insertToHash(gramHash, item)

########################################################
## extract from skl files in gram
def extractFromDir(dirPath):
    tArr = list([str(i).zfill(2) for i in range(1, 16)])
    for tStr in tArr:
        item = "skl_2013-01-"+tStr
        extractGramfromSubtree(dirPath + r"/" + item, dirPath)

def filtering(filePath):
    print "Processing file: " + filePath
    subFile = file(filePath)
    idx = 0
    while 1:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', "", lineStr)
        if len(lineStr) <= 0:
            break
        idx += 1
        insertHash(lineStr)
        if idx % 100000 == 0:
            print "# units processed: " + str(idx) + " gramNum: " + str(len(gramHash)) + " at " + str(time.asctime())

########################################################
## the main Function
print "Program starts at time:" + str(time.asctime())

stopwordHash = {}
stopwordsFilePath = r"../Tools/stoplist.dft"
loadStopword(stopwordsFilePath)

#gramFile = file(sys.argv[1] + "/grams_others", "w")
gramFile = file(sys.argv[1] + "_filtered", "w")
gramHash = {}
#lexFile = file(sys.argv[1] + "/grams_lex", "w")
#twocharFile = file(sys.argv[1] + "/grams_twochar", "w")
#markFile = file(sys.argv[1] + "/grams_mark", "w")
lexHash = {}
twocharHash = {}
markHash = {}
stopHash = {}
digitHash = {}
avglenHash = {}
fstcharHash = {}

#extractFromDir(sys.argv[1])
filtering(sys.argv[1])

'''
if len(sys.argv) == 2:
    extractGramfromSubtree(sys.argv[1], "./")
elif len(sys.argv) == 3:
    extractGramfromSubtree(sys.argv[1] + r"/" + sys.argv[2], sys.argv[1])
else:
    print "Usage: python getsklgram.py -dirpath -filename\n e.g.: python getsklgram.py ../parsedTweet/subtree1 skl_2013-01-01" 
'''

## writing grams to file separately
print "# Writing to file: lexNum: " + str(len(lexHash)) + " twocharNum: " + str(len(twocharHash)) + " markNum: " + str(len(markHash)) + " stopgramNum: " + str(len(stopHash))  + " digitgramNum: " + str(len(digitHash))  + " avglen<=4gramNum: " + str(len(avglenHash))  + " firstChar-gramNum: " + str(len(fstcharHash))  + " othergramNum: " + str(len(gramHash)) 

'''
for gram in sorted(markHash.keys()):
    markFile.write(gram + "\n")
markFile.close()
for gram in sorted(lexHash.keys()):
    lexFile.write(gram + "\n")
lexFile.close()
for gram in sorted(twocharHash.keys()):
    twocharFile.write(gram + "\n")
twocharFile.close()
'''
for gram in sorted(gramHash.keys()):
    gramFile.write(gram + "\n")
#cPickle.dump(gramHash, gramFile)
gramFile.close()

print "Program ends at time:" + str(time.asctime())
