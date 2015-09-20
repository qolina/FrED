#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle
import scipy.spatial.distance as dist
import numpy

############################
## load event segments from file
def loadEvtseg(filePath):
    unitInvolvedHash = {}#sid:1
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st

    inFile = file(filePath)
    segStrList = cPickle.load(inFile)
    unitInvolvedHash = cPickle.load(inFile)
    unitID = 0
    for lineStr in segStrList:
        lineStr = re.sub(r'\n', '', lineStr)
        contentArr = lineStr.split("\t")
        #print contentArr[2]
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event segs and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))
    return unitHash, unitDFHash, unitInvolvedHash

############################
## load frame element embedding (vector)
def getdlVec(filename, unitHash):
    vecHash = {}
    vecfile = file(filename)
    lineIdx = 1
    firstLine = vecfile.readline()[:-1].split(" ")
    wnum = firstLine[0]
    vecLen = firstLine[1]
    while 1:
        lineStr = vecfile.readline()
        if not lineStr:
            print "Loading units' vectors done. [wnum, vecLen] ",firstLine, " vecHash: ", len(vecHash), 
            if unitHash is None:
                print " NoLocalUnits",
            else:
                print " with localUnits: ", len(unitHash),
            print " at ", str(time.asctime())
            break
        if lineIdx == 1: # firstline: [\s]
            lineIdx += 1
            continue
        arr = lineStr[:-1].strip().split(" ")

        #vec = numpy.array(arr[1:])
        #vec.astype(float)
        vec = [float(val) for val in arr[1:]]

        if unitHash is None:
            # load global vec
            vecHash[arr[0]] = vec
        else:
            # load local vec
            if arr[0] in unitHash:
                vecHash[arr[0]] = vec

        lineIdx += 1
    vecfile.close()
    return vecHash


############################
## whether two unit can be matched. cosine similarity > threshould. unit is represented as distributed vector (word2vec)
def match(unit1, unit2):
    global maxSim, minSim
    arr1 = unit1.split("|")
    arr2 = unit2.split("|")
    simArr = [0.0] * 3
    for i in range(3):
        if (len(arr1[i])>1) and (len(arr2[i])>1):
            simArr[i] = cosineSim(arr1[i], arr2[i])
    
    #print "Sims between [", unit1, "] and [", unit2, "] ", simArr
    simSum = sum(simArr)
    if simSum is None:
        print "None sim between [", unit1, "] and [", unit2, "] ", simArr
        return False
    if simSum > maxSim:
        maxSim = simSum
    if simSum < minSim:
        minSim = simSum

    if simSum > matchThreshould:
        return True
    return False


def cosineSim(item1, item2):
    vec1 = None
    vec2 = None
    if item1 in vecHash:
        vec1 = vecHash[item1]
    if item2 in vecHash:
        vec2 = vecHash[item2]
    sim = 0.0
    if (vec1 is None) or (vec2 is None):
        #print "Vector is missing when calculating similarity.", [item1, item2]
        return sim
    else:
        '''
        # wrong vec1*vec2
        for i in range(len(vec1)):
            sim += vec1[i]*vec2[i]
        '''
        sim = 1.0 - dist.cosine(vec1, vec2)
    return sim


def updateDFDayHash(unitHash, unit, tStr, tweetIDstr):
    if unit in unitHash:
        df_hash = unitHash[unit]
        if tStr in df_hash:
            df_t_hash = df_hash[tStr]
        else:
            df_t_hash = {}
    else:
        df_hash = {}
        df_t_hash = {}
    df_t_hash[tweetIDstr] = 1
    df_hash[tStr] = df_t_hash
    unitHash[unit] = df_hash
    return unitHash
                        
############################
## load event segments from file
def loadBtyFrm(filePath):
    inFile = file(filePath)
    frmList = cPickle.load(inFile)
    inFile.close()
    frmHash = dict([(frmList[i], i) for i in range(len(frmList))])
    print "### " + str(time.asctime()) + " " + str(len(frmHash)) + " event units are loaded from " + inFile.name
    return frmHash

