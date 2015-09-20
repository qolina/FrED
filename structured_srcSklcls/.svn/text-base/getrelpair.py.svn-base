#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

class Parsedtweet:
    def __init__(self, id, wordarr):
        self.id = id
        self.words = wordarr

## depRel in relSet: headWord__headTag||dependentWord__dependentTag||relname
class Skeleton:
    def __init__(self, id, relSet):
        self.id = id
        self.relSet = relSet
    def setDF(self, df):
        self.df = df
    def setPS(self, ps):
        self.ps = ps

print "###program starts at " + str(time.asctime())

if len(sys.argv) == 1:
    print "Usage: python *.py day"
    sys.exit()
Day = sys.argv[1]

dataFilePath = r"../parsedTweet/"
UNIT = "skl"

fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
debug = False

''' deal with directory
for item in fileList:
    if item.find("skl_2013") != 0:
        continue
    tStr = item[-2:]
    if (sys.argv) == 2:
        dayArr = sys.argv[1].split(",")
        if tStr not in dayArr:
            continue
'''            
while 1:            
    tStr = Day 
    sklFile = file(dataFilePath + "skl_2013-01-"+tStr, "rb")
    print "### Processing " + sklFile.name
    print "Time window: " + tStr
    relPairHash = {} #relpair:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    tweetNum_t = 0
    relPairFile = file(dataFilePath + "relPairs_2013-01-"+tStr, "wb")
    while 1:
        try:
            skeleton = cPickle.load(sklFile)
        except EOFError:
            print "-loading ends."
            break
        tweetIDstr = skeleton.id
        relSet = skeleton.relSet
        if debug:
            print tweetIDstr + "\t" + "###".join(relSet)
        if len(relSet) == 1:
            print "Only one dependency relation. Skip!"
            continue
        tweetNum_t += 1
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                depRel1 = relSet[idx1]
                depRel2 = relSet[idx2]
                smallRel = depRel1
                bigRel = depRel2
                if cmp(depRel1, depRel2) > 0:
                    smallRel = depRel2
                    bigRel = depRel1
                key = "###".join(set([smallRel, bigRel]))
                if key in relPairHash:
                    df_hash = relPairHash[key]
                    if tStr in df_hash:
                        df_t_hash = df_hash[tStr]
                    else:
                        df_t_hash = {}
                else:
                    df_t_hash = {}
                    df_hash = {}
                df_t_hash[tweetIDstr] = 1
                df_hash[tStr] = df_t_hash
                relPairHash[key] = df_hash
#            print ",".join(relPairHash[key].keys()) + "\t" + str(relPairHash[key].values())

        ## depRel in relSet: headWord__headTag||dependentWord__dependentTag||relname

        if tweetNum_t % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! " + str(len(relPairHash))
    sklFile.close()
    print "### " + str(time.asctime()) + " " + UNIT + "s " + " are loaded." + str(len(relPairHash))

    cPickle.dump(tweetNum_t, relPairFile)
    cPickle.dump(relPairHash, relPairFile)
    relPairFile.close()
    print "###relPairs are writen into " + relPairFile.name
    break

print "###program ends at " + str(time.asctime())
