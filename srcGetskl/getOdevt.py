import os
import sys
import re
import time
import cPickle

########################################################
# replace mention with @usr
def normMen(relArr):
    relArrUSR = []
    for wd in relArr:
        if wd.find("#") >= 0:
            continue
        if len(wd) <= 0:
            continue
        if wd[0] == "@":
            #wd = "@usr" # op1
            continue # op2
        wd = re.sub(r"\|", "", wd) # | is used as separator later for frame
        relArrUSR.append(wd)
    return relArrUSR

def normRep(item):
    for match in re.findall(r"(((\w)+)\2{3,})", item):
        if len(match[1]) == 1:
            item = re.sub(match[0], match[1]*3, item)
        if (len(match) > 2) and (len(match[2]) == 1):
            item = re.sub(match[0], match[2]*3, item)
            #print match
    return item

#item = stripArr(tagArr, item, "/UH")
def stripArr(tagArr, item, tag):
    #strip tag(/UH) in item range of tagArr
    if item is None:
        return None
    st = item[0]
    ed = item[1]
    while tagArr[st] == tag:
        st += 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    while tagArr[ed] == tag:
        ed -= 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    return (st, ed)

def analyzeElement(element):
    eleArr = element.split("/")
    word = eleArr[0]
    netag = eleArr[1]
    postag = eleArr[2]
    evtag = eleArr[3]
    return [word, netag, postag, evtag]


####################################
#get open domain event phrases by twitter_nlp tool)
def getodevt(filename):
    relFile = file(filename)
    outputDir = os.path.split(filename)[0]
    tStr = filename[-6:-4]
    print "Processing " + filename + " time window: " + tStr
    outputFile = file(outputDir + r"/relSkl_2013-01-" + tStr, "w")
    gram_1 = 0
    gram_2 = 0
    gram_3 = 0
    lineIdx = 0
    while 1:
        lineStr = relFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. " + str(time.asctime())
            break
        arr = lineStr.split(" ")
        #print arr
        tid = tStr+str(lineIdx)
        text = ""

        # tagsArr: [word, netag, postag, evtag] tagID is the element id
        evtphases = getPhraseIdx(arr, 3)
        nes = getPhraseIdx(arr, 1)
        for evt_st in evtphases:
            evt_ed = evtphases[evt_st]
            relArr = []
            arg1Idx = None
            arg2Idx = None
            arg1 = ""
            arg2 = ""
            if len(nes) > 0:
                lidx = evt_st
                while lidx >= 0:
                    if lidx in nes and nes[lidx] < evt_st:
                        arg1Idx = [lidx, nes[lidx]]
                        break
                    lidx -= 1
                ridx = evt_ed
                while ridx < len(arr):
                    if ridx in nes:
                        arg2Idx = [ridx, nes[ridx]]
                        break
                    ridx += 1
            if arg1Idx is not None:
                arg1 = getContent(arr[arg1Idx[0]:arg1Idx[1]+1])
            if arg2Idx is not None:
                arg2 = getContent(arr[arg2Idx[0]:arg2Idx[1]+1])

            # statistical information
            if len(arg1)*len(arg2) != 0:
                gram_3 += 1
            elif len(arg1)==0 and len(arg2)==0:
                gram_1 += 1
            else:
                gram_2 += 1

            relArr.append(normRep(arg1))
            relArr.append(normRep(getContent(arr[evt_st:evt_ed+1])))
            relArr.append(normRep(arg2))
            #print relArr
            text += (" " + "|".join(relArr))
            
        if len(text) > 1:
            text = text.lower()
            outputFile.write(tid + "\t" + text + "\n")
            #print "## " + tid + " " + text

        lineIdx += 1
        if lineIdx % 100000 == 0:
            print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime())
    print "# length of rels: ",
    print [gram_1, gram_2, gram_3]
    outputFile.close()
    relFile.close()

def getPhraseIdx(arr, tagID):
    phrasesIdxHash = {}
    i = 0
    while i < len(arr):
        # tagsArr: [word, netag, postag, evtag]
        tagsArr = analyzeElement(arr[i])
        if tagsArr[tagID].startswith("B-"):
            start = i
            end = i
            for j in range(i+1, len(arr)):
                tagsArr_next = analyzeElement(arr[j])
                if tagsArr_next[tagID].startswith("I-"):
                    end = j
                else:
                    break
            phrasesIdxHash[start] = end
            i = end + 1
            continue
        i += 1
    return phrasesIdxHash

def getContent(arr):
    contentArr = []
    for it in arr:
        tagsArr = analyzeElement(it)
        contentArr.append(tagsArr[0])
    return "_".join(contentArr)

def getArg(item):
    if len(item) > 0:
        return "_".join(normMen(item.split(" ")))
    else:
        return item

####################################
#main
filename = sys.argv[1]

if len(sys.argv) == 2:
    getodevt(filename) # extract frame from tagged files processed by twitter_nlp
else:
    print "Usage getOdevt.py tagFileName"
    sys.exit()

print "Program ends at " + str(time.asctime())
