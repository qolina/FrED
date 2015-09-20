#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import cPickle

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

def readTime(timeStr):
    #Time format in tweet: "Sun Jan 23 00:00:02 +0000 2011"
    tweetTimeFormat = r"%a %b %d %X +0000 %Y"
    createTime = time.strptime(timeStr, tweetTimeFormat)
    return createTime

urlNum  = [0]*16
NtNum = [0]*16

print "###program starts at " + str(time.asctime())
dataFilePath = r"/disk/local_110_user/yxqin/fbes/data/201301_preprocess/"
outputStr = "urls"
M = 12
fileList = os.listdir(dataFilePath)
for item in sorted(fileList):
    if item.find("tweetFile_") != 0:
        continue
    tStr = item[len(item)-2:len(item)]

    print "### Processing " + item

    tweFile = file(dataFilePath + item, "rb")
    tweetNum_t = 0

    while True:
        try:
            currTweet = cPickle.load(tweFile)
            tweetIDstr = currTweet.id_str
            usrIDstr = currTweet.user_id_str

            if len(currTweet.urls) > 0:
                Url = True
                urlNum[int(tStr)] += 1

            tweetNum_t += 1
            if tweetNum_t % 1000000 == 0:
                print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"

        except EOFError:
            print "### " + str(time.asctime()) + " tweets in " + item + " are loaded." + str(tweetNum_t)
            tweFile.close()
            break
    print "url tweet num: " + str(urlNum[int(tStr)])
    print urlNum[int(tStr)]*1.0/tweetNum_t
    NtNum[int(tStr)] = tweetNum_t

print urlNum
print NtNum

ratio = [urlNum[i]*1.0/NtNum[i] for i in range(1, 16)]
print ratio
print "###program ends at " + str(time.asctime())