def getItems(filename):
    localItems = {}
    sklFile = file(filename)
    while 1:
        lineStr = sklFile.readline()
        if not lineStr:
            print "Local items obtained. ", len(localItems), " at ", time.asctime()
            break
        contentArr = lineStr[:-1].split("\t")
        if len(contentArr) < 2:
            continue
        
        textArr = re.sub("\|", " ", contentArr[1]).split(" ")
        for unit in textArr:
            if len(unit) < 1:
                continue
            if unit not in localItems:
                localItems[unit] = 1
    sklFile.close()
    return localItems

##################################
# main
print "###program starts at " + str(time.asctime())
global vecHash, matchThreshould
dataFilePath = r"../parsedTweet/"
matchThreshould = 2.0

if len(sys.argv) >= 2:
    dataFilePath = sys.argv[1]+"/"
    if len(sys.argv) == 3:
        matchThreshould == float(sys.argv[2])
else:
    print "Usage python estimatePs_smldata.py [datafilepath] [matchThreshould] (default: ../parsedTweet/ 2.0)"

vecFilename = dataFilePath+"w2vText.tvec"

# for debugging bursty methods
#btySklFileName = sys.argv[1]
#[sklHash, unitDFHash, unitInvolvedHash] = loadEvtseg(btySklFileName)
#print sklHash.keys()[0:20]

#frmHash = loadBtyFrm(sys.argv[1])
#print frmHash.keys()[0:20]
#sys.exit()

global maxSim, minSim
maxSim = -9999.0
minSim = 9999.0
similarItemHash = {}

UNIT = "skl"
unitHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
unitAppHash = {} #unit:apphash
windowHash = {} # timeSliceIdStr:tweetNum
psFile = file(dataFilePath + UNIT + "_ps", "w")
#dfFile = file(dataFilePath + UNIT + "_df", "w")
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
for item in fileList:
    if item.find("relSkl_2013") != 0:
        continue
    sklFile = file(dataFilePath + item)
    localItems = getItems(dataFilePath + item)
    vecHash = getdlVec(vecFilename, localItems)

    print "### Processing " + sklFile.name
    tStr = item[-2:]
    print "Time window: " + tStr
    tweetNum_t = 0
    while 1:
        #[GUA] seggedFile name: * + TimeWindow, format: twitterID, twitterText(segment|segment|...), ...
        lineStr = sklFile.readline()
        if not lineStr:
            break
        contentArr = lineStr[:-1].split("\t")
        if len(contentArr) < 2:
            continue
        tweetIDstr = contentArr[0]
        tweetText = contentArr[1]
        tweetNum_t += 1

        # use frame element
        #tweetText = re.sub("\|", " ", tweetText)

        textArr = tweetText.split(" ")
        '''
        # for frame structure
        # make record of location v6
        newTextArr = []
        for seg in textArr:
            eleArr = seg.split("|")
            #newEle = [eleArr[i]+"_"+str(i) for i in range(3) if len(eleArr[i])>1]

            # only distinguish verb and arg v7
            newEle = [eleArr[0], eleArr[1]+"_1", eleArr[2]]

            newTextArr.extend(newEle)
        #print newTextArr
        textArr = newTextArr
        '''
        for segment in textArr:
            unit = segment
            if len(unit) < 1:
                continue

            '''
            # for testing bursty methods
            #if re.sub(r"\|", "_", unit).strip("_") not in sklHash:
            if unit not in sklHash:
                continue
            '''

            # statistic segment df
            '''
            apphash = {}
            if unit in unitAppHash:
                apphash = unitAppHash[unit]
            apphash[tweetIDstr] = 1
            unitAppHash[unit] = apphash 
            '''

            # statistic segment ps
            # exact match pattern
            #unitHash = updateDFDayHash(unitHash, unit, tStr, tweetIDstr)

            # fuzzy/similar match pattern (sim > threshould)
            if len(unitHash) == 0:
                df_hash = {}
                df_t_hash = {}
                df_t_hash[tweetIDstr] = 1
                df_hash[tStr] = df_t_hash
                unitHash[unit] = df_hash
                continue

            if unit in similarItemHash:
                itemHash = similarItemHash[unit]
            else:
                itemHash = {}
            for cunit in unitHash:
                if cunit in itemHash:
                    unitHash = updateDFDayHash(unitHash, cunit, tStr, tweetIDstr)
                elif match(unit, cunit):
                    unitHash = updateDFDayHash(unitHash, cunit, tStr, tweetIDstr)
                    itemHash[cunit] = 1
                    #update existed cunit to similarItems
                    citemHash = {}
                    if cunit in similarItemHash:
                        citemHash = similarItemHash[cunit]
                    citemHash[unit] = 1
                    similarItemHash[cunit] = citemHash
            similarItemHash[unit] = itemHash

            unitHash = updateDFDayHash(unitHash, unit, tStr, tweetIDstr)
            '''
            if unit not in unitLengthHash:
                wordArr = segment.split("_")
                wordNum = len(wordArr)
                unitLengthHash[unit] = wordNum
            '''

        if tweetNum_t % 100 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash)), " [maxSim, minSim]: ", [maxSim, minSim], " similar Items: ", len(similarItemHash)
    windowHash[tStr] = tweetNum_t
    sklFile.close()
    # extra step: decrease memory cost
    for unit in unitHash:
        df_hash = unitHash[unit]
        if tStr not in df_hash:
            df_hash[tStr] = 0.0
        else:
            df_t_hash = df_hash[tStr]
            df_hash[tStr] = len(df_t_hash)*1.0
        unitHash[unit] = df_hash
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. unitNum: " + str(len(unitHash)), " [maxSim, minSim]: ", [maxSim, minSim]
print "### In total " + str(len(unitHash)) + " " + UNIT + "s are loaded!"

