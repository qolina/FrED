#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

sys.path.append("/home/yxqin/FrED/srcStat")
from getSocialInfo import *

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
    global unitpsHash
    psFile = file(psFilePath)
    while True:
        lineStr = psFile.readline()
        lineStr = re.sub(r'\n', '', lineStr)
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        #print contentArr
        prob = float(contentArr[0])
        unit = contentArr[1]
        unitpsHash[unit] = prob
    psFile.close()
    print "### " + str(time.asctime()) + " " + str(len(unitpsHash)) + " " + UNIT + "s' ps values are loaded from " + psFile.name

############################
## load tweetID-usrID
def loadUsrId(filepath, tweIdFileName):

    usrFile = file(filepath,"r")
    attHash = cPickle.load(usrFile)
    usrFile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath

    if tweIdFileName:
        tweIdList = getTweetID(tweIdFileName)
#        tweIdToUsrIdHash_emp = dict([(tid, "empty") for tid in tweIdList if tid not in attHash])  # only 1 in day 10, 13, 15
        tweIdToUsrIdHash = dict([(tid, attHash[tid]["Usr"]) for tid in tweIdList if tid in attHash]) 
    else:
        tweIdToUsrIdHash = dict([(tid, attHash[tid]["Usr"]) for tid in attHash]) 
    print "## " + str(time.asctime()) + " Loading done. Twe2Usr" , len(tweIdToUsrIdHash)
    return tweIdToUsrIdHash

############################
## load tweetID-usrID
def loadID(filepath):
    if not os.path.exists(filepath):
        return None

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
## getEventSkl
def getEventSkl(dataFilePath, socialFeaFilePath, idmapFilePath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        #if item.find("skl_2013-01") != 0:
        if item.find("relSkl_") != 0:
        #if item.find("segged_tweetContentFile") != 0:
            continue
        tStr = item[-2:]
        if Day != tStr:
            continue
        print "Time window: " + tStr
        print "### Processing " + item
        seggedFile = file(dataFilePath + item)
        N_t = 0
        unitHash = {} #unit:df_t_hash
        #df_t_hash --> tweetIDStr:1
        unitUsrHash = {}
        unitInvolvedHash = {}
        tweToUsrFilePath = socialFeaFilePath + "tweetSocialFeature" + tStr
        #tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath, dataFilePath+item)
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath, None)
        IDmap = loadID(idmapFilePath + "IDmap_2015-05-" + tStr)
        while True:
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            if len(contentArr) < 2:
                continue
            # format of lineStr: tweetID(originalTweetID)[\t]score[\t]tweetText   Or tweetId(day+lineId)[\t]tweetText
            tweetIDstr = contentArr[0]
            tweetText = contentArr[-1]
            
            if len(tweetIDstr)==18:
                usrIDstr = tweIdToUsrIdHash.get(tweetIDstr)
            else:
                usrIDstr = tweIdToUsrIdHash.get(IDmap[int(tweetIDstr[2:])])

            if usrIDstr is None:
                continue
            N_t += 1

            # use segment
            #tweetText = re.sub(" ", "_", tweetText)

            # use frame element
            tweetText = re.sub("\|", " ", tweetText)

            textArr = tweetText.strip().split(" ")
            '''
            # for frame structure
            # make record of location
            newTextArr = []
            for seg in textArr:
                eleArr = seg.split("|")
                #newEle = [eleArr[i]+"_"+str(i) for i in range(3) if len(eleArr[i])>1] #v6
                if len(eleArr[1]) < 1:
                    #print tweetText
                    newEle = [eleArr[0], eleArr[1], eleArr[2]] #v7
                else:
                    newEle = [eleArr[0], eleArr[1]+"_1", eleArr[2]] #v7
                newTextArr.extend(newEle)
            textArr = newTextArr
            '''

            for segment in textArr:
                unit = segment
                #unit = segment.strip("|")
                if len(unit) < 1:
                    continue
                # segment df
                df_t_hash = {}
                if unit in unitHash:
                    df_t_hash = unitHash[unit]
                df_t_hash[tweetIDstr] = 1
                unitHash[unit] = df_t_hash

                # segment users
                usr_hash = {}
                if unit in unitUsrHash:
                    usr_hash = unitUsrHash[unit]
#                    if unit == "clemson":
#                        print "## userDF of ", unit, len(usr_hash), usrIDstr
                usr_hash[usrIDstr] = 1
                unitUsrHash[unit] = usr_hash

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        #[GUA] WindowHash mapping: timeWindow -> twitterNum
        windowHash[tStr] = N_t
        seggedFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(unitHash))

        #[GUA] burstySegHash mapping: segment -> wb_st(bursty score)
        burstySegHash = {}
        burstySegHash_udf = {}
        burstySegHash_zscore = {}

        pbSegHash = {}
        for unit in unitHash:

            # twitterNum / unit, timeWindow
            f_st = len(unitHash[unit])*1.0

            # usrNum / unit, timeWindow
            u_st_num = len(unitUsrHash[unit])


            #[GUA] segmentpsHash mapping: segment -> ps, N_t: twitterNum / timeWindow
            ps = unitpsHash[unit]
            e_st = N_t * ps
            if f_st <= e_st: # non-bursty segment or word
