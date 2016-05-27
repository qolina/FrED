#! /usr/bin/env python
#coding=utf-8
# evaluation of twevent for stock corpus

import os
import time
import math
import re
import sys
import cPickle
#import numpy as np

def loadNews(newsFilePath):
    newsFile = file(newsFilePath)
    headlineHash = cPickle.load(newsFile)
    newsFile.close()
    print "** News' headlines have been loaded from ", newsFilePath
    return headlineHash


# only keep events who satify ratio < tThreshold
def loadEvents(dirPath):
    eventHash = {} # day:eventList   eventList->[eventWordList1, eventWordList2, ...]

    print "### " + str(time.asctime()) + " # Loading event files from directory: " + dirPath
    fileList = os.listdir(dirPath)
    fileList.sort()

    for item in fileList:
        #if not item.startswith("frmEventFile"):
        if not item.startswith("EventFile"):
            continue
        raw_eventFile = file(dirPath + item)
        print "*********************Reading file: " + item

        day = "2015-05-" + item[item.find("EventFile")+9:item.find("EventFile")+11]
        eventList = []

        lineArr = raw_eventFile.readlines()
        lineArr = [line[:-1] for line in lineArr]
        raw_eventFile.close()

        lineIdx = 0
        while lineIdx < len(lineArr):
            lineStr = lineArr[lineIdx]
            if lineStr.startswith("***"):
                line1 = lineArr[lineIdx + 1]
                eventId = int(line1[line1.find("Event ")+6: line1.find("ratio:")].strip())
                ratioIdxS = line1.find("ratio:") + 7
                ratioIdxE = line1.find(" ", ratioIdxS)
                ratioInt = int(math.ceil(float(line1[ratioIdxS:ratioIdxE])))

                if ratioInt >= tThreshold:
                    break

                line4 = lineArr[lineIdx + 4]
                wordsStr = re.sub("_|\||\|\|", " ", line4) # replace _, |, || into space[ ]
                wordList = wordsStr.split(" ")
                eventList.append(wordList)
            lineIdx += 6
        eventHash[day] = eventList

    return eventHash

def isEventMatchedToNews(wordList, headline):
    headlineWords = headline.lower().split(" ")
    commonWords = [word for word in wordList if word in headlineWords]
    #if len(commonWords)*1.0/len(wordList) > 0:
    if len(commonWords) > 1:
        print commonWords#, wordList, headline
        return True
    return False

def isEventANews(wordList, headlineList):
    matchedNews = [headlineList.index(headline) for headline in headlineList if isEventMatchedToNews(wordList, headline) is True]
    if len(matchedNews) >= 1:
        #print matchedNews, wordList
        return True
    return False

def getPrecision(eventHash, headlineHash):
    trueEventNumHash = {} # day:trueEventNum
    eventNumHash = {} # day:eventNum
    newsNumHash = {}
    for day in sorted(eventHash.keys()):
        eventList = eventHash[day]
        headlineList = headlineHash[day]

        trueEvents = [1 for wordList in eventList if isEventANews(wordList, headlineList)]

        trueEventNumHash[day] = len(trueEvents)
        eventNumHash[day] = len(eventList)
        newsNumHash[day] = len(headlineList)

    macPre = sum(trueEventNumHash.values())*100.0 / sum(eventNumHash.values())
    macRecall = sum(trueEventNumHash.values())*100.0 / sum(newsNumHash.values())
    if 1:
        print "*****************************************Macro Result: "
        print "##Ratio: ", tThreshold
        print "Events Num: ", sum(eventNumHash.values())
        print "trueEvents Num: ", sum(trueEventNumHash.values())
        print "Precision: ", round(macPre, 2)
        print "Recall: ", round(macRecall, 2)


    micPreList = []
    micRecallList = []
    eNumList = [eventNumHash[day] for day in sorted(eventHash.keys())]
    tNumList = [trueEventNumHash[day] for day in sorted(eventHash.keys())]

    for day in sorted(eventHash.keys()):
        micPre = trueEventNumHash[day]*100.0/eventNumHash[day]
        micRecall = trueEventNumHash[day]*100.0/newsNumHash[day]
        micPreList.append(micPre)
        micRecallList.append(micRecall)

    micPreList = [round(item, 2) for item in micPreList]
    micRecallList = [round(item, 2) for item in micRecallList]
    if 1:
        print "*****************************************Micro Result: "
        print "#Event Num: ", eNumList
        print "#TrueE Num: ", tNumList
        print "#Precision: ", sum(micPreList)/len(micPreList), micPreList
        print "#Recall: ", sum(micRecallList)/len(micRecallList), micRecallList


def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    arg1 = getArg(args, "-dir")
    arg2 = getArg(args, "-news")
    arg3 = getArg(args, "-out")

    if (arg1 is None) or (arg2 is None):
        print "Usage: python getPrecision_fromNews.py -dir eventFileDirPath -news newsFilePath [-out output_precision_filename]"
        sys.exit(0)
    return arg1, arg2, arg3

###########################################################
# main function

global tThreshold
tThreshold = 3 

if __name__ == "__main__":
    print "Program starts at time:" + str(time.asctime())
    [eventFileDirPath, newsFilePath, outFilename] = parseArgs(sys.argv)

    headlineHash = loadNews(newsFilePath)
    eventHash = loadEvents(eventFileDirPath)
    getPrecision(eventHash, headlineHash)

    #write2file(outFilename)
    print "Program ends at time:" + str(time.asctime())


