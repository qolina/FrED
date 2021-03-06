#! /usr/bin/env python
#coding=utf-8

from pubHeader import *
from estimatePs_frm import *

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

def exactfrmUsrDF(dataFilePath, frmList, day):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("digitSklText-") != 0:
            continue
        tStr = item[-2:]
        if day != tStr:
            continue

        print "Time window: " + tStr
        print "### Processing " + item
        sklFile = file(dataFilePath + item)

        idx = 0
        unitHash = {}
        unitUsrHash = {} #unit:df_t_hash
        #df_t_hash --> tweetIDStr:1
        IDmapFilePath = "../data/taggedTweet/IDmap/" + "IDmap_2013-01-" + tStr
        IDmap = loadID(IDmapFilePath)
        tweToUsrFilePath = toolDirPath + "tweetSocialFeature" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)

        while 1:
            lineStr = sklFile.readline()
            if not lineStr:
                break
            contentArr = lineStr[:-1].split("\t")
            if len(contentArr) < 2:
                continue
            tweetIDstr = contentArr[0]
            tweetText = contentArr[1]
            usrIDstr = tweIdToUsrIdHash[IDmap[int(tweetIDstr[2:])]]
            #usrIDstr = tweetIDstr
            idx += 1

            # use frame element
            #tweetText = re.sub("\|", " ", tweetText)

            textArr = tweetText.split(" ")

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
                usr_hash[usrIDstr] = 1
                unitUsrHash[unit] = usr_hash

            if idx % 1000000 == 0:
                print "### " + str(time.asctime()) + " " + str(idx) + " tweets are processed!"
                #break

        sklFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + sklFile.name + " are loaded. #usrDF: ", len(unitUsrHash), " #frmdf: ", len(unitHash)
        unitUsrHash = dict([(item, unitUsrHash[item]) for item in frmList if item in unitUsrHash])
        unitHash = dict([(item, unitHash[item]) for item in frmList if item in unitHash])
        print "After filtering: #usrDF: ", len(unitUsrHash), " #frmdf: ", len(unitHash), " frm's are obtained."
        return unitHash, unitUsrHash

############################
## getEventSkl
def getEventSkl(dataFilePath, toolDirPath, tStr, flag):
    frmList = loadFrmlist(dataFilePath)
    [unitHash, unitUsrHash] = exactfrmUsrDF(dataFilePath, frmList, tStr)
    [frmCluster, clusters] = loadFrmCls(dataFilePath, flag)
    '''
    windowHash = {}
    dfhash = {}
    tempArr = [dfhash.update(unitHash[frm]) for frm in unitHash]
    windowHash[tStr] = len(dfhash)
    '''
    exactFile = file(dataFilePath+"frmExactDF")
    windowHash = cPickle.load(exactFile)
    print "windowhash is loaded from ", exactFile.name, " at ", time.asctime()
    exactFile.close()
    
    clsDFHash = {}
    clsUsrdfHash = {}
    for clusID in clusters:
        frms = clusters[clusID]
        usrdfHash = {}
        dfHash = {}
        temparr1 = [dfHash.update(unitHash[frm]) for frm in frms if frm in unitHash]
        temparr2 = [usrdfHash.update(unitUsrHash[frm]) for frm in frms if frm in unitUsrHash]
        clsDFHash[clusID] = dfHash
        clsUsrdfHash[clusID] = usrdfHash

    if "-btyfile" in sys.argv:
        eventSegFile = file(btyFileName, "w")
    else:
        eventSegFile = file(dataFilePath + "event" + UNIT + tStr, "w")

    unitInvolvedHash = {}
    #[GUA] burstySegHash mapping: segment -> wb_st(bursty score)
    burstySegHash = {}
    for unit in unitHash:

        # if contains similar frms
        if unit in frmCluster:
            clsid = frmCluster[unit]
            f_st = len(clsDFHash[clsid])*1.0
            u_st_num = len(clsUsrdfHash[clsid])
        else:
            #default
            f_st = len(unitHash[unit])*1.0
            u_st_num = len(unitUsrHash[unit])

        ps = unitpsHash[unit]
        e_st = windowHash[tStr] * ps
        if f_st <= e_st: # non-bursty segment or word
#                print "### non-bursty " + UNIT + ": " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st)
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
#            print "# bursty seg/word: " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st),
#            print " ps: " + str(ps),
#            print " sigma: " + str(sigma_st),
#            print " pb: " + str(Pb_st),
#            print " u_st: " + str(u_st_num)
#            print " wbScore: " + str(wb_st)
        burstySegHash[unit] = wb_st
    print "Bursty " + UNIT + " num: " + str(len(burstySegHash))
    
    IDmapFilePath = "../data/taggedTweet/IDmap/" + "IDmap_2013-01-" + tStr
    IDmap = loadID(IDmapFilePath)
    K = int(math.sqrt(windowHash[tStr])) + 1
    print "K (num of event " + UNIT + "): " + str(K)
    sortedList = sorted(burstySegHash.items(), key = lambda a:a[1], reverse = True)
    sortedList = sortedList[0:K]
    segStrList = []
    for key in sortedList:
        eventSeg = key[0]
        if eventSeg in frmCluster:
            clsid = frmCluster[eventSeg]
            dfhash = clsDFHash[clsid]
        else:
            dfhash = unitHash[unit]
        f_st = len(dfhash)*1.0
        apphash = dict([(IDmap[int(tid[2:])], 1) for tid in dfhash])
        #apphash = dict([(tid[2:], 1) for tid in dfhash])
        unitInvolvedHash.update(apphash)

        #[GUA] eventSegFile name: eventSeg + TimeWindow, format: f_st(twitterNum / segment, timeWindow), wb_st(bursty score), segment
        #eventSegFile.write(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")
        segStrList.append(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")
    cPickle.dump(segStrList, eventSegFile)
    cPickle.dump(unitInvolvedHash, eventSegFile)
    eventSegFile.close()
    print "Bursty frms has been stored into ", eventSegFile.name
    # whether bursty frms belongs to one cluster
    clsIDArr = [frmCluster.get(item[0]) for item in sortedList]
    print clsIDArr

############################
## main Function
if __name__=="__main__":
    global btyFileName
    global flag
    argsArr = sys.argv
    if "-d" in argsArr:
        day = argsArr[argsArr.index("-d")+1]
    else:
        print "Usage getbtyskl.py -d day [-flag flag] [-btyfile btyFileName]"
        sys.exit()
    if "-btyfile" in sys.argv:
        btyFileName = argsArr[argsArr.index("-btyfile")+1]
    if "-flag" in sys.argv:
        flag = argsArr[argsArr.index("-flag")+1]

    global useSegmentFlag, UNIT
    print "###program starts at " + str(time.asctime())
    #dataFilePath = r"../parsedTweet/"
    dataFilePath = r"../exp/w2v/"

    UNIT = "skl"
    psFilePath = dataFilePath + UNIT + "_ps"+flag
    #slangFilePath = r"../Tools/slang.txt"
    toolDirPath = r"../Tools/"
    windowHash = {} # timeSliceIdStr:tweetNum
    unitpsHash = {} # unit:ps
    #slangHash = {} #slangword:regular word

    #loadslang(slangFilePath)
    loadps(psFilePath)
    getEventSkl(dataFilePath, toolDirPath, day, flag)

    print "###program ends at " + str(time.asctime())
