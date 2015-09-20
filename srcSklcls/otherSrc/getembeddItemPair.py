import time
import re
import os
import sys
import math
import cPickle


############################
## load frame element embedding (vector)
def getlocalVec(filename, unitHash):
    vecHash = {}
    vecfile = file(filename)
    lineIdx = 1
    firstLine = vecfile.readline()[:-1].split(" ")
    wnum = firstLine[0]
    vecLen = firstLine[1]
    while 1:
        lineStr = vecfile.readline()
        if not lineStr:
            print "Loading done. [wnum, vecLen] ",firstLine, " vecHash: ", len(vecHash), " realLen: ", len(vecHash.values()[0]), " at ", str(time.asctime())
            break
        if lineIdx == 1:
            lineIdx += 1
            continue
        arr = lineStr[:-1].strip().split(" ")

        # load global vec
        #vecHash[arr[0]] = arr[1:]

        # load local vec
        if arr[0] in unitHash:
            vecHash[arr[0]] = arr[1:]

        lineIdx += 1
    vecfile.close()
    return vecHash

############################
## cluster Event Segment
def getItemPair(dataFilePath, unitHash):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        #if item.find("skl_2013-01") != 0:
        if item.find("relSkl_2013-01") != 0:
            continue

        tStr = item[-2:]
        if tStr != Day:
            continue
        print "### Processing " + item
        print "Time window: " + tStr

        # calculate similarity
        segPairHash = {}
        segList = sorted(unitHash.items(), key = lambda a:a[1])
        segNum = len(unitHash)
        for i in range(0,segNum):
            for j in range(i+1,segNum):
                item1 = segList[i][0]
                item2 = segList[j][0]
                segId1 = segList[i][1]
                segId2 = segList[j][1]
                segPair = str(segId1) + "|" + str(segId2)

                # cosine similarity using embedding vectors
                sim = cosineSim(item1, item2)
                segPairHash[segPair] = sim
                

        segPairFile = file(dataFilePath + "segPairFile" + tStr, "w")
        cPickle.dump(unitHash, segPairFile)
        cPickle.dump(segPairHash, segPairFile)
        segPairFile.close()


def cosineSim(item1, item2):
    vec1 = None
    vec2 = None
    if item1 in vecHash:
        vec1 = vecHash[item1]
    if item2 in vecHash:
        vec2 = vecHash[item2]
    if (vec1 is None) or (vec2 is None):
        return None
    else:
        sim = 0.0
        try:
            vec1 = [float(val) for val in vec1]
        except Exception:
            print vec1
        try:
            vec2 = [float(val) for val in vec2]
        except Exception:
            print vec2
        for i in range(len(vec1)):
            sim += vec1[i]*vec2[i]
        return sim


############################
## load event segments from file
def loadEvtseg(filePath):
    unitInvolvedHash = {}#sid:1
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st

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
        '''if unit == "love_you":
            print "1. example of unit: " + str(unitHash['love_you']) + " " + str(unitDFHash[unitHash['love_you']])
            print contentArr
        '''
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))

    #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
    return unitHash, unitDFHash, unitInvolvedHash

############################
## main Function
global Day, UNIT, btyEleFilename, vecHash
if len(sys.argv) == 2:
    Day = sys.argv[1]
elif len(sys.argv) == 3:
    Day = sys.argv[1]
    btyEleFilename = sys.argv[2]
else:
    print "Usage: python getSklpair.py day [btyElementfilename]"
    sys.exit()

print "###program starts at " + str(time.asctime())
dataFilePath = r"../exp/w2v/"

UNIT = "skl"
'''
[unitHash, unitDFHash, unitInvolvedHash] = loadEvtseg(sys.argv[1])
print "\n".join(sorted(unitHash.keys()))
sys.exit()
'''

# load extracted event segments in tStr
if len(sys.argv) == 3:
    eventSegFilePath = btyEleFilename
else:
    eventSegFilePath = dataFilePath + "eventskl" + Day
#[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
[unitHash, unitDFHash, unitInvolvedHash] = loadEvtseg(eventSegFilePath)

#vecFilename = dataFilePath+"w2vText.skipneg5.tvec"
vecFilename = dataFilePath+"w2v_2013-01-01.cbowhs.tvec"
vecHash = getlocalVec(vecFilename, unitHash)
## test
missedWords = [w for w in unitHash if w not in vecHash]
print "..Words without embedding", missedWords

getItemPair(dataFilePath, unitHash)

print "###program ends at " + str(time.asctime())
