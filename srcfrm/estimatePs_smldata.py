#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

def loadID(filepath):
    idfile = file(filepath)
    IDmap = cPickle.load(idfile)
    idfile.close()
    print "## " + str(time.asctime()) + " Loading done. " + filepath
    return IDmap


print "###Estimating ps program starts at " + str(time.asctime())
if len(sys.argv) < 3:
    print "Usage: estimatePS.py dirpath outputpsfilename"
    sys.exit()

dirPath = sys.argv[1]
outputfile = sys.argv[2]

UNIT = "frm"
unitHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
windowHash = {} # timeSliceIdStr:tweetNum
luHash = {} # lu:frmid

psFile = file(dirPath + outputfile, "w")

fileList = os.listdir(dirPath)
fileList = sorted(fileList)

for item in fileList:
    if os.path.isdir(dirPath+item):
        continue
    if (item.find("ptn") != 0) or (item.find(".kptln") > 0):
        continue
    inFile = file(dirPath + item)
    print "### Processing " + inFile.name
    tStr = item[-2:]
    print "Time window: " + tStr
    #for framenet version --> will be changed when extracting verb.frmid version file again
    kptlnFilePath = dirPath + "ptn" + tStr + ".kptln"
    kptHash = loadID(kptlnFilePath)
    kptlns = sorted(kptHash.keys())

    tweetNum_t = 0
    while 1:
        #[GUA] seggedFile name: * + TimeWindow, format: twitterID, twitterText(segment|segment|...), ...
        lineStr = inFile.readline()
        if not lineStr:
            print "..End of file " + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        #for framenet version
        lineStr = str(kptlns[N_t]) + "\t" + lineStr

        # for format: tweetID[\t]tweetText
        contentArr = lineStr.split("\t")
        if len(contentArr) < 2:
            continue
        tweetIDstr = contentArr[0]
        tweetText = contentArr[1]

        # use frame element
        #tweetText = re.sub("\|", " ", tweetText)

        textArr = tweetText.split(" ")

        '''
        # for frame structure [arg1, verb, arg2]
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

        for item in textArr:
            #unit = item
            # for framenet version(item = lu.frmid, unit = frmid)
            unit = item[item.rfind(".")+1:]
            lu = item[:item.rfind(".")]

            if len(unit) < 1:
                continue

            # for framenet version 'lu.frmid'
            if lu not in luHash:
                luHash[lu] = unit

            # statistic unit ps
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

        tweetNum_t += 1
        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))
    windowHash[tStr] = tweetNum_t
    inFile.close()

    # extra step: decrease memory cost
    for unit in unitHash:
        df_hash = unitHash[unit]
        if tStr not in df_hash:
            df_hash[tStr] = 0.0
        else:
            df_t_hash = df_hash[tStr]
            df_hash[tStr] = len(df_t_hash)*1.0
        unitHash[unit] = df_hash
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + inFile.name + " are loaded. unitNum: " + str(len(unitHash))
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

#for framenet version
unitpshash = {}

## writing to unit ps file
unitNum = 0
for unit in sorted(unitHash.keys()):
    unitNum += 1
    df_hash = unitHash[unit]

    # for debugging
    #fstStr = "\t".join([str(it[1]) for it in sorted(df_hash.items(), key = lambda a:a[0])])

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

    #for framenet version
    unitpshash[unit] = prob
    #psFile.write(str(prob) + "\t" + unit + "\n")

    if unitNum % 100000 == 0:
        print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

#for framenet version
for lu in sorted(luHash.keys()):
    frmid = luHash[lu]
    prob = unitpshash[frmid]
    psFile.write(str(prob) + "\t" + lu + "\n")

psFile.close()
print "### " + UNIT + "s' ps values are written to " + psFile.name + " #unitNum: " + str(len(luHash))

print "###program ends at " + str(time.asctime())