# writing to dffile
# write each day's tweetNumber into first line of df file
# Format:01 num1#02 num2#...#15 num15
sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
tweetNumStr = ""
for item in sortedTweetNumList:
    tStr = item[0]
    tweetNum = item[1]
    tweetNumStr += tStr + " " + str(tweetNum) + "#"
'''
dfFile.write(tweetNumStr[:-1] + "\n")
itemNum = 0
for unit in sorted(unitAppHash.keys()):
    itemNum += 1
    apphash = unitAppHash[unit]
    df = len(apphash)
    dfFile.write(str(df) + "\t" + unit + "\n")
dfFile.close()
print "### " + UNIT + "s' df values are written to " + dfFile.name
'''
## writing to unit ps file
unitNum = 0
for unit in sorted(unitHash.keys()):
    unitNum += 1
    df_hash = unitHash[unit]

    # for debugging
    fstStr = "\t".join([str(it[1]) for it in sorted(df_hash.items(), key = lambda a:a[0])])

    df_hash = dict([(t, df_hash[t]/windowHash[t]) for t in df_hash if df_hash[t]>0])
    l = len(df_hash)
    probTemp = sum(df_hash.values())
    prob = probTemp/l

    '''
    # for debugging
    #if df_hash["01"] > 2*prob:
    if l > 5:
        print unit + "\t",
        print str(windowHash["01"]*prob) + "\t",
        print fstStr
    else:
        psFile.write(str(prob) + "\t" + unit + "\t" + fstStr + "\n")
    '''
    psFile.write(str(prob) + "\t" + unit + "\n")

    if unitNum % 100000 == 0:
        print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

psFile.close()
print "### " + UNIT + "s' ps values are written to " + psFile.name

print "###program ends at " + str(time.asctime())
