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


def lm_score(tweet):
    wordsArr = getValidWords(tweet)

    if len(wordsArr) > 0:
        logP_score = get_lm_Score_of_words(wordsArr)
    else:
        return wordsArr, None

    return wordsArr, logP_score

def ispunc(word):
    if len(word) == 1 and not re.search("[a-zA-Z0-9]", word):
        return True
    return False


# bi-gram
def get_lm_Score_of_words(wordsArr):
    debug = False
    if debug:
        if (logP_uni(wordsArr[0]) != -100) and logP_bin("<s> "+wordsArr[0]) == -100:
            print "start error", wordsArr
        if (logP_uni(wordsArr[-1]) != -100) and logP_bin(wordsArr[-1]+" </s>") == -100:
            print "end error", wordsArr

    lm_score = logP_bin("<s> "+wordsArr[0])
    for wordIdx in range(1, len(wordsArr)-1):
        lm_score += logP_bin(" ".join(wordsArr[wordIdx:wordIdx+2]))
    
    lm_score += logP_bin(wordsArr[-1]+" </s>")
    return lm_score


# p(w)
def logP_uni(word):
#    return -1
    if word in uniMap:
        return uniMap.get(word)
    else:
        return -100.0

# binMap[w1 w2] = p(w2|w1)
def logP_bin(words):
#    return -5
    if words in binMap:
        return binMap.get(words)
    else:
        return -100.0

# triMap[w1 w2 w3] = p(w3|w1 w2)
# p(w1|w2w3)
def logP_tri(words):
#    return -10
    if words in triMap:
        return triMap.get(words)
    else:
        return -100.0

# format of lm file
############### start
#  [empty line in US-english.lm]
#\data\
#ngram 1=64000
#ngram 2=6501697
#ngram 3=12151781
#
#  [another empty line in US-english.lm]
#\1-grams:
#logP word back-off
# ...
#
#\2-grams:
#logP word1 word2 back-off
# ...
#
#\3-grams:
#logP word1 word2 word3
# ...
#
#\end\

def load_trigram_lm(filename):
    global uniMap, binMap, triMap
    uniMap = {}
    binMap = {}
    triMap = {}

    inFile = file(filename)
    content = inFile.readlines()
    content = [line[:-1] for line in content if len(line) > 1] # delete all empty lines

    uniNum = int(content[1][8:])
    binNum = int(content[2][8:])
    triNum = int(content[3][8:])

    uniStart = 5 # 0 + 1 + 3 + 1
    binStart = uniStart + 1 + uniNum + 1
    triStart = binStart + 1 + binNum + 1
    triEnd = -2

    uniStart = 4 # 0 + 1 + 3
    binStart = uniStart + 1 + uniNum
    triStart = binStart + 1 + binNum
    triEnd = -1
    print (uniStart, binStart, triStart)

    assert content[uniStart].startswith("\\1-grams:"), "Wrong read of lm file: " + content[uniStart]
    assert content[binStart].startswith("\\2-grams:"), "Wrong read of lm file: " + content[binStart]
    assert content[triStart].startswith("\\3-grams:"), "Wrong read of lm file: " + content[triStart]

    
    for lineStr in content[uniStart+1:binStart]:
        arr = lineStr.split()
        uniMap[arr[1]] = float(arr[0])
#    for lineIdx in range(uniStart+1:len(content)):
#        if lineIdx in [binStart-1, binStart, triStart-1, triStart]:
#            continue
#        arr = content[lineIdx].split("\t")
#        lmMap[arr[1]] = float(arr[0])

    for lineStr in content[binStart+1:triStart]:
        arr = lineStr.split()
        gram = " ".join(arr[1:3])
        binMap[gram] = float(arr[0])

    for lineStr in content[triStart+1:triEnd]:
        arr = lineStr.split()
        gram = " ".join(arr[1:4])
        triMap[gram] = float(arr[0])


    assert len(uniMap) == uniNum, "Wrong uni-gram number. should be " + str(uniNum) + " current " + str(len(uniMap))
    assert len(binMap) == binNum, "Wrong bin-gram number. should be " + str(binNum) + " current " + str(len(binMap))
    assert len(triMap) == triNum, "Wrong tri-gram number. should be " + str(triNum) + " current " + str(len(triMap))


#    print min(uniMap.values())
#    print min(binMap.values())
#    print min(triMap.values())

#    print "End of file. num of 1-/2-/3-gram: ", (len(uniMap), len(binMap), len(triMap))
    inFile.close()


def filtering_tweets_lm(inFilename, outFilename):
    if outFilename:
        outFile = file(outFilename, "w")
    inFile = file(inFilename)
    lm_scoreArr = []
    scoreHash = {}

    lineIdx = 0

    noneWordApp = []

    noValidWordNum = 0
    while 1:
        lineStr = inFile.readline()
        if not lineStr:
            print "End of file. tweets are loaded. #tweets: ", lineIdx, time.asctime()
            break
        lineIdx += 1
        if lineIdx % 100000 == 0:
            print lineIdx, " tweets are processed.", time.asctime()

        tweArr = lineStr[:-1].split("\t")
        tweet = tweArr[1].lower()
#        print tweet

        [wordsArr, score] = lm_score(tweet)
        if score is None:
            noValidWordNum += 1
            continue

        if abs(score) == (len(wordsArr)+1)*100: # one word only
            noneWordApp.append(score)
            continue

        wordsNum = len(wordsArr)
        if wordsNum in scoreHash:
            scoreHash[wordsNum].append(score)
        else:
            scoreHash[wordsNum] = [score]

        # if score > -100 * 3:
        if score > -100*(wordsNum+1)*0.3: # satisfy filtering ratio
            if outFilename:
                outFile.write(lineStr)
            else:
                print tweet
#        else:
#            print tweet
        lm_scoreArr.append(score)
#            print wordsArr, score

    print "noValidWords", noValidWordNum
    print "#no word appeared tweet: ", len(noneWordApp)
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
    inFile.close()
    outFile.close()

def getArg(args, flag):
    arg = None
    if flag in args:
        arg = args[args.index(flag)+1]
    return arg

def parseArgs(args):
    arg1 = getArg(args, "-lm")
    if arg1 is None:
        sys.exit(0)
    arg2 = getArg(args, "-in")
    if arg2 is None:
        sys.exit(0)
    arg3 = getArg(args, "-out")
    return arg1, arg2, arg3


#######################################################
## main
if __name__ == "__main__":
    print "Usage: python filter_lm.py -lm lmFilename -in tweetCleanTextFilename -out output_filtered_tweetfilename"

    print "Program starts at time:" + str(time.asctime())
    [lmFilename, tweetFilename, outFilename] = parseArgs(sys.argv)

    load_trigram_lm(lmFilename)
    print "LM file is loaded. num of 1-/2-/3-gram: ", (len(uniMap), len(binMap), len(triMap)), time.asctime()

#    tweetFilename = sys.argv[2]
    filtering_tweets_lm(tweetFilename, outFilename)

#    tweet_eg = "Justin bieber smokes weed ! OMG . . . ."
#    score = lm_score(tweet_eg)

    print "Program ends at time:" + str(time.asctime())
