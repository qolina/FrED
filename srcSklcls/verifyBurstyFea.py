import time
import re
import os
import sys
import cPickle
import math

from estimatePs_smldata import *
from estimatePs_smldata import statisticDF
from estimatePs_smldata import statisticDF_fromFile


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
    print "##End of reading file. [bursty unit file]  unitNum:", len(unitHash), " involvedTweets:", len(unitInvolvedHash), inFile.name
    return unitHash, unitDFHash, unitInvolvedHash

############################
## load event segments from file
def loadBtyFrm(filePath):
    inFile = file(filePath)
    frmList = cPickle.load(inFile)
    inFile.close()
    frmHash = dict([(frmList[i], i) for i in range(len(frmList))])
    print "### " + str(time.asctime()) + " " + str(len(frmHash)) + " event units are loaded from " + inFile.name
    return frmHash


def compare2Bursty(datafilename1, datafilename2):
    [btySklHash1, unitDFHash1, unitInvolvedHash1] = loadEvtseg(datafilename1)
    [btySklHash2, unitDFHash2, unitInvolvedHash2] = loadEvtseg(datafilename2)

    commonHash = [item for item in btySklHash1 if item in btySklHash2]

    print len(commonHash)

    print "####Common:"
    for item in sorted(commonHash):
        print item

    print "######Skl1:", datafilename1
    for item in sorted(btySklHash1.keys()):
        if item not in commonHash:
            print item

    print "######Skl2:", datafilename2
    for item in sorted(btySklHash2.keys()):
        if item not in commonHash:
            print item


###############################################
if __name__ == "__main__":
    print "###program starts at " + str(time.asctime())

###############################################
# compare 2 bursty skl if they are same
#    compare2Bursty(sys.argv[1], sys.argv[2])
#    sys.exit(0)
###############################################

    # for debugging bursty methods
    if len(sys.argv) == 3:
        dataFilePath = sys.argv[1]+"/"
        btySklFileName = sys.argv[2]
    else:
        print "Usage: python verifyBurstyFea.py datafilepath burstyFeafilepath"
        sys.exit(0)

    [btySklHash, unitDFHash, unitInvolvedHash] = loadEvtseg(btySklFileName)
    print "### Example of skl: ", len(btySklHash), btySklHash.keys()[0:20]

###########
#    frmHash = loadBtyFrm(sys.argv[1])
#    print frmHash.keys()[0:20]
#    sys.exit()
###########
    
###############################################

###########
# output freq distri of bursty units
    [unitHash, windowHash] = statisticDF(dataFilePath, btySklHash)

    unitHash_FST = {}
    unitHash_Score = {}
    for unit in sorted(unitHash.keys()):
        df_hash = unitHash[unit]

        prob_hash = dict([(t, df_hash[t]/windowHash[t]) for t in df_hash if df_hash[t]>0])
        l = len(prob_hash)
        probTemp = sum(prob_hash.values())
        prob = probTemp/l

        dayStr = btySklFileName[-2:]
        e_st = windowHash[dayStr] * prob
        sigma_st = math.sqrt(e_st*(1-prob))
        unitHash_Score[unit] = (df_hash.get(dayStr) - e_st)/sigma_st

        # for debugging bursty skl
        fstStr = "\t".join([str(it[1]) for it in sorted(df_hash.items(), key = lambda a:a[0])])
        unitHash_FST[unit] = fstStr
#        print unit, fstStr

    print "unitNum in unitHash_Score, unitHash_FST", len(unitHash_Score), len(unitHash_FST)
    print "### Freq of bursty units."

    for item in sorted(unitHash_Score.items(), key = lambda a:a[1], reverse = True):
        print item[0], "\t", item[1], "\t", unitHash_FST[item[0]]
        
    print "###program ends at " + str(time.asctime())
