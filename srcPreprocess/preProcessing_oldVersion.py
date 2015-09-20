#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\Twevent\src\preProcessing.py
#author: qolina
#Function: load tweets in dir() and preProcess
#version: V1

import os
import re
import math
import time
import json
#import enchant
import cPickle

########################################################
## Define global objects.
#stemWordHash = {} # stemmedword:original word hash
#stemmer = stem.PorterStemmer()
#engDetector = enchant.Dict("en_US")
stopwordHash = {}
userHash = {} # calculate num of users
tweetLengHash = {} # calculate average length of tweets
wordHash = {} # calculate number of unique words
wordID = 0
lineStringNumber = 0
illegalJsonFormatNumber = 0
legalTweetsNumber = 0
nullIDTweetsNumber = 0
nullRTTweetsNumber = 0
nullUIDTweetsNumber = 0

########################################################
## Define class user(9) and tweet(12) with all (may) used atts.

class User:
    def __init__(self,userAtts):
        self.id_str = userAtts[userAttHash.get("id_str")]
        self.created_at = userAtts[userAttHash.get("created_at")]
        self.location = userAtts[userAttHash.get("location")]
        self.lang = userAtts[userAttHash.get("lang")]
        self.statuses_count = userAtts[userAttHash.get("statuses_count")]
        self.favourites_count = userAtts[userAttHash.get("favourites_count")]
        self.listed_count = userAtts[userAttHash.get("listed_count")]
        self.friends_count = userAtts[userAttHash.get("friends_count")]
        self.followers_count = userAtts[userAttHash.get("followers_count")]
        

class Tweet:
    def __init__(self,tweetAtts):
        self.id_str = tweetAtts[tweetAttHash.get("id_str")]
        self.user_id_str = tweetAtts[tweetAttHash.get("user_id_str")]
        self.text = tweetAtts[tweetAttHash.get("text")]
        self.created_at = tweetAtts[tweetAttHash.get("created_at")]
        self.user_mentions = tweetAtts[tweetAttHash.get("user_mentions")]
        self.hashtags = tweetAtts[tweetAttHash.get("hashtags")]
        self.urls = tweetAtts[tweetAttHash.get("urls")]
        self.retweet_count = tweetAtts[tweetAttHash.get("retweet_count")]
        self.retweeted = tweetAtts[tweetAttHash.get("retweeted")]
        self.favorited = tweetAtts[tweetAttHash.get("favorited")]
        self.in_reply_to_status_id_str = tweetAtts[tweetAttHash.get("in_reply_to_status_id_str")]
        self.lang = tweetAtts[tweetAttHash.get("lang")]
                
    ## feature used
    def setTF_IDF_Vector(self,TF_IDF_Vector):
        self.TF_IDF_Vector = TF_IDF_Vector

########################################################
## Load users and tweets from files in directory dirPath
########################################################
## preprocessing for each tweet:
## 1) delete non-Eng words (#filter out @ and url first#, filter out words contain characters except[a-z][1-9])
## 2) stop words filtering
## 3) 0-length tweet text

