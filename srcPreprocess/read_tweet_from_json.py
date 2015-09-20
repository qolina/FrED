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
import lang
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



# voting method: currTweet.lang, langText_wholeLine, langText_words
def isENTweet(currTweet):

    if currTweet.lang is not None and currTweet.lang == "en":
        return True

#    langText_wholeLine = lang.isLine_inEng(currTweet.text)
#    if langText_wholeLine == "en":
#        enScoreArr[1] = 1

    wordsArr_ori = currTweet.text.split(" ")
    wordsArr = tweWordsArr_delAllSpecial(wordsArr_ori)

    wordsLangArr = [word for word in wordsArr if lang.isLine_inEng(word)]
    if len(wordsArr) > 0:
        enScore = len(wordsLangArr)*1.0/len(wordsArr)
        if  enScore >= 0.8:
            return True
#        print currTweet.id_str, enScoreArr, currTweet.text

    return False

def loadTweetFromFile(jsonFileName, outFileName_tweetText, outFileName_tweetStruct):
    # debug format
    loadDataDebug = True

    # for statistics when debugging
    statisticArr = [0, 0] # non-eng tweets, encode-error tweets
    
    # should output result or not
    outputFlag_text = False
    outputFlag_struct = False
    if outFileName_tweetText is not None:
        outputFlag_text = True
        out_textFile = file(outFileName_tweetText, "w")
    if outFileName_tweetStruct is not None: # binary output
        outputFlag_struct = True
        out_structFile = file(outFileName_tweetStruct, "wb")

    jsonFile = file(jsonFileName)
    firstLine = jsonFile.readline()
    jsonContents = jsonFile.readlines()
    print "File loaded done. start processing", len(jsonContents), time.asctime()
    textOutArr = []
    structOutArr = []

    lineIdx = 0
### read file option 1 (line by line)
#    while 1:
#        lineStr = jsonFile.readline()
#        if not lineStr:
#            print "End of file. total lines: ", lineIdx
#            break
### read file option 2 (read all lines)
    for lineStr in jsonContents:
        lineStr = lineStr[:-1]
        lineStr = re.sub(r'\\\\', r"\\", lineStr)

        lineIdx += 1
        if lineIdx % 10 == 0:
#            if outputFlag_text:
#                for item in textOutArr:
#                    cPickle.dump(item, out_textFile)
#            if outputFlag_struct:
#                for item in structOutArr:
#                    cPickle.dump(item, out_structFile)

            print "Lines processed (stored): ", lineIdx, " at ", time.asctime()
#            del structOutArr[:]
#            del textOutArr[:]

        # compile into json format
        try:
            jsonObj = json.loads(lineStr)
        except ValueError as errInfo:
            if loadDataDebug:
                print "Non-json format! ", lineStr
            continue

        # create tweet and user instance for current jsonObj
        currUser = getUser(jsonObj)
        currTweet = getTweet(jsonObj)

        if currTweet is None: # lack of id_str
            if loadDataDebug:
                print "Null tweet (no id_str)" + str(jsonObj)
            continue
        if currUser is None: # lack of user or user's id_str
            if loadDataDebug:
                print "Null user (no usr of usr's id_str)" + str(jsonObj)
            continue
        currTweet.user_id_str = currUser.id_str # assign tweet's user_id_str


        if not isENTweet(currTweet):
            if loadDataDebug:
#                print "non-english"
#                print currTweet.id_str, currTweet.text
                statisticArr[0] += 1
            continue

        # output
        # time filtering ,keep tweets between (20130101-20130115)
#        baseTime = readTime_fromTweet(currTweet.created_at)
#        baseDate = time.strftime("%Y-%m-%d", baseTime)
#        if baseDate.startsWith("2012-12-31"):
#            continue

        if outputFlag_struct:
#            cPickle.dump(currTweet, out_structFile)
            structOutArr.append(currTweet)
        if outputFlag_text:
            try:
                # -> leads to 250k encode error tweets when output to file directly
#                out_textFile.write(currTweet.id_str + " " + currTweet.text.encode("utf-8", 'ignore') + "\n")
                # checked  no \t in text
#                cPickle.dump(currTweet.id_str + "\t" + currTweet.text, out_textFile)
                textOutArr.append(currTweet.id_str + "\t" + currTweet.text)
#                print currTweet.text
            except Exception as errInfo:
                if loadDataDebug:
#                    print "encode error"
                    statisticArr[1] += 1
                continue

#        if lineIdx > 10000:
#            print "Lines processed: ", lineIdx, " at ", time.asctime()
#            break

    if outputFlag_text:
        for item in textOutArr:
            cPickle.dump(item, out_textFile)
    if outputFlag_struct:
        for item in structOutArr:
            cPickle.dump(item, out_structFile)
    print "End of file. total lines: ", lineIdx

    jsonFile.close()
    if outputFlag_struct:
        out_structFile.close()
    if outputFlag_text:
        out_textFile.close()
    
    if loadDataDebug:
        print "Statictis of non-eng, encode-error tweets", statisticArr

def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    jsonFileName = getArg(args, "-json")
    if jsonFileName is None:
        sys.exit(0)
    outFileName_tweetText = getArg(args, "-textOut")
    outFileName_tweetStruct = getArg(args, "-structOut")
    return jsonFileName, outFileName_tweetText, outFileName_tweetStruct

if __name__ == "__main__":
    print "Usage: python read_tweet_from_json.py -json tweet.jason.file [-textOut tweetTextFilename -structOut tweetStructureFilename]"
    print "       (eg. -json twitter-20130101.txt -textOut tweetText-20130101.data -structOut tweetStructure-20130101.data)"

    print "Program starts at time:" + str(time.asctime())

    [jsonFileName, outFileName_tweetText, outFileName_tweetStruct] = parseArgs(sys.argv)

    loadTweetFromFile(jsonFileName, outFileName_tweetText, outFileName_tweetStruct)

    print "Program ends at time:" + str(time.asctime())
