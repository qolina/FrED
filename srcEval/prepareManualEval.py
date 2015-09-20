#! /usr/bin/env python
#coding=utf-8
# evaluation of twevent
import os
import sys
import time
import math
import re
import cPickle

def loadHoroscopeWords(path):
    horoFile = file(path)
    lineArr = horoFile.readlines()
    horolist = []
    for line in lineArr:
        horolist.append(line[:-1])
    return horolist


def getContent(itemfile, tag1, tag2):
    eventList = []
    idxList = []
    lbl_eventFile = file(itemfile)
    #print "*********************Reading file: " + itemfile

    lineArr = lbl_eventFile.readlines()
    lineIdx = 0
    while lineIdx < len(lineArr):
        lineStr = lineArr[lineIdx]
        if lineStr.startswith("***"):
            line1 = lineArr[lineIdx + 1]
            arr = line1.split("#")

            segmentList = lineArr[lineIdx+4][:-1].split(tag1)
            wordList = []
            for segment in segmentList:
                segment = re.sub("\|", " ", segment)
                segment = re.sub("_", " ", segment)
                wArr = segment.split(" ")
                wordList.extend(wArr)
            #'''# filter out horoscope topics
            horoflag = False
            for horoWord in horoWordList:
                for word in wordList:
                    if word.find(horoWord) >= 0:
                        '''
                        print lineArr[lineIdx + 1][:-1]
                        print horoWord + "\t#" + str(wordList)
                        print lineArr[lineIdx + 4][:-1]
                        '''
                        horoflag = True
                        break
            if horoflag:
                lineIdx += 6
                continue
            #'''
            ratioIdxS = line1.find("ratio:") + 7
            ratioIdxE = line1.find(" ", ratioIdxS)
            ratioInt = int(math.ceil(float(line1[ratioIdxS:ratioIdxE])))
            #print "ratio: " + str(ratioInt)
            
            #print segmentList
            segmentList = [re.sub(tag2, " ", seg) for seg in segmentList]
            segmentList = [re.sub("\|", " ", seg).strip() for seg in segmentList]
            newSegs = []
            for it in segmentList:
                if it not in newSegs:
                    newSegs.append(it)
            #print newSegs
            line4 = "##".join(newSegs)
            #print line4
            eventList.append(line4) 

            if arr[0].startswith("T") | arr[0].startswith("t"):
                idxList.append(1)
            else:
                idxList.append(0)

        lineIdx += 6

    lbl_eventFile.close()
    return eventList, idxList


def getMix(day, tweFile, frmFile):
    mixlist = []
    [twelist, tlbls] = getContent(tweFile, '||', ' ')
    [frmlist, flbls] = getContent(frmFile, ' ', '_')

    idxhash = {}
    taghash = {}

    short = min(len(twelist), len(frmlist))
    for i in range(short):
        mixlist.append(twelist[i])
        sys = "#".join(['t', day, str(i)])
        lbl = tlbls[i]
        idxhash[len(idxhash)] = sys
        taghash[sys] = lbl
        #print "0" + "\t" + str(tlbls[i])

        mixlist.append(frmlist[i])
        sys = "#".join(['f', day, str(i)])
        lbl = flbls[i]
        idxhash[len(idxhash)] = sys
        taghash[sys] = lbl
        #print "0" + "\t" + str(flbls[i])

    if len(twelist) > short:
        mixlist.extend(twelist[short:])
        for i in range(short, len(twelist)):
            sys = "#".join(['t', day, str(i)])
            lbl = tlbls[i]
            idxhash[len(idxhash)] = sys
            taghash[sys] = lbl
            #print "0" + "\t" + str(tlbls[i])

    if len(frmlist) > short:
        mixlist.extend(frmlist[short:])
        for i in range(short, len(frmlist)):
            sys = "#".join(['f', day, str(i)])
            lbl = flbls[i]
            idxhash[len(idxhash)] = sys
            taghash[sys] = lbl
            #print "0" + "\t" + str(flbls[i])
    return mixlist, idxhash, taghash


# main function
print "### " + str(time.asctime()) + " # Preparing events for manual labelling. "
global horoWordList 
toolPath = r"../Tools/horoscopeWords"
if len(sys.argv) != 3:
    print "Usage dirPath outputFile"
    sys.exit()
dirPath = sys.argv[1]
outputFile = sys.argv[2]

horoWordList = loadHoroscopeWords(toolPath)
eventFile = file(dirPath+outputFile, "w")
qTagFile = file(dirPath+r"tagsByQin", "w")

idTosys = {}
tagsAll = {}
dayArr = [str(i).zfill(2) for i in range(1, 16)]
id = 0
for day in dayArr:
    dayStr = "Jan. "+day
    twefilename = dirPath + "l_EventFile" + day + "_k5t2_ltwe"
    frmfilename = dirPath + "frmEventFile"+day
    [mixlist, idxhash, taghash] = getMix(day, twefilename, frmfilename)
    for i in range(len(mixlist)):
        idTosys[id] = idxhash[i]
        #eventFile.write(idxhash[i] + "\t")
        eventFile.write(str(id) + "\t" + idTosys[id] + "\t")
        eventFile.write(str(taghash[idxhash[i]]) + "\t")
        eventFile.write(dayStr + "\t" + mixlist[i] + "\n")
        id += 1
    tagsAll.update(taghash)

cPickle.dump(idTosys, qTagFile)
cPickle.dump(tagsAll, qTagFile)

print "Prepared events are stored into " + eventFile.name
print "Corresponding tags for events are stored into " + qTagFile.name
eventFile.close()
qTagFile.close()
