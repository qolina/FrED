#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle
import sys
from copy import deepcopy
import operator

class Parsedtweet:
    def __init__(self, id, wordarr):
        self.id = id
        self.words = wordarr

## depRel in relSet: headWord__headTag||dependentWord__dependentTag||relname
class Skeleton:
    def __init__(self, id, relSet):
        self.id = id
        self.relSet = relSet
    def setDF(self, df):
        self.df = df

############################
## load ps from file
def loadslang(slangFilePath):
    global slangHash
    inFile = file(slangFilePath)
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("  -   ")
        sWord = contentArr[0].strip()
        rWord = contentArr[1].strip()
        slangHash[sWord] = rWord
    inFile.close()
    print "### " + str(len(slangHash)) + " slang words are loaded from " + inFile.name

############################
## load ps from file
def loadps(psFilePath):
    unitpsHash = {}
    psFile = file(psFilePath, "rb")
    unitpsHash = cPickle.load(psFile)
    print "### " + str(len(unitpsHash)) + " " + UNIT + "s' ps values are loaded from " + psFile.name
    psFile.close()
    return unitpsHash

############################
## load tweetID-usrID
def loadUsrId(filepath):
    usrFile = file(filepath,"r")
    attHash = cPickle.load(usrFile)
    tweIdToUsrIdHash = dict([(tid, attHash[tid]["Usr"]) for tid in attHash]) 
    usrFile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return tweIdToUsrIdHash

############################
## load tweetID-usrID
def loadID(filepath):
    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap

############################
## calculate sigmoid
def sigmoid(x):
    return 1.0/(1.0+math.exp(-x))

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
## getBurstySkeleton
def getBurstySkeleton(dataFilePath, toolDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("skl_2013-01") != 0:
            continue
        tStr = item[-2:]
        if len(sys.argv) == 2:
            Day = sys.argv[1]
            if Day != tStr:
                continue
        print "### Processing " + item
        print "Time window: " + tStr
        sklFile = file(dataFilePath + item)
        psFilePath = dataFilePath + UNIT + "_pshash_2013-01-"+tStr
        unitpsHash = loadps(psFilePath)
        relPairPath = dataFilePath + "relPairs_2013-01-"+tStr
        [tweetNum_day, relPairHash] = loadRelPair(relPairPath)
        burstySklFile = file(dataFilePath + "bursty" + UNIT + tStr, "wb")
        outSklFile = file(dataFilePath + "Output_bursty" + UNIT + tStr, "w")
        N_t = 0
        unitHash = {} #unitID:df_t_hash
        #df_t_hash --> tweetIDStr:1
        unitContentHash = {}
        unitInvolvedHash = {}
        btyUnitAppHash = {}
        unitUsrHash = {}
        tweToUsrFilePath = toolDirPath + "tweetSocialFeature" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)
        IDmapFilePath = dataFilePath + "IDmap_2013-01-" + tStr
        IDmap = loadID(IDmapFilePath)
        while 1:
            try:
                skeleton = cPickle.load(sklFile)
            except EOFError:
                print "-loading ends(bursty skeleton detection)." + item
                break
            tweetIDstr = skeleton.id
            relSet = skeleton.relSet
            N_t += 1
            sdf_hash = {}
            for idx1 in xrange(len(relSet)):
                for idx2 in xrange(idx1+1, len(relSet)):
                    smallRel = relSet[idx1]
                    bigRel = relSet[idx2]
                    if cmp(smallRel, bigRel) > 0:
                        smallRel = relSet[idx2]
                        bigRel = relSet[idx1]
                    key = "###".join(set([smallRel, bigRel]))
                    if key not in relPairHash: # skeleton(t1) may not appear in day t2
                        continue
                    df_hash = relPairHash[key] # only one day
                    for day in df_hash.keys():
                        df_t_hash = df_hash[day]
                        if day in sdf_hash:
                            sdf_hash[day].update(df_t_hash)
                        else:
                            sdf_hash[day] = deepcopy(df_t_hash)

            dayDF = len(sdf_hash[tStr])*1.0
            # bursty skeleton detection
            if dayDF <= unitpsHash[tweetIDstr]*tweetNum_day:
                continue
            skeleton.setDF(dayDF)
            unitContentHash[skeleton.id] = skeleton
            btyUnitAppHash[skeleton.id] = sdf_hash[tStr]
            # segment users
            unit = skeleton.id
            usr_hash = {}
            if unit in unitUsrHash:
                usr_hash = unitUsrHash[unit]
            usr_hash.update(dict([(IDmap[int(tid[2:])], 1) for tid in sdf_hash[tStr]]))
            unitUsrHash[unit] = usr_hash


            ps = unitpsHash[tweetIDstr]
            e_st = tweetNum_day * ps
            sigma_st = math.sqrt(e_st*(1-ps))
            if dayDF >= e_st + 2*sigma_st: # extremely bursty segments or words
                Pb_st = 1.0
            else:
                Pb_st = sigmoid(10*(dayDF - e_st - sigma_st)/sigma_st)
            unitHash[tweetIDstr] = Pb_st

            if N_t % 10000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        #[GUA] WindowHash mapping: timeWindow -> twitterNum
        sklFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(unitHash))

        #[GUA] burstySegHash mapping: segment -> wb_st(bursty score)
        burstySklHash = {}
        for unit in unitHash:
            u_st_num = len(unitUsrHash[unit])
            u_st = math.log10(u_st_num)
            wb_st = unitHash[unit]*u_st
            burstySklHash[unit] = wb_st
        print "Bursty " + UNIT + " num: " + str(len(burstySklHash))
        
        K = int(math.sqrt(tweetNum_day)) + 1
        print "K (num of event " + UNIT + "): " + str(K)
        #sortedList = sorted(burstySklHash.items(), key = lambda a:a[1], reverse = True)
        sortedList = sorted(burstySklHash.iteritems(), key = operator.itemgetter(1), reverse = True)
        #'''
        for key in sortedList[:K]:
            sid = key[0]
            unitInvolvedHash[sid] = 1
            unitInvolvedHash.update(btyUnitAppHash[sid])
            skeleton = unitContentHash[sid]
            simpleRels = []
            for rel in skeleton.relSet:
                warr = rel.split("||")
                if len(warr) != 3:
                    print tweetIDstr + " " + rel
                warrNew = []
                for w in warr:
                    if w.find("__")>=0:
                        warrNew.append(w[:w.find("__")])
                    else:
                        warrNew.append(w)
                relNew = "||".join(warrNew)
                simpleRels.append(relNew)
            outSklFile.write(sid + "\t" + str(key[1]) + "\t" + " ".join(simpleRels) + "\n")
            #burstySklFile.write(tweetIDstr + "\t" + " ".join(relSet) + "\n")
        #'''
        btySklIDHash = dict([(key[0], 1) for key in sortedList[:K]])
        btyUnitContentHash = dict([(sid, unitContentHash[sid]) for sid in btySklIDHash])
        cPickle.dump(unitInvolvedHash, burstySklFile)
        cPickle.dump(btyUnitContentHash, burstySklFile)
        burstySklFile.close()
        outSklFile.close()

############################
## main Function
global UNIT
print "###program starts at " + str(time.asctime())
dataFilePath = r"../parsedTweet/sklDataV4/"
UNIT = "skl"
toolDirPath = r"../Tools/"
#slangFilePath = r"../Tools/slang.txt"
#slangHash = {} #slangword:regular word

#loadslang(slangFilePath)
getBurstySkeleton(dataFilePath, toolDirPath)

print "###program ends at " + str(time.asctime())