#                print "### non-bursty " + UNIT + ": " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st)
#                if unit == "clemson":
#                    print "##### clemson:", f_st, e_st
                continue
            # bursty segment or word
            sigma_st = math.sqrt(e_st*(1-ps))

            #[GUA] Whether or not f_st in (e_st, e_st + sigma_st) ?

            if f_st >= e_st + 2*sigma_st: # extremely bursty segments or words
                Pb_st = 1.0
            else:
                Pb_st = sigmoid(10*(f_st - e_st - sigma_st)/sigma_st)
            u_st = math.log10(u_st_num)
            wb_st = Pb_st*u_st
            zscore = (f_st - e_st) / sigma_st
#            print "# bursty seg/word: " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st),
#            print " ps: " + str(ps),
#            print " sigma: " + str(sigma_st),
#            print " pb: " + str(Pb_st),
#            print " u_st: " + str(u_st_num)
#            print " wbScore: " + str(wb_st)



#            burstySegHash[unit] = wb_st
#            pbSegHash[unit] = "\t".join([str(i) for i in [wb_st, Pb_st, f_st, e_st, 2*sigma_st, u_st_num, u_st]])

            burstySegHash_udf[unit] = u_st_num
            burstySegHash_zscore[unit] = zscore
            pbSegHash[unit] = "\t".join([str(i) for i in [zscore, u_st_num]])

#            burstySegHash[unit] = (f_st - e_st) / sigma_st
#            pbSegHash[unit] = (f_st - e_st) / sigma_st

        print "Bursty " + UNIT + " num: " + str(len(burstySegHash)), len(burstySegHash_udf), len(burstySegHash_zscore)
        
        K = int(math.sqrt(N_t)) + 1
        print "K (num of event " + UNIT + "): " + str(K)

        #option1 use one score to rank
        sortedList = sorted(burstySegHash_zscore.items(), key = lambda a:a[1], reverse = True)
        sortedList = sortedList[0:K]


        #option2 use two score to rank
#        sortedList_udf = sorted(burstySegHash_udf.items(), key = lambda a:a[1], reverse = True)
#        sortedList_zscore = sorted(burstySegHash_zscore.items(), key = lambda a:a[1], reverse = True)
#
#        sortedList_udf_unit = [item[0] for item in sortedList_udf][:2*K]
#        sortedList_zscore_unit = [item[0] for item in sortedList_zscore][:2*K]
#
##        for i in range(2000):
##            print sortedList_udf_unit[i], "\t", sortedList_zscore_unit[i]
#
#        commonList_unit = [item for item in sortedList_zscore_unit if item in sortedList_udf_unit]
#        print "Num of commonBursty features of 2K-size lists:", len(commonList_unit)
#        if len(commonList_unit) > K:
#            commonList_unit = commonList_unit[:K]
#
#        sortedList = [(unit, str(burstySegHash_zscore[unit]) + "-" + str(burstySegHash_udf[unit])) for unit in commonList_unit]


        # write 2 file
        segStrList = []
        for key in sortedList:
            eventSeg = key[0]
            if len(tweetIDstr) == 18:
                apphash = dict([(tid, 1) for tid in unitHash[eventSeg]])
            else:
                apphash = dict([(IDmap[int(tid[2:])], 1) for tid in unitHash[eventSeg]])

            unitInvolvedHash.update(apphash)
            f_st = len(unitHash[eventSeg])

            #[GUA] eventSegFile name: eventSeg + TimeWindow, format: f_st(twitterNum / segment, timeWindow), wb_st(bursty score), segment
            #eventSegFile.write(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")
            segStrList.append(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")

        if len(sys.argv) == 2:
            eventSegFile = file(dataFilePath + "event" + UNIT + tStr, "w")
        else:
            eventSegFile = file(btyFileName, "w")

        cPickle.dump(segStrList, eventSegFile)
        cPickle.dump(unitInvolvedHash, eventSegFile)
        eventSegFile.close()

        #sorted_pblist = sorted(pbSegHash.items(), key = lambda a:a[1], reverse = True)[0:K]
        for item in sortedList:
            print item[0], "\t", pbSegHash[item[0]]

global UNIT
UNIT = "skl"
#UNIT = "segment"

############################
## main Function
if __name__ == "__main__":
    global Day, btyFileName
    if len(sys.argv) > 2:
        Day = sys.argv[1]
        btyFileName = sys.argv[2]
    elif len(sys.argv) == 2:
        Day = sys.argv[1]
    else:
        print "Usage getbtyskl.py day [btyFileName]"
        sys.exit()

    print "###program starts at " + str(time.asctime())

    #dataFilePath = r"/home/yxqin/corpus/data_twitter201301/201301_segment/"
    #dataFilePath = r"/home/yxqin/corpus/data_twitter201301/201301_skl/"
    dataFilePath = r"/home/yxqin/corpus/data_stock201504/skl/"

    psFilePath = dataFilePath + UNIT + "_ps"
    #slangFilePath = r"../Tools/slang.txt"

    # for frame
    socialFeaFilePath = dataFilePath + r"../nonEng/"
    # for segment
    #socialFeaFilePath = dataFilePath + r"../201301_segment/"
    # available for all
    #socialFeaFilePath = dataFilePath + r"../rawData/"

    #idmapFilePath = dataFilePath + r"../201301_clean/"
    idmapFilePath = dataFilePath + r"../clean/"

    windowHash = {} # timeSliceIdStr:tweetNum
    unitpsHash = {} # unit:ps
    #slangHash = {} #slangword:regular word

    #loadslang(slangFilePath)
    loadps(psFilePath)
    getEventSkl(dataFilePath, socialFeaFilePath, idmapFilePath)

    print "###program ends at " + str(time.asctime())
