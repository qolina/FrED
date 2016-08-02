# func: load content from tweet.txt file. recollect tweets in each day into seperate files
# this sequence version is for original tweets arranged by time
# the other version is for original tweets may not be arranged by time, and each days' tweet is stored into memory first.

import os
import sys
import re
import time
import json
import cPickle

from Tweet import *

sys.path.append("/home/yxqin/Scripts/")
from tweetStrOperation import *
from strOperation import *


def loadTweetFromFile(dirPath):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    # debug format
    loadDataDebug = True

    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()

    print fileList

    baseDate = None
    output_rawTweetFile = None
    for item in fileList:

        print "## Processing file ", item
        if not item.endswith(".txt"):
            print item, " is not txt file. passed."
            continue
        jsonFile = file(item)
        firstLine = jsonFile.readline()

        lineIdx = 0
        while 1:
            lineStr = jsonFile.readline()
            if not lineStr:
                print "End of file. total lines: ", lineIdx
                break

            lineIdx += 1
            if lineIdx % 100000 == 0:
                print "Lines processed: ", lineIdx, " at ", time.asctime()

            lineStr = lineStr[:-1]
            if len(lineStr) < 20:
                continue
#            lineStr = re.sub(r'\\\\', r"\\", lineStr) # for twitter201301 data, not for stockTweets_201504

            # compile into json format
            try:
                jsonObj = json.loads(lineStr)
            except ValueError as errInfo:
                if loadDataDebug:
                    print "Non-json format! in lineNum:", lineIdx, lineStr
                continue

            # create tweet and user instance for current jsonObj
            currTweet = getTweet(jsonObj)
            if currTweet is None: # lack of id_str
                if loadDataDebug:
                    print "Null tweet (no id_str) in lineNum", lineIdx, str(jsonObj)
                continue

            # output
            # time filtering ,keep tweets between (20130101-20130115)
            currTime = readTime_fromTweet(currTweet.created_at)
            currDate = time.strftime("%Y-%m-%d", currTime)
#            print currDate
            if currDate.startswith("2012-12-31"): 
                continue
            if not currDate[5:7] in ["04", "05"]: # month
                continue

            if baseDate > currDate: # tweet in wrong time series
                print "tweet in wrong time. basedate currdate ", baseDate, currDate, "in lineNum: ", lineIdx
                continue
            if baseDate != currDate:
            # a new date, close previous file, create a new file
                print "Create a new file for date", currDate, " close old date", baseDate
                baseDate = currDate

                if output_rawTweetFile: #close previous file
                    output_rawTweetFile.close()

                output_rawTweetFile = file(dirPath + r"rawTwitter_timeCorrect-" + currDate, "w")
            output_rawTweetFile.write(lineStr + "\n")

        jsonFile.close()
   
def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    rawTweet_dirPath = getArg(args, "-dir")
    if rawTweet_dirPath is None:
        sys.exit(0)
    return rawTweet_dirPath

if __name__ == "__main__":
    print "Usage: python read_tweet_from_json.py -dir rawTweet_dirPath "
    print "       (eg. -dir ~/corpus/rawData_twitter201301 [search for .txt file to process])"

    print "Program starts at time:" + str(time.asctime())

    rawTweet_dirPath = parseArgs(sys.argv)

    loadTweetFromFile(rawTweet_dirPath)

    print "Program ends at time:" + str(time.asctime())