def loadDataFromFiles(dirPath, outputDirPath):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    loadDataDebug = True
 #   preprocessDebug = True
    preprocessDebug = False
    global userHash, wordHash, tweetLengHash
    global illegalJsonFormatNumber, legalTweetsNumber, nullIDTweetsNumber, nullUIDTweetsNumber, nullRTTweetsNumber, lineStringNumber
    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()
    lineIdx = 0
    docIndex = 0

    for item in fileList:
        if item.startswith("forzpar"):
            break
        docIndex += 1
        if loadDataDebug:
            print "Reading from file " + ": " + item
        subFile = file(item)
        while True:
           currTweet.user_id_str = currUser.id_str # assign tweet's user_id_str
            
            # pre-processing
            if loadDataDebug:
                print "----current Tweet:" + currTweet.id_str
                print "Before pre-process:" + currTweet.text

            #filter out non-Eng words
           # text_Eng = filter_nonEng(currTweet)
            text_Eng = filterForParsing(currTweet)
            if len(text_Eng) <= 0:
                currTweet.text = None
                if preprocessDebug:
                    print "Deleting 0-length tweet... " + currTweet.id_str
                continue
            else:
                currTweet.text = text_Eng
                if preprocessDebug:
                    print "After process:" + currTweet.text
            
            # calculate
            if currUser.id_str not in userHash:
                userHash[currUser.id_str] = 1
            wordArr = currTweet.text.split(" ");
            tweetLeng = len(wordArr)
            if tweetLeng in tweetLengHash:
                tweetLengHash[tweetLeng] += 1
            else:
                tweetLengHash[tweetLeng] = 1
            for word in wordArr: # wordHash
                if word in wordHash:
                    wordHash[word] += 1
                else:
                    wordHash[word] = 1
            
            # storing
            if legalTweetsNumber == 0:
                baseTime = readTime_fromTweet(currTweet.created_at)
                baseDate = time.strftime("%Y-%m-%d", baseTime)
                legalTweetsNumber += 1
                outputTweetFile = file(outputDirPath + r"tweetFile_" + inputDir_startTime + "_" + baseDate, "wb")
                outputTweetContentFile = file(outputDirPath + r"tweetContentFile_" + inputDir_startTime + "_" + baseDate, "w")
                cPickle.dump(currTweet, outputTweetFile)
                outputTweetContentFile.write(currTweet.id_str + " " + currTweet.text + "\n")
                continue
            
            if loadDataDebug:
                print "After loading: current Tweet:" + currTweet.id_str + " " + currTweet.text
            if lineIdx%10000 == 0:
                print "Log info: " + str(time.asctime()) + " # " + str(lineIdx) + " lines has been read from file" + item
            currDate = time.strftime("%Y-%m-%d", readTime_fromTweet(currTweet.created_at))
            if currDate < baseDate:
                print "wrong current Tweet:" + currTweet.id_str + " " + currTweet.created_at
                continue
            if currDate != baseDate:
                print "### " + outputTweetFile.name, 
                print " and " + outputTweetContentFile.name + " writing process finished! start writing next..."
                outputTweetFile = file(outputDirPath + r"tweetFile_" + inputDir_startTime + "_" + currDate, "wb")
                outputTweetContentFile = file(outputDirPath + r"tweetContentFile_" + inputDir_startTime + "_" + currDate, "w")
                baseDate = currDate
            
            cPickle.dump(currTweet, outputTweetFile)
            outputTweetContentFile.write(currTweet.id_str + " " + currTweet.text + "\n")
            legalTweetsNumber += 1

    
    lineStringNumber = lineIdx
    os.chdir(currDir)
    outputTweetFile.close()
    outputTweetContentFile.close()

   
  

########################################################
## the main Function

print "Attributes lost:" + str(lackAttHash.keys())
print "***All lines in file: " + str(lineStringNumber)
print "Illegal JsonFormat Tweet Number: " + str(illegalJsonFormatNumber)
print "Null Tweet ID Tweet number: " + str(nullIDTweetsNumber)
print "Null user ID String number: " + str(nullUIDTweetsNumber)
print "***Null Eng-content Tweet number: " + str(lineStringNumber-legalTweetsNumber-illegalJsonFormatNumber-nullIDTweetsNumber-nullUIDTweetsNumber-nullRTTweetsNumber)
print "***Legal Tweet number: " + str(legalTweetsNumber)
print "***User number: " + str(len(userHash))
print "***Word number: " + str(len(wordHash))
rtWordNum = 0
hashWordNum = 0
for word in wordHash:
    if word.find("@") == 0:
        rtWordNum += 1
    if word.find("#") == 0:
        hashWordNum += 1
print "***RT usr word: " + str(rtWordNum)
print "***Hash tagged word: " + str(hashWordNum)

print "***Tweet length distribution: " + str(len(tweetLengHash)) + " kind of length"
sortedTweLenList = sorted(tweetLengHash.items(), key = lambda a:a[1], reverse = True)
print sortedTweLenList
sumLen = 0.0
for key in sortedTweLenList:
    sumLen += key[0]*key[1]
print "***Average tweet length: " + str(sumLen/legalTweetsNumber)

print "Program ends at time:" + str(time.asctime())
