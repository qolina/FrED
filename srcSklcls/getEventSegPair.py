#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

from getbtySkl import *

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeList, edgeHash):
        self.nodeList = nodeList
        self.edgeHash = edgeHash

############################
## load df of word from file into wordDFHash
def loadDF(dfFilePath):
    global wordDFHash
    dfFile = file(dfFilePath)
    wordDFHash = cPickle.load(dfFile)
    #print sorted(wordDFHash.items(), key = lambda a:a[1], reverse = True)[0:50]
    print "### " + str(time.asctime()) + str(len(wordDFHash)) + " " + UNIT + "s' df values are loaded from " + dfFile.name
    dfFile.close()
    return wordDFHash

############################
## load df from file
def loadDFOld(dfFilePath):
    #global wordDFHash, TWEETNUM 
    windowHash = {}
    dfFile = file(dfFilePath)
    firstLine = dfFile.readline()
# Format:01 num1#02 num2#...#15 num15
    itemArr = firstLine.split("#")
    for item in itemArr:
        arr = item.split(" ")
        tStr = arr[0]
        tweetNum = int(arr[1])
        windowHash[tStr] = tweetNum
    print "### Loaded tweets Num in each time window: "
    print sorted(windowHash.items(), key = lambda a:a[0])
    TWEETNUM = sum(windowHash.values())
    while True:
        lineStr = dfFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        df = int(contentArr[0])
        word = contentArr[1]
        wordDFHash[word] = df
#        print "Word: #" + word + "# df: " + str(df)
    dfFile.close()
    print "### " + str(len(wordDFHash)) + " words' df values are loaded from " + dfFile.name

############################
## load event segments from file
def loadEvtseg(filePath):
    unitInvolvedHash = {}#sid:1
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st
    unitScoreHash = {} # segmentID: score

    #[GUA] eventSegFile name: eventSeg + TimeWindow, format: f_st(twitterNum / segment, timeWindow), wb_st(bursty score), segment
    inFile = file(filePath)
    segStrList = cPickle.load(inFile)
    unitInvolvedHash = cPickle.load(inFile)
    unitID = 0
    #while True:
        #lineStr = inFile.readline()
        #lineStr = re.sub(r'\n', ' ', lineStr)
        #lineStr = lineStr.strip()
        #if len(lineStr) <= 0:
            #break
    for lineStr in segStrList:
        lineStr = re.sub(r'\n', '', lineStr)
        contentArr = lineStr.split("\t")
        #print contentArr[2]
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        #unitScoreHash[unitID] = float(contentArr[1]) # one score
        unitScoreHash[unitID] = contentArr[1] # two score
        '''if unit == "love_you":
            print "1. example of unit: " + str(unitHash['love_you']) + " " + str(unitDFHash[unitHash['love_you']])
            print contentArr
        '''
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))

    #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
    return unitHash, unitDFHash, unitInvolvedHash, unitScoreHash

def newHour(hourStr):
    hour = int(hourStr)
    if hour >= 16:
        return str(hour-16)
    else:
        return str(hour+8)


############################
## load tweetID-createdHour
def loadTime(filepath, tweIdFileName):
    inFile = file(filepath,"r")
    attHash = cPickle.load(inFile)
    inFile.close()
    print "## " + str(time.asctime()) + " Loading done (hour of tweets). " + filepath

    if tweIdFileName:
        tweIdList = getTweetID(tweIdFileName)
        timeHash = dict([(tid, attHash[tid]["Time"]) for tid in tweIdList if tid in attHash]) 
    else:
        #timeHash = dict([(tid, newHour(attHash[tid]["Time"])) for tid in attHash]) # temporally modified
        timeHash = dict([(tid, attHash[tid]["Time"]) for tid in attHash])  # in version 1

    print "## " + str(time.asctime()) + " Loading done. timeOfTwe" , len(timeHash)

#    hourHash = dict([(i, 0) for i in range(24)])
#    for id in timeHash:
#        hour = int(timeHash[id])
#        hourHash[hour] += 1
#
#    print "## tweetNum in each hour: " + str(sorted(hourHash.items(), key = lambda a:a[0]))
    return timeHash

############################
## calculate similarity of two segments
def calSegPairSim(segAppHash, segTextHash, unitDFHash, docNum):
    segPairHash = {}
    segfWeiHash = {}
    segTVecHash = {}
    segVecNormHash = {}
    for segId in segAppHash:

        #[GUA] m_eSegAppHash mapping: segID -> [twitterID -> 1/0]
        #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
        #[GUA] segmentDFHash mapping: segID -> f_st
        #[GUA] segmentDFHash mapping: twitterNum
        f_st = unitDFHash[segId]
        f_stm = len(segAppHash[segId])

        #[GUA] f_st(twitterNum / segment, timeWindow), f_stm(twitterNum / segment, interval)
        f_weight = f_stm * 1.0 / f_st
        segfWeiHash[segId] = f_weight
