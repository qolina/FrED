#! /usr/bin/env python
#coding=utf-8

import urllib
import urllib2
import os
import re
import time
import sys
import math

def getProb_unknown(phraseList):
    phraseListNew = list([urllib.quote(gram) for gram in phraseList])
    phrasesStr = "\n".join(phraseListNew) 
    #probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6c5bffbd-e43c-44ab-8c69-acf0439a7a6b',phrasesStr)).read()
    probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()
    '''
    try:
        #probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()
        probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6c5bffbd-e43c-44ab-8c69-acf0439a7a6b',phrasesStr)).read()
    except:
        return list(["-1" for i in phraseList])
    '''
    probArr = probStr.split("\r\n")
    return probArr

def getProb_redmond(phraseList):
    phraseListNew = list([urllib.quote(gram) for gram in phraseList])
    phrasesStr = "\n".join(phraseListNew) 
    try:
        probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()
    except:
        return list(["-1" for i in phraseList])
    probArr = probStr.split("\r\n")
    return probArr

def getProb_beijing(phraseList):
    phraseListNew = list([urllib.quote(gram) for gram in phraseList])
    phrasesStr = "\n".join(phraseListNew) 
    try:
        probStr = urllib2.urlopen(urllib2.Request('http://msraml-s003/ngram-lm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',gramStr)).read()
    except:
        return list(["-1" for i in phraseList])
    probArr = probStr.split("\r\n")
    return probArr

def getProbDebug(phraseList):
    probsAll = []
    for i in range(0, len(phraseList)):
        probArr = getProb(phraseList[i])
        if probArr is None:
            probArr = ["-1"]
            print "##In Debug(<10): Error: " + str(i) + "'s gram: " + str(subList)
        probsAll.append(probArr[0])
    return probsAll 

def getProbDebug1(phraseList):
    probsAll = []
    if len(phraseList) > 100:
        for i in range(0, int(math.ceil(len(phraseList)/100))):
            end = 100*(i+1)
            if end > len(phraseList):
                end = len(phraseList)
            subList = phraseList[100*i, end]
            probArr = getProb(subList)
            if probArr is None:
                probArr = getProbDebug(subList[:])
            probsAll.extend(probArr)
    elif len(phraseList) > 10:
        for i in range(0, int(math.ceil(len(phraseList)/10))):
            end = 10*(i+1)
            if end > len(phraseList):
                end = len(phraseList)
            subList = phraseList[10*i, end]
            probArr = getProb(subList)
            if probArr is None:
                print "## in debug(before): " + str(probArr)
                probArr = getProbDebug(subList[:])
                print "## in debug(before): " + str(probArr)
            probsAll.extend(probArr)
    else:
        for i in range(0, len(phraseList)):
            subList = phraseList[i]
            probArr = getProb(subList)
            if probArr is None:
                probArr = ["-1"]
                print "##In Debug(<10): Error: " + str(i) + "'s gram: " + str(subList)
            probsAll.extend(probArr)
    return probsAll 

def write2file(phraseList, probArr):
    for i in range(len(phraseList)):
        prob = probArr[i]
        gram = phraseList[i]
        probFile.write(prob + " " + gram + "\n")
## main
print "Program starts at time:" + str(time.asctime())

global probFile
#dirPath = r"../parsedTweet/subtree1/"
dirPath = r"/home/yxqin/corpus/data_stock201504/segment/grams_qtwe/"

args = sys.argv
subFile = file(dirPath + args[1])
probFile = file(dirPath + args[1] + "_prob", "w")
print "## Reading file " + subFile.name
phraseList = []
phrasesStr = ""
emptyGramList = []
lineIdx = 0
N = int(args[2]) # default 1000
while True:
    lineStr = subFile.readline()
    if len(lineStr) <= 0:
        print str(lineIdx) + " lines are processed. End of file"
        break
    gramStr = lineStr
    if lineStr == "\n":
        print "##Empty gram: " + lineStr[:-1]
        emptyGramList.append(lineStr)
        continue
    phraseList.append(gramStr[:-1])
    if len(phraseList) == N:
        probArr = getProb_unknown(phraseList)
        '''
        if probArr is None:
            print "## Error: " + str(lineIdx-N+1) + " and following " + str(N) + "grams. probArr: " + str(probArr)
            probArr = getProbDebug(phraseList)
        '''
        ''' output temp result
        print "------------------------------ " + str(lineIdx-N+1) + "-" + str(lineIdx)
        print phraseList
        print probArr
        '''
        if len(phraseList) == len(probArr):
            write2file(phraseList, probArr)
        else:
            print "------------------------------ " + str(lineIdx-N+1) + "-" + str(lineIdx)
            print "##Wrong: prob does not mathch phrases: " + str(len(phraseList)) + " probs: " + str(len(probArr))
        del phraseList[:]
        phrasesStr = ""
    lineIdx += 1
    if lineIdx % N == 0:
        print str(lineIdx) + " lines are processed at " + str(time.asctime())

# last 1000
#try:
#    probArr = getProb(phraseList)
#except:
#    print "Error: " + str(lineIdx) + " and previous " + str(len(phraseList)) + "grams"
#    probArr = getProbDebug(phraseList)

probArr = getProb_unknown(phraseList)
write2file(phraseList, probArr)

subFile.close()
probFile.close()

print "### " + str(len(emptyGramList)) + " empty grams are detected! ",
print emptyGramList
print "## Probs are written to file " + probFile.name
print "Program ends at time:" + str(time.asctime())

