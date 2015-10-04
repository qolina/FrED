# func: load content from tweet.txt file. recollect tweets in each day into seperate files
# this sequence version is for original tweets arranged by time
# the other version is for original tweets may not be arranged by time, and each days' tweet is stored into memory first.
# besides, thread version is designed for running program using threads.

import os
import sys
import re
import time
import json
import cPickle
import threading

from Tweet import *

sys.path.append("/home/yxqin/Scripts/")
from tweetStrOperation import *


def loadTweetFromFile(dirPath, dayStr):
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
    if dayStr:
        output_rawTweetFile = file(dirPath + r"rawTwitter_timeCorrect-2013-01-" + dayStr, "w")
    for item in fileList:

        print "## Processing file ", item
        if not item.endswith(".txt"):
            print item, " is not txt file. passed."
            continue
        if dayStr: # only process 201301+dayStr, 201301+(dayStr+1)
            if int(item[-6:-4]) not in [int(dayStr), int(dayStr)+1]: 
                continue

        jsonFile = file(item)
        firstLine = jsonFile.readline()

        lineIdx = 0
        while 1:
            lineStr = jsonFile.readline()
            if not lineStr:
                print "End of file. total lines: ", lineIdx
                break
            lineStr = lineStr[:-1]
            lineStr_readable = re.sub(r'\\\\', r"\\", lineStr)

            lineIdx += 1
            if lineIdx % 100000 == 0:
                print "Lines processed: ", lineIdx, " at ", time.asctime()

            # compile into json format
            try:
                jsonObj = json.loads(lineStr_readable)
            except ValueError as errInfo:
                if loadDataDebug:
                    print "Non-json format! ", lineStr_readable
                continue

            # create tweet and user instance for current jsonObj
            currTweet = getTweet(jsonObj)

            if currTweet is None: # lack of id_str
                if loadDataDebug:
                    print "Null tweet (no id_str)" + str(jsonObj)
                continue

            # output
            # time filtering ,keep tweets between (20130101-20130115)
            currTime = readTime_fromTweet(currTweet.created_at)
            currDate = time.strftime("%Y-%m-%d", currTime)
#            print currDate
            if currDate.startswith("2012-12-31"): 
                continue
            if baseDate > currDate: # tweet in wrong time series
                print "tweet in wrong time", baseDate, currDate
                continue

            if dayStr: # process(timeCorrect) one day's file 
                currDay = time.strftime("%d", currTime)
                if currDay < dayStr:
                    continue
                elif currDay == dayStr:
                    output_rawTweetFile.write(lineStr + "\n")
                else:
                    output_rawTweetFile.close()
                    break
            else:
                if baseDate != currDate:
                # a new date, close previous file, create a new file
                    print "Create a new file for date", currDate, " close old date", baseDate
                    baseDate = currDate

                    if output_rawTweetFile: #close previous file
                        output_rawTweetFile.close()

                    output_rawTweetFile = file(dirPath + r"rawTwitter_timeCorrect-" + currDate, "w")
                output_rawTweetFile.write(lineStr + "\n")

        jsonFile.close()
   

class DayThread(threading.Thread):
    def __init__(self, dirPath, day):
        threading.Thread.__init__(self)
        self.dirPath = dirPath
        self.day = day


    def run(self):
        loadTweetFromFile(self.dirPath, self.day)

def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    rawTweet_dirPath = getArg(args, "-dir")
    stDayStr = getArg(args, "-stday")
    dayNum = int(getArg(args, "-daynum"))
    if rawTweet_dirPath is None:
        sys.exit(0)
    return rawTweet_dirPath, stDayStr, dayNum

if __name__ == "__main__":
    print "Usage: python read_tweet_from_json.py -dir rawTweet_dirPath -stday stDayStr -daynum dayNum"
    print "       (eg. -dir ~/corpus/rawData_twitter201301)"

    print "Program starts at time:" + str(time.asctime())

    [rawTweet_dirPath, stDayStr, dayNum] = parseArgs(sys.argv)

    dayArr = [str(int(stDayStr)+i*2).zfill(2) for i in range(dayNum)]
    print "To be process dayfile", dayArr

    for dayStr in dayArr:
        thread = DayThread(rawTweet_dirPath, dayStr)
        thread.start()

    print "Program ends at time:" + str(time.asctime())
