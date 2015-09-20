import re
import sys
import time

sys.path.append("/home/yxqin/Scripts")
from tweetStrOperation import *


def getValidWords(tweet):
    wordsArr = tweet.split(" ")
    wordsArr_noPunc = [word for word in wordsArr if not ispunc(word)]
    wordsArr_noTwiTag = tweWordsArr_delAllSpecial(wordsArr_noPunc)
    wordsArr_noTwiTag = tweWordsArr_delHashtag(wordsArr_noTwiTag)
    return wordsArr_noTwiTag



def filtering_tweets_lm(lmProbFilename, tidFilename, outFilename):
    if outFilename:
        outFile = file(outFilename, "w")
    if tidFilename:
        tidFile = file(tidFilename)
        tidsArr = tidFile.readlines()
        tidsArr = [line.strip() for line in tidsArr]
        tidFile.close()

    lmProbFile = file(lmProbFilename)
    lm_scoreArr = []
    scoreHash = {}

    lineIdx = 0

    noneWordApp = []
    shortlengthNum = 0 # |tweet| < 3

    noValidWordNum = 0
    while 1:
        lineStr = lmProbFile.readline()
        if not lineStr:
            print "End of file. tweets are loaded. #tweets: ", lineIdx, time.asctime()
            break
        lineIdx += 1
        if lineIdx % 100000 == 0:
            print lineIdx, " tweets are processed.", time.asctime()

        tweArr = lineStr[:-1].split("\t")
        score = float(tweArr[0])
        tweet = tweArr[1]
#        print tweet

        if score is None:
            noValidWordNum += 1
            continue

        wordsArr = tweet.split(" ")

        wordsNum = len(wordsArr)
        if wordsNum < 3: # short length tweet
            shortlengthNum += 1
            continue

        if abs(score) == (wordsNum+1)*100: # one word only
            noneWordApp.append(score)
            continue

        if wordsNum in scoreHash:
            scoreHash[wordsNum].append(score)
        else:
            scoreHash[wordsNum] = [score]

        # if score > -100 * 3:
        if score > -100*(wordsNum+1)*0.3: # satisfy filtering ratio
            tidStr = ""
            if tidFilename:
                tidStr = tidsArr[lineIdx-1] + "\t"
            if outFilename:
                outFile.write(tidStr + tweet + "\n")
            else:
                print tweet
#        else:
#            print score, "\t", tweet
        lm_scoreArr.append(score)
#            print wordsArr, score

    print "noValidWords", noValidWordNum
    print "#no word appeared tweet: ", len(noneWordApp)
    print "#tweets with (<3) words: ", shortlengthNum
    print "all valid tweets", len(lm_scoreArr)

# num of tweets satisfy filtering ratio
    goodNum = 0
    for wordsNum in scoreHash:
        if wordsNum > 30:
            continue
        scores = scoreHash[wordsNum]
#        good = [1 for score in scores if score > -300]
        good = [1 for score in scores if score > -100*(wordsNum+1)*0.3]
        goodNum += len(good)
        print "******** wordsNum", wordsNum, len(scores), len(good), len(good)*1.0/len(scores)
#        print min(scores), max(scores), sum(scores)/len(scores)

    print goodNum, goodNum*1.0/len(lm_scoreArr)
    lmProbFile.close()
    outFile.close()

def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    arg1 = getArg(args, "-prob")
    if arg1 is None:
        sys.exit(0)
        
    arg2 = getArg(args, "-tid")
    arg3 = getArg(args, "-out")

    return arg1, arg2, arg3


#######################################################
## main
if __name__ == "__main__":
    print "Usage: python filtering_by_lmProb.py -prob lmProbFilename -tid tidFilename -out output_filtered_tweetfilename"

    print "Program starts at time:" + str(time.asctime())
    [lmProbFilename, tidFilename, outFilename] = parseArgs(sys.argv)

    filtering_tweets_lm(lmProbFilename, tidFilename, outFilename)

    print "Program ends at time:" + str(time.asctime())

