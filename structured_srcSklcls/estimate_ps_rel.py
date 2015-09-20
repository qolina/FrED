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
dataFilePath = r"../parsedTweet/"

relHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
windowHash = {} # timeSliceIdStr:tweetNum
UNIT = "skl"
unitHash = {}
unitAppHash = {}
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
debug = False
for item in fileList:
    if item.find("skl_2013") != 0:
        continue
    sklFile = file(dataFilePath + item)
    print "### Processing " + sklFile.name
    tStr = item[-2:]
    print "Time window: " + tStr
    tweetNum_t = 0
    while 1:
        skeleton = None
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
#            print "Only one dependency relation. Skip!"
            continue
        tweetNum_t += 1
        for rel in relSet:
            key = rel 
            if key in relHash:
                df_hash = relHash[key]
                if tStr in df_hash:
                    df_t_hash = df_hash[tStr]
                else:
                    df_t_hash = {}
            else:
                df_t_hash = {}
                df_hash = {}
            df_t_hash[tweetIDstr] = 1
            df_hash[tStr] = df_t_hash
            relHash[key] = df_hash
        ## depRel in relSet: headWord__headTag||dependentWord__dependentTag||relname

        if tweetNum_t % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! " + str(len(relHash))
    windowHash[tStr] = tweetNum_t
    sklFile.close()
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(relHash))

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
    if item.find("skl_2013") != 0:
        continue
    sklFile = file(dataFilePath + item)
    tStr = item[-2:]
    tweetNum_t = 0
#    dfFile = file(dataFilePath + UNIT + "_df_2013-01-"+tStr, "wb")
    dfFile = file(dataFilePath + UNIT + "_df_01-"+tStr, "wb")
    dfFile.write(tweetNumStr[:-1] + "\n")
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
        sdf_hash = {}
        sapphash = {}
        for idx1 in xrange(len(relSet)):
            for idx2 in xrange(idx1+1, len(relSet)):
                df_hash1 = relHash[relSet[idx1]]
                df_hash2 = relHash[relSet[idx2]]
                days = list(set(df_hash1.keys()).intersection(set(df_hash2.keys())))
 #               days = list([dayid for dayid in df_hash1.keys() if dayid in df_hash2.keys()])
                for day in days:
                    df_t_hash1 = df_hash1[day]
                    df_t_hash2 = df_hash2[day]
                    # df_t_hash  v1
                    #'''                    
                    df_t_list = list(set(df_t_hash1.keys()).intersection(set(df_t_hash2.keys())))
                    df_t_hash = dict([(tid, 1) for tid in df_t_list])
                    #'''                    
                    # df_t_hash  v2 --> bad
                    #df_t_hash = dict([(tid, 1) for tid in df_t_hash1.keys() if tid in df_t_hash2.keys()])

                    sapphash.update(df_t_hash)
                    # update sdf_hash v1
                    '''                    
                    if day in sdf_hash:
                        sdf_t_hash = sdf_hash[day]
                    else:
                        sdf_t_hash = {}
                    sdf_t_hash.update(df_t_hash)
                    sdf_hash[day] = sdf_t_hash
                    '''
                    # update sdf_hash v2
                    #'''                    
                    if day in sdf_hash:
                        sdf_hash[day].update(df_t_hash)
                    else:
                        sdf_hash[day] = df_t_hash
                    #'''                        
        l = len(sdf_hash)
        probTemp = 0.0
        # cal psSum v1
        #'''        
        probList = list([len(sdf_hash[dayid])*1.0/windowHash[dayid] for dayid in sdf_hash.keys()])
        probTemp = sum(probList)
        #'''
        # cal psSum v2
        '''
        for dayid in sorted(sdf_hash.keys()):
            sdf_t_hash = sdf_hash[dayid]
            fst = len(sdf_t_hash)
            probTemp += (fst*1.0)/windowHash[dayid]
        '''
        skeleton.setPS(probTemp/l)
        skeleton.setDF(len(sapphash))
        cPickle.dump(skeleton, dfFile)
        if tweetNum_t % 1000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! "
    dfFile.close()
    print "### " + UNIT + "s' df values are written to " + dfFile.name

print "###program ends at " + str(time.asctime())
