# func: load content from tweet.json file. read each tweet into 
# tweetContent(original text) 
# and tweetStructure 

import os
import sys
import re
import time
import json
import cPickle

from Tweet import *

sys.path.append("/home/yxqin/Scripts/")
from tweetStrOperation import *

## extract a tweet for current tweetLine
def getTweet(jsonObj):
    tweetAtts = []
    if not jsonObj.has_key('id_str'):
        return None
    tweetAtts.append(jsonObj['id_str'])
    tweetAtts.append('user_id_str')# user-id will be assigned later
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'text')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'created_at')
    #tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','media')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','user_mentions')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','hashtags')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','urls')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'retweet_count')
    #tweetAtts = getValue_InJson(tweetAtts,jsonObj,'is_rtl_tweet')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'retweeted')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'favorited')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'in_reply_to_status_id_str')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'lang')
    
    tweet = Tweet(tweetAtts)
    tweet = textInOneLine(tweet)

    return tweet

## extract an user for current tweetLine
def getUser(jsonObj):
    userAtts = []
    if not jsonObj.has_key('user'):
        return None
    if not jsonObj['user'].has_key('id_str'):
        return None
    
    userAtts.append(jsonObj['user']['id_str'])
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','screen_name')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','name')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','description')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','created_at')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','location')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','lang')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','statuses_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','favourites_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','listed_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','friends_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','followers_count')
    
    user = User(userAtts)
    return user


# special processing in Tweet.text, replace \n with " "
def textInOneLine(currTweet):
    currTweet.text = re.sub("\n", " ", currTweet.text)
    currTweet.text = re.sub("\s+", " ", currTweet.text).strip()
    return currTweet

def getValue_InJson(attArr, jsonObj, keyword):
    if jsonObj.has_key(keyword):
        attArr.append(jsonObj[keyword])
    else:
        attArr.append(None)
    return attArr
    
def getValue_from2ndLayer_InJson(attArr, jsonObj, keyword1, keyword2):
    if not jsonObj.has_key(keyword1):
        attArr.append(None)
        return attArr
    if jsonObj[keyword1].has_key(keyword2):
            attArr.append(jsonObj[keyword1][keyword2])
    else:
        attArr.append(None)
        #print "Not Found " + keyword1 + " - " + keyword2
        #statistic number of atts missed
        keyword = keyword1 + "-" + keyword2
    return attArr


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
    print "       (eg. -dir ~/corpus/rawData_twitter201301)"

    print "Program starts at time:" + str(time.asctime())

    rawTweet_dirPath = parseArgs(sys.argv)

    loadTweetFromFile(rawTweet_dirPath)

    print "Program ends at time:" + str(time.asctime())
