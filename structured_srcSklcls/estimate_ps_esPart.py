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

def loadRelPair(filePath):
    relPairHash = {} #relpair:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    windowHash = {} # timeSliceIdStr:tweetNum
    relPairFile = file(filePath, "rb")
    windowHash = cPickle.load(relPairFile)
    relPairHash = cPickle.load(relPairFile)
    relPairFile.close()
    return windowHash, relPairHash

print "###program starts at " + str(time.asctime())

dataFilePath = r"../parsedTweet/part/"
if len(sys.argv) ==2 :
    dayArr = sys.argv[1].split(",")
UNIT = "skl"

#relPairPath = dataFilePath + "relPairs_2013-01-"+tStr
#[windowHash, relPairHash] = loadRelPair(relPairPath)
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)




# writing to dffile
# write each day's tweetNumber into first line of df file
# Format:01 num1#02 num2#...#15 num15
sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
tweetNumStr = ""
for item in sortedTweetNumList:
    tStr = item[0]
    tweetNum = item[1]
    tweetNumStr += tStr + " " + str(tweetNum) + "#"

# calculate skeleton appHash --> unitHash
for item in fileList:
    if item.find("skl_2013-01-") != 0:
        continue
    sklFile = file(dataFilePath + item)
    tStr = item[-2:]
    if tStr not in dayArr:
        continue
    dfFile = file(dataFilePath + UNIT + "_df_2013-01-"+tStr, "wb")
    dfFile.write(tweetNumStr[:-1] + "\n")
    tweetNum_t = 0
    while 1:
        try:
            skeleton = cPickle.load(sklFile)
        except EOFError:
            print "-loading ends."
            break
        tweetIDstr = skeleton.id
        relSet = skeleton.relSet
        if len(relSet) == 1:
            continue
        tweetNum_t += 1
        sapphash = {}
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                smallRel = relSet[idx1]
                bigRel = relSet[idx2]
                if cmp(smallRel, bigRel) > 0:
                    smallRel = relSet[idx2]
                    bigRel = relSet[idx1]
                key = "###".join(set([smallRel, bigRel]))
                df_t_hash = relPairHash[key][tStr]
                sapphash.update(df_t_hash)
        probTemp = len(sapphash)*1.0/tweetNum_tStr
        if skeleton.id in tweetPSHash:
            tweetPSHash[skeleton.id].update(dict([(tStr:probTemp)]))
        else:
            tweetPSHash[skeleton.id] = dict([(tStr:probTemp)])
        if tweetNum_t % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! "
    dfFile.close()
    print "### " + UNIT + "s' df values are written to " + dfFile.name

print "###program ends at " + str(time.asctime())

