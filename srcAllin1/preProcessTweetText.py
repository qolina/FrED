import sys
import os
import cPickle
from collections import Counter

sys.path.append(os.path.expanduser("~")+"/Scripts")
from sysOperation import *
from strOperation import *
from tweetStrOperation import *
from fileOperation import *

#########  Procedures
# tweetClean:
#    delete illegal: 
#        delete non-valid Url, 
#        delete illegeLetter in mention, 
#        delete words with puncs only, 
#        changeCode2char, 
#        strip illegal letter in word, 
#        delete illegal letter in word, 
#        delete illegal letter in hashtag
#    add space before punctuations: !,.;?
#    stem words
#    delete stopwords
# delete 0-length cleanedText
# del tweets with no normal words, which are not Mention, Url, RT; del tweets with one Hashtag

#stemmer = stem.PorterStemmer()
#engDetector = enchant.Dict("en_US")
#@profile
def tweetTextCleaning_infile(textFileName, outFileName):
    # debug format
    debugFlag = True

    # for statistics when debugging
    statisticArr = [0, 0] # 0-length tweets, mention-url-RT-only tweet

    outputFlag_text = False
    if outFileName is not None:
        outputFlag_text = True
        out_textFile = file(outFileName, "w")

    textFile = file(textFileName)

    clean_tweets = []

    lineIdx = 0
    while 1:
        lineStr = textFile.readline()
        if not lineStr: break
        lineStr = lineStr.strip()

        lineIdx += 1
        if lineIdx % 10000 == 0:
            print "Lines processed: ", lineIdx, " at ", time.asctime()

        tweet_arr = lineStr.split("\t")
        if len(tweet_arr) < 13: continue
        tweet_id = tweet_arr[6]
        tweet_text = tweet_arr[8]
        tweet_time = tweet_arr[9]
        if tweet_time == "false": continue
        [ttime_year, ttime_month, ttime_day, ttime_hour] = gettime(tweet_time)
        if ttime_year != 2012 or ttime_month=="": continue
        #if (ttime_month == "Oct" and ttime_day not in range(9, 32)) or (ttime_month == "Nov" and ttime_day not in range(1, 8)): continue
        if ttime_month != "Oct": continue
        if ttime_day not in range(9, 31): continue
        #if ttime_day not in range(20, 31): continue

        cleaned_text = tweetClean(tweet_text)

        ## special case filtering
        if len(cleaned_text) < 1:
            if debugFlag:
#                print "0-length tweet"
                statisticArr[0] += 1
            continue

        wordsArr_normalWord = tweWordsArr_delAllSpecial(cleaned_text.split(" "))
        if len(wordsArr_normalWord) < 1 or oneHTArr(wordsArr_normalWord):
            if debugFlag:
#                print "all-special-tag tweet"
                statisticArr[1] += 1
            continue

        if 0: # use first3days
            tw = hour/4
            if ttime_day==10: tw += 6
            if ttime_day==11: tw += 12
            tw = str(tw)
            subtw=hour
        else: # use data in Oct 9-30, which contains 2million tweets each day
            tw = str(ttime_day)
            subtw = 1+(ttime_hour/2)
        #clean_tweets.append([tweet_id, cleaned_text, tw, subtw])
        clean_tweets.append([tweet_id, tweet_text, tw, subtw])

        #if lineIdx == 1000000: break
    if debugFlag:
        print "Statictis of 0-length, all-special-tag tweets", statisticArr
    textFile.close()

    print "# Obtained #tweet", len(clean_tweets), time.asctime()
    if outputFlag_text:
        for day in range(9, 31):
            sorted_clean_tweets_day = sorted([(item[0], item[1], item[2], item[3]) for item in clean_tweets if item[2]==str(day)], key=lambda a:a[3])
            for [tweet_id, cleaned_text, tweet_tw, tweet_subtw] in sorted_clean_tweets_day:
                out_textFile.write(tweet_id + "\t" + tweet_tw + "\t" + str(tweet_subtw) + "\t" + cleaned_text + "\n")
            print "# written #tweets in day ", len(sorted_clean_tweets_day), day, time.asctime()
        out_textFile.close()
 
def gettime(time_str):
    #print time_str
    year = 2012 if time_str.find("2012") else 0
    month = ""
    if time_str.find("Oct") >=0 : month = "Oct"
    elif time_str.find("Nov") >= 0: month = "Nov"
    day = int(time_str[time_str.find("-")+2:].split(" ")[0])
    arr = time_str.split(" ")
    hour = int(arr[0][:arr[0].find(":")])
    if arr[1]=="AM" and hour==12: hour = 0
    if arr[1]=="PM" and hour!=12: hour += 12
    return year, month, day, hour

