#! /usr/bin/env python
#coding=utf-8

# there is no need to do recheck. most error are caused by time out

import urllib
import urllib2
import os
import re
import time
import sys
import math

def getProb(phraseList):
    phraseListNew = list([urllib.quote(gram) for gram in phraseList])
    phrasesStr = "\n".join(phraseListNew) 
    #probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6c5bffbd-e43c-44ab-8c69-acf0439a7a6b',phrasesStr)).read()
    #probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()

    try:
        #probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()
        #probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6c5bffbd-e43c-44ab-8c69-acf0439a7a6b',phrasesStr)).read()
        probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',phrasesStr)).read()
#        print probStr[-10:]
    except:# Exception as error_detail:
        #time.sleep(1)
        #return getProb(phraseList)
#        print "error", error_detail #sys.exc_info()[0]

        return list(["-1" for i in phraseList])

    probArr = probStr.strip().split("\r\n")
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

## main

if __name__ == "__main__":
    print "Program starts at time:" + str(time.asctime())

    if len(sys.argv) == 2:
        probFilePath = sys.argv[1]
    else:
        print "Usage: python ngramProb_recheck.py probFilePath (/home/yxqin/corpus/data_stock201504/segment/grams_qtwe/qngrams_01_prob)"
        print "there is no need to do recheck. most error are caused by time out"

        sys.exit(1)

    probFile = file(probFilePath)
    newProbFile = file(probFilePath + "_newprob", "w")

    print "## Reading file " + probFile.name
    phraseList = []
    lineIdx = 0
    N = 1000 # gramNum in each request

    contentArr = probFile.readlines()
    contentArr = [line[:-1] for line in contentArr]
    probFile.close()

    newContentArr = [line[:line.find(" ")].strip()+" "+line[line.find(" ")+1:] for line in contentArr]

#    newContentArr = []
#    for i in range(len(contentArr)/N +1):
#        st = N*i
#        end = N*(i+1)
#        if end > len(contentArr):
#            end = len(contentArr)
#
#        scoreList = [item[:item.find(" ")].strip() for item in contentArr[st:end]]
#        phraseList = [item[item.find(" ")+1:] for item in contentArr[st:end]]
#
#        errorBatch = [1 for item in scoreList if item == "-1"]
#        if sum(errorBatch) == len(scoreList):
#            print "errorBatch: st, end", st, end, len(phraseList), phraseList[-5:]
#            probArr = []
#            for j in range(10):
#                sub_phraseList = phraseList[j*N/10:(j+1)*N/10]
#                sub_probArr = getProb(sub_phraseList)
#                probArr.extend(sub_probArr)
#            
#            print "get prob done", probArr[:5]
#            if len(probArr) != len(phraseList):
#                print "Error! prob output number not equal phrase number"
#                sys.exit(0)
#            for j in range(st, end):
#                newContentArr.append(probArr[j%N] + " " + phraseList[j%N])
#        else:
#            for idx in range(len(scoreList)):
#                newContentArr.append(scoreList[idx] + " " + phraseList[idx])
#        if st % 10000 == 0:
#            print "**", st, "lines are processed.", len(newContentArr) 


    newProbFile.write("\n".join(newContentArr))
    newProbFile.close()

    print "## New Probs are written to file " + newProbFile.name
    print "Program ends at time:" + str(time.asctime())

