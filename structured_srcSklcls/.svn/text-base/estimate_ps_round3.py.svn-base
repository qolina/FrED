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

def loaddfhash(filePath):
    dfHash = {} #tweetid:df_day
    dfFile = file(filePath, "rb")
    tweetNum_day = cPickle.load(dfFile)
    dfHash = cPickle.load(dfFile)
    dfFile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filePath
    return tweetNum_day, dfHash

########################################################
#main

print "###program starts at " + str(time.asctime())

dataFilePath = r"../parsedTweet/"
UNIT = "skl"

windowHash = {}
tweetPSHash = {}
tweetDFHash = {}

### calculate ps of all tweets in all day
# writing to dffile
for tStr in xrange(1, 16):
    tStr = str(tStr).zfill(2)
    dfFilepath = dataFilePath + UNIT + "_dfhash_2013-01-"+tStr
    [tweetNum_day, dfHash] = loaddfhash(dfFilepath)
    print "Day " + tStr + " tweet_day: " + str(tweetNum_day) + ", tweet_All: " + str(len(dfHash))
    windowHash[tStr] = tweetNum_day
    for sid in dfHash:
        dayDF = dfHash[sid]
        dayPS = dayDF*1.0/tweetNum_day
        pshash = {}
        pshash[tStr] = dayPS
        if dayDF > 0: # a skeleton may not appear in some days
            if sid in tweetPSHash:
                tweetPSHash[sid].update(pshash)
                tweetDFHash[sid] += dayDF
            else:
                tweetPSHash[sid] = pshash
                tweetDFHash[sid] = dayDF
    print "## " + str(time.asctime()) + " Merging done in day " + tStr

print "len tweetPSHash: " + str(len(tweetPSHash))
print "len tweetDFHash: " + str(len(tweetDFHash))

for tStr in xrange(1, 16):
    tStr = str(tStr).zfill(2)
    psFile = file(dataFilePath + UNIT + "_pshash_2013-01-"+tStr, "wb")
    ps_day = {}
    df_day = {}
    for sid in tweetPSHash:
        if not sid.startswith(tStr):
            continue
        psVal = sum(tweetPSHash[sid].values())/len(tweetPSHash[sid])
        ps_day[sid] = psVal
        df_day[sid] = tweetDFHash.pop(sid)

    cPickle.dump(ps_day, psFile)
    cPickle.dump(df_day, psFile)
    print "## " + str(time.asctime()) + " writing done in day " + tStr + " int " + psFile.name
    psFile.close()

print "###program ends at " + str(time.asctime())