def oneHTArr(wordsArr):
    if len(wordsArr) == 1 and wordsArr[0].startswith("#"):
        return True

#@profile
def tweetClean(text):
    wordsArr = text.split(" ")
    wordsArr = tweetArrClean_delIllegal(wordsArr)
    wordsArr = tweetArrClean_spcBefPunc(wordsArr)

#    wordsArr = tweetArr_stem(wordsArr)

#    stopFileName = r"~/Tools/stoplist.dft"
#    stopwordHash = loadStopword(stopFileName)
#    wordsArr = tweetArrClean_delStop(wordsArr, stopwordHash)

    return " ".join(wordsArr)

def tweetArr_stem(wordsArr):
    wordsArr = [stemmer.stem(word) for word in wordsArr]
    return wordsArr

def tweetArrClean_spcBefPunc(wordsArr):
    wordsArr = [add_space_before_puncsInStr(word) for word in wordsArr]
    return wordsArr

def tweetArrClean_delStop(wordsArr, stopwordHash):
    wordsArr = [word for word in wordsArr if word not in stopwordHash]
    return wordsArr

def tweetArrClean_delUrl(wordsArr):
    wordsArr = [word for word in wordsArr if word.find("http") < 0]
    return wordsArr

#@profile
def tweetArrClean_delIllegal(wordsArr):
    newArr = []
    for word in wordsArr:
#        if re.search('http',word):  # keep urls
        if word.find("http") >= 0:
            if not getValidURL(word):
                continue

            newArr.append(getValidURL(word))
            continue        

        if word.find("@") >= 0: # mention
            word = word[word.find("@"):]
            word = re.sub("[^@a-zA-Z0-9_]"," ",word) # catenation of mention and other words
            newArr.append(word)
            continue
 
        hashTagWordCopy = ""
        if word.startswith("#"):
            hashTagWordCopy = word
            word = word[1:]
       
        if len(word) > 1 and contain_only_punc_in_word(word):
            continue

        word = code2char(word)

        word = strip_nonLetter_in_word(word)
        if len(word) < 1:
            continue

        if contain_illegal_letter_in_word(word):
            continue

        if len(hashTagWordCopy)>1: # if hashtag word contains illegal letter, remove it
            newArr.append("#"+word)
            continue

        newArr.append(word)
    return newArr 

def getValidURL(word):
    if not word.startswith("http"):
        return None
    if len(word)<20:
        return None
    if contain_illegal_letter_in_word(word):
        return None
    if len(word) > 20:
        return word[:20]

# replace code like &lt; &gt; to < > in word
def code2char(word):
#    word = re.sub("&lt;","<", word)
#    word = re.sub("&gt;",">", word)
    word = word.replace("&lt;", "<")
    word = word.replace("&gt;", ">")
    word = word.replace("&amp;", "&")
    return word

def contain_illegal_letter_in_word(word):
#    illegalLetters = [1 for letter in word if ord(letter) not in range(32, 127)]
    illegalLetters = [1 for letter in word if (ord(letter) < 32 or ord(letter) > 126)]

    if len(illegalLetters) > 0:
        return True
    return False

def contain_only_punc_in_word(word):
    if re.search("[a-zA-Z0-9]", word):
        return False
    return True

# version-20160512 
# allow $ appear in words ($cashtag in corpus)
def strip_nonLetter_in_word(word):
    if re.findall("[^a-zA-Z0-9$]", word): # contain some punctuations
        word = re.sub("^[^a-zA-Z0-9$]*","", word) # start with punc
        word = re.sub("[^a-zA-Z0-9$]*$","", word) # end with punc
    return word


def parseArgs(args):
    textFileName = getArg(args, "-text")
    if textFileName is None:
        sys.exit(0)
    outFileName = getArg(args, "-out")
    return textFileName, outFileName


#############################
if __name__ == "__main__":
    print "Usage: python preProcessTweetText.py -text tweetFileName [-out tweetTextFileName]"
    print "Program starts at time:" + str(time.asctime())

    [textFileName, outFileName] = parseArgs(sys.argv)

    tweetTextCleaning_infile(textFileName, outFileName)

    print "Program ends at time:" + str(time.asctime())
