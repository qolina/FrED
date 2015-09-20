#! /usr/bin/env python
# -*- coding: utf-8 -*-
#author: qolina
#Function: split id[tab]text into two files which contains ids and text separately.
# input is the tweetContentFiles after preprocessing.

import os
import re
import time
import sys

########################################################
## Load users and tweets from files in directory dirPath

def extractTags(filepath):
    subFile = file(filepath)
    tagFile = file(r"./tags.txt", "w")
    tagHash = {}
    while True:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break

        arr = lineStr.split(" ")
        for word in arr:
#            warr = word.split("/")
#            tag = warr[1]
#            spliterIndex = word.rfind("/")
            spliterIndex = word.rfind("_")
            tag = word[spliterIndex:]

            if tag in tagHash:
                continue
            else:
                tagHash[tag] = 1
    sortedList = sorted(tagHash.items(), key = lambda a:a[0])            
    for item in sortedList:
        tagFile.write(item[0] + "\n")

    tagFile.close()
    
########################################################
## the main Function
print "Program starts at time:" + str(time.asctime())

if len(sys.argv) == 2:
    extractTags(sys.argv[1])
else:
    filepath = "./data/input.txt"
    extractTags(filepath)

print "Program ends at time:" + str(time.asctime())
