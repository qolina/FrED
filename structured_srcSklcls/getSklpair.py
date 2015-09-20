#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle
import sys
from copy import deepcopy

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeList, edgeHash):
        self.nodeList = nodeList
        self.edgeHash = edgeHash

class Skeleton:
    def __init__(self, id, relSet):
        self.id = id
        self.relSet = relSet
    def setDF(self, df):
        self.df = df

############################
## load df of word from file into wordDFHash
def loadDF(dfFilePath):
    wordDFHash = {}
    dfFile = file(dfFilePath)
    wordDFHash = cPickle.load(dfFile)
    print "### " + str(time.asctime()) + str(len(wordDFHash)) + " " + UNIT + "s' df values are loaded from " + dfFile.name
    dfFile.close()
    return wordDFHash

############################
## load bursty skeletons from file
def loadbtySkl(filePath):
    unitInvolvedHash = {}#sid:1
    unitContentHash = {}#sid:skeleton
    inFile = file(filePath)
    unitInvolvedHash = cPickle.load(inFile)
    unitContentHash = cPickle.load(inFile)
    inFile.close()
    print "### " + str(time.asctime()) + str(len(unitContentHash)) + " bursty " + UNIT + "s values are loaded from " + inFile.name + " with Involved skeleton number: " + str(len(unitInvolvedHash))
    return unitInvolvedHash, unitContentHash

############################
## load tweetID-createdHour
def loadTime(filepath):
    inFile = file(filepath,"r")
    attHash = cPickle.load(inFile)
    timeHash = dict([(tid, attHash[tid]["Time"]) for tid in attHash]) 
    print "## " + str(time.asctime()) + " Loading done (hour of tweets). " + filepath
    inFile.close()
    return timeHash

############################
## load tweetID-usrID
def loadID(filepath):
    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap

############################
def loadRelPair(filePath):
    relPairHash = {} #relpair:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    relPairFile = file(filePath, "rb")
    tweetNum_day = cPickle.load(relPairFile)
    relPairHash = cPickle.load(relPairFile)
    relPairFile.close()
    print "## loading done. " + str(time.asctime()) + filePath
    return tweetNum_day, relPairHash

############################
def loadText(tStr, unitInvolvedHash):
    unitTextHash = {} #sid:text
    textFile = file(r"../data/201301_preprocess/text_2013-01-"+tStr)
    idx = 0
    while True:
        lineStr = textFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        if len(lineStr) <= 0:
            break

        sid = tStr + str(idx)
        if sid in unitInvolvedHash:
            unitTextHash[sid] = lineStr
        idx += 1

    print "## loading done. " + str(time.asctime()) + textFile.name
    textFile.close()
    return unitTextHash

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

    #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
    #[GUA] segmentDFHash mapping: twitterNum
    docArr = text.split("###")
    docId = 0
    # one word(unigram) is a feature, not segment
    feaTFHash = {}
    feaAppHash = {}
    featureHash = {}
    norm = 0.0
    for docStr in docArr:
        docId += 1
        segArr = docStr.split("|")
        for segment in segArr:

            #[GUA] appHash mapping: docId -> 1/0
            #[GUA] feaAppHash mapping: segment -> [docId -> 1/0]
            #[GUA] feaTFHash mapping: segment -> segmentFreq
            wordArr = segment.split(" ")
            for word in wordArr:
                if len(word) < 1:
                    continue
                appHash = {}
                if word in feaTFHash:
                    feaTFHash[word] += 1
                    appHash = feaAppHash[word]
                else:
                    feaTFHash[word] = 1
                appHash[docId] = 1
                feaAppHash[word] = appHash
    for word in feaTFHash:
#        tf = math.log(feaTFHash[word]*1.0 + 1.0)
#        idf = math.log((docNum + 1.0)/(len(feaAppHash[word]) + 0.5))
        tf = feaTFHash[word] 
