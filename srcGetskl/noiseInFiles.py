import os
import sys
import re
import time
import cPickle


def loadDic(filename):
    dicFile = file(filename)
    dicHash = cPickle.load(dicFile)
    dicFile.close()
    return dicHash 

def getNoiseInFile(filename, noiseHash):
    segNoiseHash = {}
    print "Processing " + filename
    currFile = file(filename)

    lineIdx = 0
    while 1:
        lineStr = currFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. " + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        lineIdx += 1
        text = lineStr.split("\t")[2]
        segNoiseHash = getNoiseInText(text, noiseHash, segNoiseHash)

        if lineIdx % 100000 == 0:
            print str(lineIdx) + " lines are processed. " + str(time.asctime()) + " segNoiseWords: " + str(len(segNoiseHash))

    return segNoiseHash

def getNoiseInText(text, noiseHash, segNoiseHash):
    text = re.sub("\|", " ", text)
    text = re.sub("_", " ", text)
    arr = text.split(" ")
    for word in arr:
        if word in noiseHash:
            segNoiseHash = insert(segNoiseHash, word)

    return segNoiseHash

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
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        unitID += 1

    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s and f_st values are loaded from " + inFile.name + " with Involved tweet number: " + str(len(unitInvolvedHash))

    return unitHash#, unitDFHash, unitInvolvedHash

def insert(hash, item):
    if item in hash:
        hash[item] += 1
    else:
        hash[item] = 1
    return hash

def outputSegNoise(segNoiseHash, filename):
    segNoiseFile = file(filename, "w")
    print len(segNoiseHash)
    cPickle.dump(segNoiseHash, segNoiseFile)
    segNoiseFile.close()

    for item in sorted(segNoiseHash.items(), key = lambda a:a[1], reverse = True):
        print item

######################################
#main

if len(sys.argv) == 4:
    noiseFilename = sys.argv[1]
    segFilename = sys.argv[2]
    outputFname = sys.argv[3]
else:
    print "Usage: python noiseInSegs.py noiseFname segFname outputFname"
    sys.exit()

noiseHash = loadDic(noiseFilename)
# op1: get Noise from line-written file
#segNoiseHash = getNoiseInFile(segFilename, noiseHash)

# op2: get Noise from cPickle file
global UNIT
UNIT = "frm ele"
btySklHash = loadEvtseg(segFilename)
text = " ".join(btySklHash.keys())
segNoiseHash = {}
segNoiseHash = getNoiseInText(text, noiseHash, segNoiseHash)

outputSegNoise(segNoiseHash, outputFname+noiseFilename[-2:])

print "Program ends at " + str(time.asctime())
