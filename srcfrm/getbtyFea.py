#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import math
import cPickle

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
## getEventFeature word/seg/Skl/frm
def getEventUnit(dirPath, toolDirPath):
    fileList = os.listdir(dirPath)
    for item in sorted(fileList):
        if os.path.isdir(dirPath+item):
            continue
        #if item.find("skl_2013-01") != 0:
        #if item.find("relSkl_2013-01") != 0:
        if (item.find("ptn") != 0) or (item.find(".kptln") > 0):
            continue
        tStr = item[-2:]
        if Day != tStr:
            continue
        print "Time window: " + tStr
        print "### Processing " + item
        inFile = file(dirPath + item)
        if len(sys.argv) == 3:
            eventUnitFile = file(dirPath + "event" + UNIT + tStr, "w")
        else:
            eventUnitFile = file(btyFileName, "w")

        N_t = 0
        unitHash = {} #unit:df_t_hash
        #df_t_hash --> tweetIDStr:1
        unitUsrHash = {}
        unitInvolvedHash = {}
        tweToUsrFilePath = toolDirPath + "tweetSocialFeature" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)
        IDmapFilePath = dirPath + "IDmap_2013-01-" + tStr
        IDmap = loadID(IDmapFilePath)

        #for framenet version --> will be changed when extracting verb.frmid version file again
        kptlnFilePath = dirPath + "ptn" + tStr + ".kptln"
        kptHash = loadID(kptlnFilePath)
        kptlns = sorted(kptHash.keys())
        luHash = {}
        ludfHash = {}

        while True:
            lineStr = inFile.readline()
            if not lineStr:
                break
            lineStr = lineStr[:-1]
            lineStr = str(kptlns[N_t]) + "\t" + lineStr
            contentArr = lineStr.split("\t")
            if len(contentArr) < 2:
                continue
            tweetIDstr = contentArr[0]
            #tweetIDstr = tweetIDstr[2:]
            tweetText = contentArr[1]
            usrIDstr = tweIdToUsrIdHash[IDmap[int(tweetIDstr)]]
            N_t += 1

            # use frame element
            #tweetText = re.sub("\|", " ", tweetText)

            textArr = tweetText.split(" ")
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

            for item in textArr:
                #unit = item
                # for framenet version(item = lu.frmid, unit = frmid)
                unit = item[item.rfind(".")+1:]
                lu = item[:item.rfind(".")]
                unit = lu

                if len(unit) < 1:
                    continue

                # for framenet version 'lu.frmid'
                if lu not in luHash:
                    luHash[lu] = unit

                # lu df
                lu_df_t_hash = {}
                if lu in ludfHash:
                    lu_df_t_hash = ludfHash[lu]
                lu_df_t_hash[tweetIDstr] = 1
                ludfHash[lu] = lu_df_t_hash

                # unit df
                df_t_hash = {}
                if unit in unitHash:
                    df_t_hash = unitHash[unit]
                df_t_hash[tweetIDstr] = 1
                unitHash[unit] = df_t_hash

                # unit users
                usr_hash = {}
                if unit in unitUsrHash:
                    usr_hash = unitUsrHash[unit]
                usr_hash[usrIDstr] = 1
                unitUsrHash[unit] = usr_hash

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        #[GUA] WindowHash mapping: timeWindow -> twitterNum
        windowHash[tStr] = N_t
        inFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + inFile.name + " are loaded." + str(len(unitHash))

        #[GUA] burstyUnitHash mapping: unit -> wb_st(bursty score)
        burstyUnitHash = {}
        #for unit in unitHash:
        for lu in luHash:
            unit = luHash[lu]

            # twitterNum / unit, timeWindow
            f_st = len(unitHash[unit])*1.0

            # usrNum / unit, timeWindow
            u_st_num = len(unitUsrHash[unit])


            #[GUA] unitpsHash mapping: unit -> ps, N_t: twitterNum / timeWindow
            #ps = unitpsHash[unit]
            ps = unitpsHash[lu] # for framnet version
            e_st = N_t * ps
            if f_st <= e_st: # non-bursty unit or word
#                print "### non-bursty " + UNIT + ": " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st)
                continue
            # bursty unit or word
            sigma_st = math.sqrt(e_st*(1-ps))

            #[GUA] Whether or not f_st in (e_st, e_st + sigma_st) ?

            if f_st >= e_st + 2*sigma_st: # extremely bursty units or words
                Pb_st = 1.0
            else:
                Pb_st = sigmoid(10*(f_st - e_st - sigma_st)/sigma_st)
            u_st = math.log10(u_st_num)
            wb_st = Pb_st*u_st
#            print "# bursty seg/word: " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st),
#            print " ps: " + str(ps),
#            print " sigma: " + str(sigma_st),
#            print " pb: " + str(Pb_st),
#            print " u_st: " + str(u_st_num)
#            print " wbScore: " + str(wb_st)
            #burstyUnitHash[unit] = wb_st
            burstyUnitHash[lu] = wb_st # for framenet ver
        print "Bursty " + UNIT + " num: " + str(len(burstyUnitHash))
        
        K = int(math.sqrt(N_t)) + 1
        print "K (num of event " + UNIT + "): " + str(K)
        sortedList = sorted(burstyUnitHash.items(), key = lambda a:a[1], reverse = True)
        sortedList = sortedList[0:K]
        unitStrList = []
        for key in sortedList:
            eventUnit = key[0]
            frmid = luHash[eventUnit]
            #apphash = dict([(IDmap[int(tid[2:])], 1) for tid in unitHash[eventUnit]])
            #f_st = len(unitHash[eventUnit])
            # for framenet version
            apphash = dict([(IDmap[int(tid)], 1) for tid in unitHash[frmid]])
            f_st = len(unitHash[frmid])
            unitInvolvedHash.update(apphash)

            #[GUA] eventUnitFile name: eventUnit + TimeWindow, format: f_st(twitterNum / unit, timeWindow), wb_st(bursty score), unit
            unitStrList.append(str(f_st) + "\t" + str(key[1]) + "\t" + eventUnit + "\n")
            print eventUnit + "\t" + str(len(ludfHash[eventUnit])) + "\t" + frmid + "\t" + str(f_st)
        cPickle.dump(unitStrList, eventUnitFile)
        cPickle.dump(unitInvolvedHash, eventUnitFile)
        eventUnitFile.close()

############################
## main Function
global Day, btyFileName
if len(sys.argv) > 3:
    Day = sys.argv[1]
    dirPath = sys.argv[2]
    btyFileName = sys.argv[3]
elif len(sys.argv) == 3:
    Day = sys.argv[1]
    dirPath = sys.argv[2]
else:
    print "Usage getbtyskl.py day dirPath [btyFileName]"
    sys.exit()

global UNIT
print "###program starts at " + str(time.asctime())

if len(dirPath) < 1:
    dirPath = r"../parsedTweet/"
toolDirPath = r"../Tools/"

UNIT = "frm"
psFilePath = dirPath + UNIT + ".ps"
#slangFilePath = r"../Tools/slang.txt"
windowHash = {} # timeSliceIdStr:tweetNum
unitpsHash = {} # unit:ps
#slangHash = {} #slangword:regular word

#loadslang(slangFilePath)
loadps(psFilePath)
getEventUnit(dirPath, toolDirPath)

print "###program ends at " + str(time.asctime())