#        print "###" + str(segId) + " fweight: " + str(f_weight),
#        print " f_stm: " + str(f_stm) + " f_st: " + str(f_st)
        segText = segTextHash[segId]
        if segText.endswith("###"):
            segText = segText[:-3]
#        print "Appeared Text: " + segText[0:50]

        #[GUA] featureHash mapping: segment -> tf-idf 
        [featureHash, norm] = toTFIDFVector(segText, docNum)
        segTVecHash[segId] = featureHash
        segVecNormHash[segId] = norm
#        print "###" + str(segId) + " featureNum: " + str(len(featureHash)),
#        print " norm: " + str(norm)
#        print featureHash

    # calculate similarity
    segList = sorted(segfWeiHash.keys())
    segNum = len(segList)
    for i in range(0,segNum):
        for j in range(i+1,segNum):
            segId1 = segList[i]
            segId2 = segList[j]
            segPair = str(segId1) + "|" + str(segId2)
            tSim = textSim(segTVecHash[segId1], segVecNormHash[segId1], segTVecHash[segId2], segVecNormHash[segId2])
            sim = segfWeiHash[segId1] * segfWeiHash[segId2] * tSim
            segPairHash[segPair] = sim
#            print "similarity of segPair " + segPair + " : " + str(sim),
#            print " Text similarity: " + str(tSim)
            
    return segPairHash 

############################
## represent text string into tf-idf vector
def textSim(feaHash1, norm1, feaHash2, norm2):
    tSim = 0.0
    for seg in feaHash1:
        if seg in feaHash2:
            w1 = feaHash1[seg]
            w2 = feaHash2[seg]
            tSim += w1 * w2
    tSim = tSim / (norm1 * norm2)
#    print "text similarity: " + str(tSim)
#    if tSim == 0.0:
#        print "Error! textSimilarity is 0!"
#        print "vec1: " + str(norm1) + " ",
#        print feaHash1
#        print "vec2: " + str(norm2) + " ",
#        print feaHash2
    return tSim

############################
## represent text string into tf-idf vector
def toTFIDFVector(text, docNum):

    #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment segment ...)###twitterText###...
    #[GUA] segmentDFHash mapping: twitterNum
    docArr = text.split("###")
    docId = 0
    # one word(unigram) is a feature, not segment
    feaTFHash = {}
    #feaAppHash = {}
    featureHash = {}
    norm = 0.0
    for docStr in docArr:
        docId += 1
        segArr = docStr.split(" ")
        for segment in segArr:

            #[GUA] appHash mapping: docId -> 1/0
            #[GUA] feaAppHash mapping: segment -> [docId -> 1/0]
            #[GUA] feaTFHash mapping: segment -> segmentFreq
            wordArr = segment.split(" ")
            for word in wordArr:
                #appHash = {}
                if len(word) < 1:
                    continue
                if word in feaTFHash:
                    feaTFHash[word] += 1
                    #appHash = feaAppHash[word]
                else:
                    feaTFHash[word] = 1
                #appHash[docId] = 1
                #feaAppHash[word] = appHash
    for word in feaTFHash:
#        tf = math.log(feaTFHash[word]*1.0 + 1.0)
#        idf = math.log((docNum + 1.0)/(len(feaAppHash[word]) + 0.5))
        tf = feaTFHash[word] 
        if word not in wordDFHash:
            print "## word not existed in wordDFhash: " + word
            continue
        idf = math.log(TWEETNUM/wordDFHash[word])
        weight = tf*idf
        featureHash[word] = weight
        norm += weight * weight
    norm = math.sqrt(norm)

    #[GUA] featureHash mapping: segment -> tf-idf / interval
    return featureHash, norm

############################
def loadText(textFilePath, IDmap, unitInvolvedHash):
    unitTextHash = {} #sid:text (word word word)
    textFile = file(textFilePath)

    while True:
        lineStr = textFile.readline()
        if not lineStr:
            print "## loading text done. " + str(time.asctime()) + textFile.name
            break
        arr = lineStr[:-1].strip().split("\t")
        sid = arr[0]

        if len(sid) != 18:
            tid = IDmap[int(sid[2:])]
        else:
            tid = sid

        if tid in unitInvolvedHash:
            text = re.sub(r"\|", " ", arr[-1])
            unitTextHash[sid] = text 
    textFile.close()
    return unitTextHash

