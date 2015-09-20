#! /usr/bin/env python
# -*- coding: utf-8 -*-
#author: qolina
#Function: extract structured or string version of skeleton from parsed tweets

import os
import re
import time
import sys
import cPickle
import math

def sigmod(value):
    return 1.0/(1.0+math.exp(-1.0*value))

def getMsProb(str1):
    str1 = re.sub(" ", "_", str1)
    if str1 in gramHash:
        return gramHash[str1]
    else:
        return 0.0

########################################################
# cFunc
def cFunc(gramStr):
    score = 0.0
    ngramProb = getMsProb(gramStr)
    ngramProb = math.pow(10.0, ngramProb)
    gramStrSpc = re.sub("_", " ", gramStr)
    if gramStrSpc in wikiHash:
        wikiProb = wikiHash[gramStrSpc]
    else:
        wikiProb = 0.0
    wikiProb = math.exp(wikiProb)

    arr = gramStr.split("_")
    if len(arr) == 1:
        l = 1.0
        scp = 2*math.log10(ngramProb)
    else:
        l = (len(arr)-1)*1.0/len(arr)
        #scp
        scp = ngramProb*ngramProb
        temp = 0.0
        for i in range(len(arr)-1):
            s1 = "_".join(arr[0:i+1])
            s2 = "_".join(arr[i+1:])
            s1prob = math.pow(10.0, getMsProb(s1))
            s2prob = math.pow(10.0, getMsProb(s2))
            temp += s1prob * s2prob
        temp /= (len(arr)-1)
        if scp/temp <= 0.0:
            scp = 0.0  
            #print "## Wrong: scp: " + str(scp), 
            #print " temp: " + str(temp)
        else:
            scp = math.log10(scp/temp)
            #print "## scp: " + str(scp), 
            #print " temp: " + str(temp)
            
            
    score = l * wikiProb*2.0*sigmod(scp)
    '''
    print "cFunc: " + gramStr + " ",
    print score
    '''
    return score

########################################################
def segStr(wArr):
    #print " ".join(wArr)
    gramSet = {} # candidate segmentation
    for i in range(0, len(wArr)):
        #print "****************************" + str(i)
        gramSet_i = {} # candidate segmentation for segmentation begining at i
        gram1 = "_".join(wArr[0:i+1])
        if i < 5:
            #print "###Single: " + gram1
            gramSet_i[gram1] = cFunc(gram1)
        for j in range(0, i):
            if (i-j) <= 5:
                gram2 = "_".join(wArr[0+j+1:i+1])
                for gram_j in gramSet[j]:
                    gram = gram_j + " " + gram2
                    #print "###Mix: " + gram + " = " + gram_j + " + " + gram2
                    gramSet_i[gram] = cFunc(gram_j) + cFunc(gram2)
        sortedSet_i = sorted(gramSet_i.items(), key = lambda a:a[1], reverse = True)
        if len(sortedSet_i) > 5:
            sortedSet_i = sortedSet_i[0:5]
        gramSet_i = dict([(item[0], item[1]) for item in sortedSet_i])
        #print gramSet_i
        gramSet[i] = gramSet_i
    bestSet = sorted(gramSet[len(wArr)-1].items(), key = lambda a:a[1], reverse = True)[0][0]
    return bestSet
    #print bestSet

########################################################
## Load users and tweets from files in directory dirPath
def segstSkl(filepath, outdirPath):
    subFile = file(filepath)
    outputFile = file(filepath + "_segs_repeated", "w")
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

        #segHash = {}
        segList = []
        arr = lineStr.split("\t")
        stArr = arr[1].split(" ")
        for st in stArr:
            wArr = st.split("_") # words in each subtree skeleton
            if len(wArr) == 1: # no more unigram
                continue
            else:
                #print "st: " + st
                seggedStr = segStr(wArr)
                for seg in seggedStr.split(" "):
                    #segHash[seg] = 1
                    segList.append(seg)

        #print lineStr
        #print segHash
        outputFile.write(arr[0] + "\t" +  " ".join(segList) + "\n")
        tweetNum += 1
        if tweetNum % 10000 == 0:
            print "# tweets processed: " + str(tweetNum) + " at " + str(time.asctime())
    subFile.close()
    outputFile.close()

def mark(w):
    if re.search(r"[:;,.+?!\"\\/\[\]{}<>()*&^%$#@|~]", w):
        return True
    return False

## load wiki probabilities of anchor text for subtree skeleton
def loadWiki(filePath):
    global wikiHash
    wikiFile = file(filePath)
    while True:
        lineStr = wikiFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        arr = lineStr.split(" ")
        wikiHash[" ".join(arr[1:])] = float(arr[0])
    wikiFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(wikiHash)) + " wiki anchor texts(prob) are loaded from " + filePath

## load probabilities of grams for subtree skeleton
def loadGrams(filePath):
    global gramHash
    gramFile = file(filePath)
    while True:
        lineStr = gramFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        arr = lineStr.split(" ")
        gramHash[arr[1]] = float(arr[0])
        #if len(gramHash) == 10000000:
            #break
    gramFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(gramHash)) + " grams(prob) are loaded from " + filePath

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
## extract from skl files in gram
def extractFromDir(dirPath):
    tArr = list([str(i).zfill(2) for i in range(1, 16)])
    for tStr in tArr:
        item = "skl_2013-01-"+tStr
        extractGramfromSubtree(dirPath + r"/" + item, dirPath)

########################################################
## the main Function
print "Program starts at time:" + str(time.asctime())

stopwordHash = {}
stopwordsFilePath = r"../Tools/stoplist.dft"
loadStopword(stopwordsFilePath)

gramHash = {}
wikiHash = {}
wikiprobFilePath = r"../Tools/anchorProbFile_all"
loadWiki(wikiprobFilePath)

gramprobFilePath = r"../Tools/gramskl_prob"
loadGrams(gramprobFilePath)

#str1 = "example of word segmentation bill gates"
#segStr(str1.split(" "))
#extractFromDir(sys.argv[1])

if len(sys.argv) == 2:
    segstSkl(sys.argv[1], "./")
elif len(sys.argv) == 3:
    segstSkl(sys.argv[1] + r"/" + sys.argv[2], sys.argv[1])
else:
    print "Usage: python segsklgram.py -dirpath -filename\n e.g.: python segsklgram.py ../parsedTweet/subtree1 skl_2013-01-01" 

print "Program ends at time:" + str(time.asctime())
