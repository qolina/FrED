#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle
from copy import deepcopy

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

def loadRelPair(filePath):
    relPairHash = {} #relpair:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    relPairFile = file(filePath, "rb")
    tweetNum_day = cPickle.load(relPairFile)
    relPairHash = cPickle.load(relPairFile)
    relPairFile.close()
    print "## loading done. " + str(time.asctime()) + filePath
    return tweetNum_day, relPairHash

########################################################
#main

print "###program starts at " + str(time.asctime())

if len(sys.argv) == 1:
    print "Usage: python *.py day"
    sys.exit()
Day = sys.argv[1]

dataFilePath = r"../parsedTweet/"
UNIT = "skl"
relPairPath = dataFilePath + "relPairs_2013-01-"+Day
[tweetNum_day, relPairHash] = loadRelPair(relPairPath)

dfFile = file(dataFilePath + UNIT + "_dfhash_2013-01-"+Day, "wb")
tweetDFHash = {}

### calculate df of all tweets in Day
# writing to dffile
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
for item in fileList:
    if item.find("skl_2013-01-") != 0:
        continue
    sklFile = file(dataFilePath + item, "rb")
    print "##round 2 processing " + item
    tweetNum_t = 0
    while 1:
        try:
            skeleton = cPickle.load(sklFile)
        except EOFError:
            print "-loading ends(round 2)."
            break
        tweetIDstr = skeleton.id
        relSet = skeleton.relSet
        if len(relSet) == 1:
            print "skip root"
            continue
        tweetNum_t += 1
        sdf_hash = {}
        #'''
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                smallRel = relSet[idx1]
                bigRel = relSet[idx2]
                if cmp(smallRel, bigRel) > 0:
                    smallRel = relSet[idx2]
                    bigRel = relSet[idx1]
                key = "###".join(set([smallRel, bigRel]))
                if key not in relPairHash:
                    continue
                df_hash = relPairHash[key] # only one day
                for day in df_hash.keys():
                    df_t_hash = df_hash[day]
                    if day in sdf_hash:
                        sdf_hash[day].update(df_t_hash)
                    else:
                        sdf_hash[day] = deepcopy(df_t_hash)

        if Day not in sdf_hash:
            dayDF = 0
        else:
            dayDF = len(sdf_hash[Day])*1.0
        tweetDFHash[skeleton.id] = dayDF
        #'''
        if tweetNum_t % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! "

cPickle.dump(tweetNum_day, dfFile)
cPickle.dump(tweetDFHash, dfFile)
dfFile.close()
print "### " + UNIT + "s' df values are written to " + dfFile.name

print "###program ends at " + str(time.asctime())