def loadOriText(oriTweetTextDir, tStr, IDmap, unitInvolvedHash):
    unitTextHash = {} #sid:text (word word word...)
#    textFile = file(r"../data/201301_preprocess/text_2013-01-"+tStr)
    textFile = file(oriTweetTextDir + r"/tweetText"+tStr)
    idx = 0
    while True:
        lineStr = textFile.readline().lower()
        if not lineStr:
            print "## loading text done. " + str(time.asctime()) + textFile.name, " len(unitTextHash)", len(unitTextHash)
            break
        lineStr = lineStr[:-1]

        sid = tStr + str(idx)
        tid = IDmap[idx]
        if tid in unitInvolvedHash:
            unitTextHash[sid] = lineStr
        idx += 1
    textFile.close()
    return unitTextHash

############################
## merge two hash: add smallHash's content into bigHash
def merge(smallHash, bigHash):
    print "Incorporate " + str(len(smallHash)) + " pairs into " + str(len(bigHash)),
    newNum = 0
    changeNum = 0
    for pair in smallHash:
        if pair in bigHash:
            bigHash[pair] += smallHash[pair]
            changeNum += 1
        else:
            bigHash[pair] = smallHash[pair]
            newNum += 1
    print " with newNum/changedNum " + str(newNum) + "/" + str(changeNum)
    return bigHash

############################
## cluster Event Segment
def geteSegPairSim(dataFilePath, M, idmapFileDir, tweetSocialInfoDir, oriTweetTextDir):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        #if item.find("skl_2013-01") != 0:
        #if item.find("relSkl_") != 0:
        if item.find("segged_tweet") != 0:
            continue

        #[GUA] Time window
        tStr = item[-2:]
        if tStr != Day:
            continue
        print "### Processing " + item
        print "Time window: " + tStr
        N_t = 0 # tweetNum appeared in time window tStr
        # load segged tweet files in time window tStr
        seggedFile = file(dataFilePath + item)

        # load extracted event segments in tStr
        if len(sys.argv) == 3:
            eventSegFilePath = btyEleFilename
        else:
            eventSegFilePath = dataFilePath + "event" + UNIT + tStr
        #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
        [unitHash, unitDFHash, unitInvolvedHash, unitScoreHash] = loadEvtseg(eventSegFilePath)

        # load extracted createdHour of tweet in tStr
        tweetTimeFilePath = tweetSocialInfoDir + "tweetSocialFeature" + tStr
        #[GUA] usrHour name: tweetSocialFeature + TimeWindow, format: twitterID -> hourStr([00, 23])
        #timeHash = loadTime(tweetTimeFilePath, dataFilePath+item)
        timeHash = loadTime(tweetTimeFilePath, None)

        IDmapFilePath = idmapFileDir + "IDmap_2015-05-" + tStr
        IDmap = loadID(IDmapFilePath)

        if UNIT == "skl":
            unitTextHash = loadOriText(oriTweetTextDir, tStr, IDmap, unitInvolvedHash)
        elif UNIT == "segment":
            unitTextHash = loadText(dataFilePath+item, IDmap, unitInvolvedHash)

        m = 0
        m_step = 24 / M # split time window tStr into M parts
        m_docNum = 0
        m_eSegAppHash = {} # event segments' appearHash in time interval m
        m_eSegTextHash = {} # event segments' appeared in Text in time interval m
        segPairHash = {} # all edges in graph
        while True:
            #[GUA] seggedFile name: * + TimeWindow, format: twitterID, *, twitterText(segment|segment|...), ...
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            if len(tweetIDstr) < 18:
                tweIDOri = IDmap[int(tweetIDstr[2:])]
            else:
                tweIDOri = tweetIDstr
            '''
            if len(contentArr) < 2:
                continue
            '''
            tweetText = contentArr[-1]
            if tweetIDstr in unitTextHash:
                tweTxtOri = unitTextHash[tweetIDstr]
            N_t += 1
            hourStr = timeHash.get(tweIDOri)
            if hourStr is None:
                continue
            hour = int(hourStr)
            #print tweetIDstr + " is created at hour: " + str(hour)
            if hour >= (m+m_step):
                print "### new interval time slice in tStr: " + str(hour) + " with previous tweet Num: " + str(m_docNum) + " bursty seg number: " + str(len(m_eSegTextHash))
                # end of one m interval

                #[GUA] m_eSegAppHash mapping: segID -> [twitterID -> 1/0]
                #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
                #[GUA] segmentDFHash mapping: segID -> f_st
                #[GUA] segmentDFHash mapping: twitterNum
                m_segPairHash = calSegPairSim(m_eSegAppHash, m_eSegTextHash, unitDFHash, m_docNum)
                segPairHash = merge(m_segPairHash, segPairHash)
                m_eSegAppHash.clear()
                m_eSegTextHash.clear()
                m_docNum = 0
                #m += m_step
                m = hour
            if hour < m:
                print "##!! tweet created time in chaos: " + str(hour) + " small than " + str(m)
                continue

            m_docNum += 1

            # for segment
            #tweetText = re.sub(" ", "_", tweetText)

            # for frame element
            tweetText = re.sub("\|", " ", tweetText)

            textArr = tweetText.strip().split(" ")
            for segment in textArr:
                #if segment == "love_you":
                #    print "corres to love_you: " + tweetText
                #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
                if segment not in unitHash:
                    continue
                # event segments
                segId = unitHash[segment]
                appTextStr = ""
                apphash = {}
                if segId in m_eSegAppHash:
                    apphash = m_eSegAppHash[segId]
                    appTextStr = m_eSegTextHash[segId]
                if tweIDOri in apphash:
                    continue
