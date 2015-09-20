#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

############################
## load tweetID-usrID
def loadID(filepath):
    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap

############################
## getEventSkl
def mergeSegSkl(dataFilePath, toolDirPath):
    seggedFile = file(dataFilePath + "segged_tweetContentFile_jan" + Day)
    sklFile = file(dataFilePath + "skl_segs_2013-01-" + Day)
    segSklFile = file(dataFilePath + "seggedAndSkl_2013-01-" + Day, "w")
    print "Time window: " + Day

    IDmapFilePath = dataFilePath + "IDmap_2013-01-" + Day
    IDmap = loadID(IDmapFilePath)
    seggedHash = {}

    Idx = 0
    while True:
        lineStr = seggedFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        newContent = re.sub(r" ", r"_", contentArr[2])
        newContent = re.sub(r"\|", r" ", newContent)
        seggedHash[contentArr[0]] = newContent
        Idx += 1
        if Idx % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(Idx) + " tweets are processed!"
    seggedFile.close()
    print "### " + str(time.asctime()) + " " + str(len(seggedHash)) + " segged tweets are loaded!"

    Idx = 0
    common = 0
    sklOnly = 0
    while True:
        lineStr = sklFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        IDstr = IDmap[int(contentArr[0][2:])]
        if IDstr in seggedHash:
            if len(contentArr) < 2:
                segSklFile.write(contentArr[0] + "\t" + seggedHash[IDstr] + "\n")
            else:
                text = contentArr[1].strip() + " " + seggedHash[IDstr].strip()
                segSklFile.write(contentArr[0] + "\t" + text + "\n")
            common += 1
        else:
            if len(contentArr) < 2:
                continue
            else:
                segSklFile.write(lineStr + "\n")
                sklOnly += 1

        Idx += 1
        if Idx % 10000 == 0:
            print "### " + str(time.asctime()) + " " + str(common) + " common tweets, " + str(sklOnly) + " sklOnly tweets are obtained! in tweets: " + str(Idx)

    print "### " + str(time.asctime()) + " " + str(common) + " common tweets, " + str(sklOnly) + " sklOnly tweets are obtained! in tweets: " + str(Idx)
    sklFile.close()
    segSklFile.close()

############################
## main Function
if len(sys.argv) == 2:
    Day = sys.argv[1]
else:
    print "Usage getbtyskl.py day"
    sys.exit()

print "###program starts at " + str(time.asctime())

dataFilePath = r"../parsedTweet/"
toolDirPath = r"../Tools/"

UNIT = "skl"

mergeSegSkl(dataFilePath, toolDirPath)

print "###program ends at " + str(time.asctime())