#        if word not in wordDFHash:
#            print "Error! word " + word + " not appeared in wordDFHash"
#        print "**" + word + " df: " + str(wordDFHash[word])
        idf = math.log(TWEETNUM/wordDFHash[word])
        weight = tf*idf
        featureHash[word] = weight
        norm += weight * weight
    norm = math.sqrt(norm)

    #[GUA] featureHash mapping: segment -> tf-idf / interval
    return featureHash, norm

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
def getSklPairSim(dataFilePath, M, toolDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("skl_2013") != 0:
            continue
        tStr = item[-2:]
        if tStr != Day:
            continue
        print "### Processing " + item
        print "Time window: " + tStr

        # load segged tweet files in time window tStr
        sklFile = file(dataFilePath + item)
        # load extracted event segments in tStr
        burstySklFilePath = dataFilePath + "bursty" + UNIT + tStr
        #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
        [unitInvolvedHash, unitContentHash] = loadbtySkl(burstySklFilePath)

        # load extracted createdHour of tweet in tStr
        tweetTimeFilePath = toolDirPath + "tweetSocialFeature" + tStr
        #[GUA] usrHour name: tweetSocialFeature + TimeWindow, format: twitterID -> hourStr([00, 23])
        timeHash = loadTime(tweetTimeFilePath)
        IDmapFilePath = dataFilePath + "IDmap_2013-01-" + tStr
        IDmap = loadID(IDmapFilePath)
        relPairPath = dataFilePath + "relPairs_2013-01-"+tStr
        [tweetNum_day, relPairHash] = loadRelPair(relPairPath)
        unitTextHash = loadText(tStr, unitInvolvedHash)
        dfFilePath = toolDirPath + "wordDF"
        global wordDFHash
        wordDFHash = loadDF(dfFilePath)
        m_docNumHash = {} # format: m->docNum
        sklDFHash = {}
        sklTVecHash = {}
        sklVecNormHash = {}
        N_t = 0
        while 1:
            try:
                skeleton = cPickle.load(sklFile)
            except EOFError:
                print "-loading ends(bursty skeleton pair similarity)." + item
                break
            # calculate m_docNum
            sid = skeleton.id
            hour = int(timeHash[IDmap[int(sid[2:])]])
            m = hour/M
            if m in m_docNumHash:
                m_docNumHash[m] += 1
            else:
                m_docNumHash[m] = 1

            if skeleton.id not in unitContentHash:
                continue
            relSet = skeleton.relSet

            # calculate f(s,t)
            sdf_hash = {}
            for idx1 in xrange(len(relSet)):
                for idx2 in xrange(idx1+1, len(relSet)):
                    smallRel = relSet[idx1]
                    bigRel = relSet[idx2]
                    if cmp(smallRel, bigRel) > 0:
                        smallRel = relSet[idx2]
                        bigRel = relSet[idx1]
                    key = "###".join(set([smallRel, bigRel]))
                    df_hash = relPairHash[key] # only one day
                    for day in df_hash.keys():
                        df_t_hash = df_hash[day]
                        if day in sdf_hash:
                            sdf_hash[day].update(df_t_hash)
                        else:
                            sdf_hash[day] = deepcopy(df_t_hash)

            # calculate f_t(s,m)
            mdfhash = {} #format: m->f_t(s,m)
            mnormhash = {} #format: m->textNorm
            mfeatureHash = {}
            for id in sdf_hash[tStr]:
                hour = int(timeHash[IDmap[int(id[2:])]])
                if hour/M in mdfhash:
                    mdfhash[hour/M].update(dict([(id, 1)]))
                else:
                    mdfhash[hour/M] = dict([(id, 1)])
            sklDFHash[sid] = mdfhash
            N_t += 1
            if N_t % 100 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        print "## m_docNums: " + str(m_docNumHash) + str(time.asctime())
        # calculate textStrings where bursty skeleton appears in
        for sid in unitContentHash: 
            mdfhash = sklDFHash[sid]
            for m in mdfhash.keys():
                textStr = "###".join(list([unitTextHash[id] for id in mdfhash[m]]))
                [featureHash, norm] = toTFIDFVector(textStr, m_docNumHash[m])
                mnormhash[m] = norm
                mfeatureHash[m] = featureHash
                mdfhash[m] = len(mdfhash[m])
            sklTVecHash[sid] = mfeatureHash
            sklVecNormHash[sid] = mnormhash
        print "### " + str(time.asctime()) + " " + str(len(sklVecNormHash)) + " tweets' textString are obtained!"

        sklPairFile = file(dataFilePath + "sklPairFile_right" + tStr, "w")
        cPickle.dump(unitContentHash, sklPairFile)
        # calculate the similarities between sklpair
        sklPairHash = {} # all edges in graph
        sklList = sorted(sklDFHash.keys())
        sklNum = len(sklList)
        sklpairId = 0
        for i in xrange(0,sklNum):
            for j in xrange(i+1,sklNum):
                sid1 = sklList[i]
                sid2 = sklList[j]
                sklPair = str(sid1) + "|" + str(sid2)
                sklpairId += 1

                sklPairHash[sklPair] = 0.0
                for m in xrange(0, 12):
                    if (m not in sklVecNormHash[sid1]) | (m not in sklVecNormHash[sid2]):
                        sim = 0
                    else:
                        tSim = textSim(sklTVecHash[sid1][m], sklVecNormHash[sid1][m], sklTVecHash[sid2][m], sklVecNormHash[sid2][m])
                        sim = tSim * (sklDFHash[sid1][m]*1.0/unitContentHash[sid1].df) * (sklDFHash[sid2][m]*1.0/unitContentHash[sid2].df)
                    sklPairHash[sklPair] += sim
    #            print "similarity of segPair " + segPair + " : " + str(sim),
    #            print " Text similarity: " + str(tSim)
                if sklpairId % 100 == 0:
                    print "### " + str(time.asctime()) + " " + str(sklpairId) + " skl pairs are processed!"
            
        cPickle.dump(sklPairHash, sklPairFile)
        print "### " + str(time.asctime()) + " " + str(len(unitContentHash)) + " event skeletons in " + item + " are loaded. With skeletons pairs Num: " + str(len(sklPairHash))
        
        sklPairFile.close()

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
global Day, UNIT
print "###program starts at " + str(time.asctime())
dataFilePath = r"../parsedTweet/sklDataV4/"
toolDirPath = r"../Tools/"
UNIT = "skl"
if len(sys.argv) == 2:
    Day = sys.argv[1]
else:
    print "Usage: python getSklpair.py day"
    sys.exit()

TWEETNUM = 29359304 # sum(tweetNum_days)
M = 2

getSklPairSim(dataFilePath, M, toolDirPath)

print "###program ends at " + str(time.asctime())