#                print segment, tweetIDstr, tweTxtOri
                appTextStr += tweTxtOri + "###"
                apphash[tweIDOri] = 1
                m_eSegAppHash[segId] = apphash
                m_eSegTextHash[segId] = appTextStr

            if N_t % 10000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed! segNum: " + str(len(m_eSegAppHash)) + " " + str(len(m_eSegTextHash))

        # last interval in tStr
        m_segPairHash = calSegPairSim(m_eSegAppHash, m_eSegTextHash, unitDFHash, m_docNum)
        segPairHash = merge(m_segPairHash, segPairHash)
        seggedFile.close()
        print "### " + str(time.asctime()) + " " + str(len(unitHash)) + " event segments in " + item + " are loaded. With segment pairs Num: " + str(len(segPairHash))
        
        segPairFile = file(dataFilePath + "segPairFile" + tStr, "w")
        cPickle.dump(unitHash, segPairFile)
        cPickle.dump(segPairHash, segPairFile)
        segPairFile.close()

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash

############################
## main Function
global Day, UNIT, TWEETNUM, btyEleFilename 
UNIT = "segment"
#UNIT = "skl"

if __name__=="__main__":
    if len(sys.argv) == 2:
        Day = sys.argv[1]
    elif len(sys.argv) == 3:
        Day = sys.argv[1]
        btyEleFilename = sys.argv[2]
    else:
        print "Usage: python getSklpair.py day [filename]"
        sys.exit()

    print "###program starts at " + str(time.asctime())


    #dataFilePath = r"/home/yxqin/corpus/data_twitter201301/201301_skl/"
    #dataFilePath = r"/home/yxqin/corpus/data_twitter201301/201301_segment/"
    #dataFilePath = r"/home/yxqin/corpus/data_stock201504/skl/"
    dataFilePath = r"/home/yxqin/corpus/data_stock201504/segment/"

    dfFilePathFromSkl = dataFilePath + "wordDF"
    #dfFilePathFromOriText = dataFilePath + "../201301_clean/"+ "wordDF"
    dfFilePathFromOriText = dataFilePath + "../clean/"+ "wordDF"

    #idmapFileDir = dataFilePath + "../201301_clean/"
    idmapFileDir = dataFilePath + "../clean/"
    #tweetSocialInfoDir = dataFilePath + "../201301_nonEng/"
    #tweetSocialInfoDir = dataFilePath + "../rawData/"
    tweetSocialInfoDir = dataFilePath + "../nonEng/"

    # used for calculate textSim of bursty feature(frame or segment)
    #oriTweetTextDir = dataFilePath + "../201301_preprocess"
    oriTweetTextDir = dataFilePath + "../preprocess"

    #TWEETNUM = 41293009 # tweetnum in text_2013-01-??
    #TWEETNUM = 28651435 # relSkl-2013-01-??

    #TWEETNUM = 19334497 # frED_relSkl-2013-01-01-15
    #TWEETNUM = 12608621 # frED_relSkl-2013-01-06-15

    #TWEETNUM = 31097528 # segged_tweetContentFile
    #TWEETNUM = 10888639 # segged_tweetContentFile 01-05
    #TWEETNUM = 20208889 # segged_tweetContentFile 06-15

    #TWEETNUM = 949229 # FrED_relSkl-2015-05-01-31
    TWEETNUM = 1199088 # FrED_segged_tweetCleanText-2015-05-01-31


    wordDFHash = {}
    M = 12


    loadDF(dfFilePathFromOriText)
    #loadDF(dfFilePathFromSkl)

    geteSegPairSim(dataFilePath, M, idmapFileDir, tweetSocialInfoDir, oriTweetTextDir)

    print "###program ends at " + str(time.asctime())
