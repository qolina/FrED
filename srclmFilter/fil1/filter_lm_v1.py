import re
import sys
import time

def lm_score(tweet):
    wordsArr = tweet.lower().split(" ")
    wordsArr_noPunc = [word for word in wordsArr if not ispunc(word)]
    logP_score = get_lm_Score_of_words(wordsArr_noPunc)
    return logP_score

def ispunc(word):
    if len(word) == 1 and not re.search("[a-zA-Z0-9]", word):
        return True
    return False


def get_lm_Score_of_words(wordsArr):
    debug = False
    logP_uni_Arr = [logP_uni(word) for word in wordsArr]
#    print "logP_uni_Arr", logP_uni_Arr
    if len(wordsArr) == 1:
        score = logP_uni_Arr[0]
        if debug:
            print "----uni", wordsArr, score
        return score

    elif len(wordsArr) == 2:
        scoreArr = [sum(logP_uni_Arr), logP_bin(wordsArr)]
        score = max(scoreArr)
        if debug:
            print "----bin", wordsArr, scoreArr, score
        return score

    elif len(wordsArr) == 3:
        scoreArr = [sum(logP_uni_Arr), logP_uni_Arr[0] + logP_bin(wordsArr[1:]), logP_uni_Arr[-1] + logP_bin(wordsArr[:-1]), logP_tri(wordsArr)]
        score = max(scoreArr)
        if debug:
            print "----tri", wordsArr, scoreArr, score
        return score

    else:
        scoreArr = []
        for i in range(len(wordsArr)-1):
            left = wordsArr[:i+1]
            right = wordsArr[i+1:]
            scoreArr.append(get_lm_Score_of_words(left) + get_lm_Score_of_words(right))
            if debug:
                print "..split", wordsArr, left, right, scoreArr[-1]
        score = max(scoreArr)
        if debug:
            print "********", wordsArr, scoreArr, score
        return score 


def logP_uni(word):
#    return -1
    if word in uniMap:
        return uniMap.get(word)
    else:
        return -1000.0

def logP_bin(wordsArr):
#    return -5
    words = " ".join(wordsArr)
    if words in binMap:
        return binMap.get(words)
    else:
        return -1000.0

def logP_tri(wordsArr):
#    return -10
    words = " ".join(wordsArr)
    if words in triMap:
        return triMap.get(words)
    else:
        return -1000.0

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
        gram = " ".join(arr[1:-1])
        binMap[gram] = float(arr[0])

    for lineStr in content[triStart+1:triEnd]:
        arr = lineStr.split()
        gram = " ".join(arr[1:])
        triMap[gram] = float(arr[0])


    assert len(uniMap) == uniNum, "Wrong uni-gram number"
    assert len(binMap) == binNum, "Wrong bin-gram number"
    assert len(triMap) == triNum, "Wrong tri-gram number"

#    print min(uniMap.values())
#    print min(binMap.values())
#    print min(triMap.values())

#    print "End of file. num of 1-/2-/3-gram: ", (len(uniMap), len(binMap), len(triMap))
    inFile.close()


def filtering_tweets_lm(filename):
    inFile = file(filename)
    lm_scoreArr = []
    lineIdx = 0
    while 1:
        lineStr = inFile.readline()
        if not lineStr:
            print "End of file. tweets are loaded. #tweets: ", lineIdx, time.asctime()
            break
        lineIdx += 1
        if lineIdx % 1000 == 0:
            print lineIdx, " tweets are processed.", time.asctime()

        tweet = lineStr[:-1]
        print tweet

        score = lm_score(tweet)
        lm_scoreArr.append(score)
        if lineIdx < 10000:
            print score

    inFile.close()

#######################################################
## main
if __name__ == "__main__":
    print "Program starts at time:" + str(time.asctime())
    filename = sys.argv[1]
    load_trigram_lm(filename)
    print "LM file is loaded. num of 1-/2-/3-gram: ", (len(uniMap), len(binMap), len(triMap)), time.asctime()

    tweetFilename = sys.argv[2]
    filtering_tweets_lm(tweetFilename)

#    tweet_eg = "Justin bieber smokes weed ! OMG . . . ."
#    score = lm_score(tweet_eg)

    print "Program ends at time:" + str(time.asctime())
