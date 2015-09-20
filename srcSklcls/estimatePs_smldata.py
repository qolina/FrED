#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle

def statisticDF(dataFilePath, predefinedUnitHash):

    unitHash = {} #unit:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    unitAppHash = {} #unit:apphash
    windowHash = {} # timeSliceIdStr:tweetNum

    fileList = os.listdir(dataFilePath)
    fileList = sorted(fileList)
    for item in fileList:
        if item.find("relSkl_2013") != 0:
#        if item.find("segged_tweetContentFile") != 0:
            continue
        inFile = file(dataFilePath + item)
        print "### Processing " + inFile.name
        tStr = item[-2:]
        if int(tStr) <= 5: # test
            continue
        tweetNum_t = 0
        while 1:
            #[GUA] seggedFile name: * + TimeWindow, format: twitterID, [score,] twitterText(segment|segment|...), ...
            lineStr = inFile.readline()
            if not lineStr:
                break

            contentArr = lineStr[:-1].split("\t")
            # lineStr frame format: tweetIDstr[\t]tweetText
            # Or segment format: tweetIDstr[\t]score[\t]tweetText
            if len(contentArr) < 2: 
                continue
            
            tweetIDstr = contentArr[0]
            tweetText = contentArr[-1]
            tweetNum_t += 1

            # use segment
            # tweetText: seg1|seg2|...
            # segment: word1 word2
#            if UNIT == "segment":
#                tweetText = re.sub(" ", "_", tweetText)

            # use frame element
            # tweetText: frm1[1space]frm2 frm3...
            # frame: arg1|vp|arg2   frmEle: word1_word2_...
            tweetText = re.sub("\|", " ", tweetText)


            textArr = tweetText.strip().split(" ")

#            # for frame structure
#            # v6: make record of location
#            newTextArr = []
#            for seg in textArr:
#                eleArr = seg.split("|")
#                #newEle = [eleArr[i]+"_"+str(i) for i in range(3) if len(eleArr[i])>1]
#
#                #v7: only distinguish verb and arg 
#                newEle = [eleArr[0], eleArr[1]+"_1", eleArr[2]]
#
#                newTextArr.extend(newEle)
#            #print newTextArr
#            textArr = newTextArr

            for unit in textArr:
                if len(unit) < 1:
                    continue

                # for testing bursty methods
                # predefinedUnitHash usually is bursty skl hash
                if predefinedUnitHash is not None:
                    #if re.sub(r"\|", "_", unit).strip("_") not in sklHash: # use frame
                    if unit not in predefinedUnitHash: # use frame element or segment
                        continue

                # statistic unit df
                '''
                apphash = {}
                if unit in unitAppHash:
                    apphash = unitAppHash[unit]
                apphash[tweetIDstr] = 1
                unitAppHash[unit] = apphash 
                '''

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

        print "### (current day)" + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. unitNum: " + str(len(unitHash))

    print "### In total(whole corpora) " + str(len(unitHash)) + " " + UNIT + "s are loaded!"

    return unitHash, windowHash


# writing to dffile
def write2dfFile(unitAppHash, windowHash, dfFilePath):

    dfFile = file(dfFilePath, "w")

    # write each day's tweetNumber into first line of df file
    # Format:01 num1#02 num2#...#15 num15
    sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
    tweetNumStr = ""
    for item in sortedTweetNumList:
        tStr = item[0]
        tweetNum = item[1]
        tweetNumStr += tStr + " " + str(tweetNum) + "#"

    dfFile.write(tweetNumStr[:-1] + "\n")
    itemNum = 0
    for unit in sorted(unitAppHash.keys()):
        itemNum += 1
        apphash = unitAppHash[unit]
        df = len(apphash)
        dfFile.write(str(df) + "\t" + unit + "\n")
    dfFile.close()
    print "### " + UNIT + "s' df values are written to " + dfFile.name


# writing to unit ps file
def write2psFile(unitHash, windowHash, psFilePath):

    psFile = file(psFilePath, "w")
    unitNum = 0
    for unit in sorted(unitHash.keys()):
        unitNum += 1
        df_hash = unitHash[unit]

        df_hash = dict([(t, df_hash[t]/windowHash[t]) for t in df_hash if df_hash[t]>0])
        l = len(df_hash)
        probTemp = sum(df_hash.values())
        prob = probTemp/l

        # for debugging
#        #if df_hash["01"] > 2*prob:
#        if l > 5:
#            print unit + "\t",
#            print str(windowHash["01"]*prob) + "\t",
#            print fstStr
#        else:
#            psFile.write(str(prob) + "\t" + unit + "\t" + fstStr + "\n")

        psFile.write(str(prob) + "\t" + unit + "\n")

        if unitNum % 100000 == 0:
            print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

    psFile.close()
    print "### " + UNIT + "s' ps values are written to " + psFile.name

global UNIT
UNIT = "skl"
#UNIT = "segment"


if __name__ == "__main__":
    print "###program starts at " + str(time.asctime())
    if len(sys.argv) == 2:
        dataFilePath = sys.argv[1]+"/"
    else:
        print "Usage python estimatePs_smldata.py [datafilepath] (default: ../parsedTweet/)"
#        dataFilePath = r"../parsedTweet/"
#        dataFilePath = r"/home/yxqin/corpus/data_twitter201301/201301_skl/"
        sys.exit(0)

    [unitHash, windowHash]  = statisticDF(dataFilePath, None)

#    dfFilePath = dataFilePath + UNIT + "_df"
#    write2dfFile(unitAppHash, windowHash, dfFilePath)

    psFilePath = dataFilePath + UNIT + "_ps"
    write2psFile(unitHash, windowHash, psFilePath)

    print "###program ends at " + str(time.asctime())


