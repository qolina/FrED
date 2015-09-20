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
'''
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
'''

print "###program starts at " + str(time.asctime())

dataFilePath = r"../parsedTweet/part/"
UNIT = "skl"

relPairHash = {} #relpair:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
windowHash = {}
#tweetDFHash = {}
#tweetPSHash = {}
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)

## build the dictionary
debug = False
for item in fileList:
    if item.find("skl_2013") != 0:
        continue
    sklFile = file(dataFilePath + item, "rb")
    print "### Processing " + sklFile.name
    tStr = item[-2:]
    print "Time window: " + tStr
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
        if debug:
            print tweetIDstr + "\t" + "###".join(relSet)
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                key = "###".join(set([relSet[idx1], relSet[idx2]]))
                if cmp(relSet[idx1], relSet[idx2]) > 0:
                    key = "###".join(set([relSet[idx2], relSet[idx1]]))
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
    windowHash[tStr] = tweetNum_t
    sklFile.close()
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(relPairHash))


### calculate df
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
    sklFile = file(dataFilePath + item, "rb")
    tStr = item[-2:]
    if len(sys.argv) == 2:
        dayArr = sys.argv[1].split(",")
        if tStr not in dayArr:
            continue
    print "##round 2 processing " + item
    dfFile = file(dataFilePath + UNIT + "_ps_2013-01-"+tStr, "w")
    dfFile.write(tweetNumStr[:-1] + "\n")
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
            continue
        tweetNum_t += 1
        sdf_hash = {}
        sapphash = {}
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                smallRel = relSet[idx1]
                bigRel = relSet[idx2]
                if cmp(smallRel, bigRel) > 0:
                    smallRel = relSet[idx2]
                    bigRel = relSet[idx1]
                key = "###".join(set([smallRel, bigRel]))
                df_hash = relPairHash[key]
                for day in df_hash.keys():
                    df_t_hash = df_hash[day]
                    sapphash.update(df_t_hash)
                    if day in sdf_hash:
                        sdf_hash[day].update(df_t_hash)
                    else:
                        sdf_hash[day] = df_t_hash

        l = len(sdf_hash)
        probTemp = 0.0
        probList = list([len(sdf_hash[dayid])*1.0/windowHash[dayid] for dayid in sdf_hash.keys()])
        probTemp = sum(probList)
        skeleton.setPS(probTemp/l)
        skeleton.setDF(len(sapphash))
#        cPickle.dump(skeleton, dfFile)
        outputArr = list([skeleton.id, str(skeleton.df), str(skeleton.ps)])
        dfFile.write("\t".join(outputArr) + "\t" + " ".join(skeleton.relSet) + "\n")
#        tweetDFHash[skeleton.id] = len(sapphash)
#        tweetPSHash[skeleton.id] = probTemp/l
        if tweetNum_t % 10000 == 0:
#            dfFile.flush()
#            cPickle.Pickler.clear_memo()
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! "
#    cPickle.dump(tweetDFHash, dfFile)
#    cPickle.dump(tweetPSHash, dfFile)
    dfFile.close()
    print "### " + UNIT + "s' df values are written to " + dfFile.name

print "###program ends at " + str(time.asctime())

