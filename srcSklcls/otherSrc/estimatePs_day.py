#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

print "###program starts at " + str(time.asctime())
dataFilePath = r"../parsedTweet/"

if len(sys.argv) == 1:
    print "Usage: python estimatePs_day.py day"
    sys.exit()
else:
    Day = sys.argv[1]

UNIT = "skl"
unitHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
windowHash = {}
psFile = file(dataFilePath + UNIT + "_ps_"+Day, "w")
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
for item in fileList:
    if item.find("skl_2013") != 0:
        continue
    tStr = item[-2:]
    if tStr != Day:
        continue
    sklFile = file(dataFilePath + item)
    print "### Processing " + sklFile.name
    print "Time window: " + tStr
    tweetNum_t = 0
    while 1:
        #[GUA] seggedFile name: * + TimeWindow, format: twitterID, twitterText(segment|segment|...), ...
        lineStr = sklFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        tweetIDstr = contentArr[0]
        tweetText = contentArr[1]
        tweetNum_t += 1
        textArr = tweetText.split(" ")
        for segment in textArr:
            unit = segment
            # statistic segment df
            '''
            apphash = {}
            if unit in unitAppHash:
                apphash = unitAppHash[unit]
            apphash[tweetIDstr] = 1
            unitAppHash[unit] = apphash 
            '''

            # statistic segment ps
            if unit in unitHash:
                df_hash = unitHash[unit]
                if tStr in df_hash:
                    df_t_hash = df_hash[tStr]
                else:
                    df_t_hash = {}
            else:
                df_hash = {}
                df_t_hash = {}
            df_t_hash[tweetIDstr] = 1
            df_hash[tStr] = df_t_hash
            unitHash[unit] = df_hash
            '''
            if unit not in unitLengthHash:
                wordArr = segment.split("_")
                wordNum = len(wordArr)
                unitLengthHash[unit] = wordNum
            '''

        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"
    windowHash[tStr] = tweetNum_t
    sklFile.close()
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. validTweetNum: " + str(tweetNum_t) + " unitNum: " + str(len(unitHash))

print "###Calculating units' ps in one day. " + str(time.asctime())
## writing to unit ps file
for unit in unitHash.keys():
    prob = len(unitHash[unit][Day])*1.0/windowHash[Day]
    unitHash[unit] = prob

cPickle.dump(unitHash, psFile)
psFile.close()
print "### " + UNIT + "s' ps values are written to " + psFile.name

print "###program ends at " + str(time.asctime())
