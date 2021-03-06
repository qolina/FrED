#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

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
    '''
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
    '''
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
## load tweetID-usrID
def loadID(filepath):
    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap

## cluster Event Segment
def getEventFrm(dataFilePath, toolDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("relSkl_2013-01") != 0:
            continue
        tStr = item[-2:]
        if tStr != Day:
            continue

        print "### Processing " + item
        print "Time window: " + tStr
        N_t = 0 # tweetNum appeared in time window tStr
        # load segged tweet files in time window tStr
        seggedFile = file(dataFilePath + item)
        #eventSegFilePath = dataFilePath + "eventskl" + tStr
        eventSegFilePath = btySklFileName

        # load extracted event segments in tStr
        [unitHash, unitDFHash, unitInvolvedHash] = loadEvtseg(eventSegFilePath)
        #print "\n".join(sorted(unitHash.keys()))

        frmHash = {} # bursty frame Hash
        frmInvolvedHash = {} # bursty frame involved tweets

        IDmapFilePath = dataFilePath + "IDmap_2013-01-" + tStr
        IDmap = loadID(IDmapFilePath)

        lineIdx = 0
        while 1:
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            lineIdx += 1

            #print "************ " + str(lineIdx)
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            tweIDOri = IDmap[int(tweetIDstr[2:])]

            textArr = contentArr[1].split(" ")
            #print lineStr
            for fm in textArr:
                ## element without location infor
                #eleArr = fm.strip("|").split("|")
                #btyele = [ele for ele in eleArr if ele in unitHash]

                ## element with location infor
                eleArr = fm.split("|")
                #newEle = [eleArr[i]+"_"+str(i) for i in range(3)] # v6
                newEle = [eleArr[0], eleArr[1]+"_1", eleArr[2]] #v7
                eleArr = newEle
                btyele = [ele for ele in eleArr if ele in unitHash]

                # current frame is bursty frame
                # v1: one element is bursty
                # v2: more than 50% element is bursty
                #if len(btyele) >= 0.5*len(eleArr):
                # v3: all element is bursty
                #if len(btyele) == len(eleArr):
                # v5: complete frames: all 3 element is bursty, and keep top K
                if len(btyele) == 3:
                    if fm in frmHash:
                        hash = frmHash[fm]
                    else:
                        hash = {}
                    hash[tweetIDstr] = 1
                    frmHash[fm] = hash

                    if len(fm.split("|")) != 3:
                        print "######BtyFrm: " + fm + " ---> " + str(btyele)
                        print lineStr
                    if tweIDOri not in frmInvolvedHash:
                        frmInvolvedHash[tweIDOri] = 1

            if lineIdx % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(lineIdx) + " tweets are processed!"
        print "## " + str(len(frmInvolvedHash)) + " tweets contain bursty frames: " + str(len(frmHash))

        '''
        ## v4: keep top N frames according to wikiScore
        wikiHash = dict([(frm, frmNewWorth(frm)) for frm in frmHash])
        K = 5000 #v8
        #K = 2000 #v9
        frmHash = getTopItems(wikiHash, K)
        for item in sorted(wikiHash.items(), key = lambda a:a[1], reverse = True):
            print item
        '''

        '''
        # when frmHash[frm] = btyEleArr
        frm1List = [frm for frm in frmHash if len(frm.strip("|").split("|"))==1]
        frm2List = [frm for frm in frmHash if len(frm.strip("|").split("|"))==2]
        frm3List = [frm for frm in frmHash if len(frm.strip("|").split("|"))==3]
        len1 = len(frm1List)
        len2 = len(frm2List)
        len3 = len(frm3List)
        print "## length of frames: " + str([len1, len2, len3])
        for frm in sorted(frm1List):
            print "######BtyFrm: " + frm + " ---> " + str(frmHash[frm])
        for frm in sorted(frm2List):
            print "######BtyFrm: " + frm + " ---> " + str(frmHash[frm])
        for frm in sorted(frm3List):
            print "######BtyFrm: " + frm + " ---> " + str(frmHash[frm])
        '''

        frmHash = dict([(frm, len(frmHash[frm])) for frm in frmHash])
        frmStrList = []
        for frm in frmHash:
            f_st = frmHash[frm]
            frmStrList.append(str(f_st) + "\t" + frm + "\n")

        #eventSegFile = file(dataFilePath + "event" + UNIT + tStr, "w")
        eventSegFile = file(btyFrmName, "w")
        #cPickle.dump(sorted(frmHash.keys()), eventSegFile) # v1
        cPickle.dump(frmStrList, eventSegFile)
        cPickle.dump(frmInvolvedHash, eventSegFile)
        print "### " + str(time.asctime()) + " " + str(len(frmHash)) + " frames are stored(ranked) into " + eventSegFile.name
        eventSegFile.close()
        seggedFile.close()

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    if K < len(sortedList):
        sortedList = sortedList[0:K]
    sampleHash = dict([(key[0], key[1]) for key in sortedList])
    return sampleHash

############################
## load wikiGram
def loadWiki(filepath):
    global wikiProbHash
    inFile = file(filepath,"r")
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = float(lineStr[0:lineStr.find(" ")])
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
#        print gram + "\t" + str(prob)
        wikiProbHash[gram] = prob
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(wikiProbHash)) + " wiki grams' prob are loaded from " + inFile.name

############################
## newsWorthiness
def frmNewWorth(frm):
    frm = frm.strip("|")
    segArr = frm.split("|")
    worthArr = [segNewWorth(seg) for seg in segArr]
    return sum(worthArr)/len(worthArr)

def segNewWorth(segment):
    wordArr = segment.split("_")
    wordNum = len(wordArr)
    if wordNum == 1:
        if segment in wikiProbHash:
            return math.exp(wikiProbHash[segment])
        else:
            return 0.0
    maxProb = 0.0

    for i in range(0, wordNum):
        for j in range(i+1, wordNum+1):
            subArr = wordArr[i:j]
            prob = 0.0
            subS = " ".join(subArr)
            if subS in wikiProbHash:
                prob = math.exp(wikiProbHash[subS]) - 1.0
            if prob > maxProb:
                maxProb = prob
#    if maxProb > 0:
#        print "Newsworthiness of " + segment + " : " + str(maxProb)
    return maxProb

############################
## main Function
global Day, UNIT, btySklFileName, btyFrmName
if len(sys.argv) >= 2:
    Day = sys.argv[1]
    btySklFileName = sys.argv[2]
    btyFrmName = sys.argv[3]
else:
    print "Usage: python getbtyFrm.py day btySklFileName btyfrmFilename"
    sys.exit()

print "###program starts at " + str(time.asctime())
dataFilePath = r"../parsedTweet/"
toolDirPath = r"../Tools/"
UNIT = "frm"

getEventFrm(dataFilePath, toolDirPath)

print "###program ends at " + str(time.asctime())
