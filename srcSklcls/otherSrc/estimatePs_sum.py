#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

print "###program starts at " + str(time.asctime())
dataFilePath = r"../parsedTweet/"

if len(sys.argv) == 1:
    print "Usage: python estimatePs_sum.py day"
    sys.exit()
else:
    Day = sys.argv[1]

UNIT = "skl"
unitHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
psFile = file(dataFilePath + UNIT + "_ps" + Day, "w")
tArr = [str(i).zfill(2) for i in range(1, 16) if i != int(Day)]
tArr.insert(0, Day)
for tStr in tArr:
    item = UNIT+"_ps_"+tStr
    psdayFile = file(dataFilePath + item)
    print "Time window: " + tStr
    print "### Loading " + psdayFile.name
    unitDayHash = cPickle.load(psdayFile)
    print "## " + str(time.asctime()) + " " + str(len(unitDayHash))+ " units' ps are loaded"
    psdayFile.close()
    unitNum = 0
    for unit in unitDayHash:
        if unit not in unitHash:
            df_hash = {}
        else:
            df_hash = unitHash[unit] 
        df_hash[tStr] = unitDayHash[unit]
        #'''# record ps of words appeared in Day
        if Day not in df_hash: 
            continue
        #'''
        unitHash[unit] = df_hash
        unitNum += 1

        if unitNum % 1000000 == 0:
            print "### " + str(time.asctime()) + " " + str(unitNum) + " units are processed!"
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. unitNum: " + str(len(unitHash))
print "### In total " + str(len(unitHash)) + " " + UNIT + "s are loaded!"

## writing to unit ps file
unitNum = 0
for unit in sorted(unitHash.keys()):
    unitNum += 1
    df_hash = unitHash[unit]
    l = len(df_hash)
    probTemp = sum(df_hash.values())
    prob = probTemp/l
    psFile.write(str(l) + "\t" + str(prob) + "\t" + unit + "\n")
    if unitNum % 1000000 == 0:
        print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

psFile.close()
print "### " + UNIT + "s' ps values are written to " + psFile.name

print "###program ends at " + str(time.asctime())
