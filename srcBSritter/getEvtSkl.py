import os
import sys
import re
import time
import cPickle
import random

sys.path.append("/home/yxqin/Scripts")
from strOperation import * # normRep and cleanStr
from hashOperation import * # cumulativeInsert

#from synConstraint_reverb import * # getVerbs(get verbs satisfy regular expression), mergeAdj (merge adjacent verb rels)

###################################
# get neTag, posTag, evtTag from mixed tagArr
# format: party/O/NN/B-EVENT  push/O/VB/B-EVENT  edinburgh/B-geo-loc/NNP/O
def splitTags(arr):
    wordArr = [item[:item.find("/")] for item in arr]
    evtTagArr = [item[item.rfind("/")+1:] for item in arr]
    
    tagsArr = [item[item.find("/")+1:item.rfind("/")] for item in arr]
    neTagArr = [item[:item.rfind("/")] for item in tagsArr]
    posTagArr = [item[item.rfind("/")+1:] for item in tagsArr]

    return wordArr, neTagArr, posTagArr, evtTagArr

####################################
#get relation skeletons from nlp-ritter's output (ne, event, ne)
def getEvtskl(filename):
    print "Processing " + filename
    posFile = file(filename)
    outputDir = os.path.split(filename)[0]
    tStr = filename[-6:-4]#[:3]#[-5:-3]

    outputFile = file(outputDir + r"/relSkl_2013-01-" + tStr, "w")

    evtOnlyStatisticHash = {}
    evtOnlyLengthHash = {}
    evtLengthHash = {}

    rndLines = random.sample(range(0, 10000), 100)

    lineIdx = 0 # line number in original file
    evtLineIdx = 0 # line number in evtSkl file
    while 1:
        lineStr = posFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. " + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        lineIdx += 1

#        print "************************* " + str(lineIdx)
        arr = lineStr.split(" ")
#        print arr

        [wordArr, neTagArr, posTagArr, evtTagArr] = splitTags(arr)
#        print wordArr
#        print neTagArr
#        print posTagArr
#        print evtTagArr

        # skip tweets with /FW(foreign word)
        fwArr = [1 for tag in posTagArr if tag.startswith("/FW")]
        if len(fwArr) > 0:
            #print "#tweet with FW: " + lineStr
            continue
        
        evtIndex = getEvents(evtTagArr)

        tripleIndex = getNEArgs(evtIndex, neTagArr, posTagArr, wordArr)

        if tripleIndex is None:
            continue

        resultArr = []
        for tripleItem in tripleIndex:
            [leftNE, evtItem, rightNE] = tripleItem
            cumulativeInsert(evtLengthHash, evtItem[1]-evtItem[0]+1, 1)
            if leftNE is None and rightNE is None:
#                print arr
                cumulativeInsert(evtOnlyStatisticHash, "_".join(posTagArr[evtItem[0]:evtItem[1]+1]), 1)
                cumulativeInsert(evtOnlyLengthHash, evtItem[1]-evtItem[0]+1, 1)
#                print "**Evt only", ed-st+1, wordArr[st:ed+1], posTagArr[st:ed+1]
    #            if "NN" in posTagArr[st:ed+1]
    #            else:
                continue
#            print tripleItem
            resultArr.append("|".join([getWord(wordArr, leftNE), getWord(wordArr, evtItem), getWord(wordArr, rightNE)]))


#        if lineIdx % 10 == 0:
#            break

        if len(resultArr) > 0:
            evtLineIdx += 1
#            print resultArr
            if evtLineIdx in rndLines:
                outputFile.write(lineStr + "\n")
                outputFile.write(tStr+str(lineIdx-1) + "\t" + " ".join(resultArr) + "\n")
           
        if lineIdx % 10000 == 0:
            print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime())
    outputFile.close()
    posFile.close()

    # output debug statistic information
    print "****Evt statistic", sum(evtLengthHash.values()), sorted(evtLengthHash.items(), key = lambda a:a[1], reverse=True)
    print "****Evt only statistic", sum(evtOnlyLengthHash.values()), sorted(evtOnlyLengthHash.items(), key = lambda a:a[1], reverse=True)

    for i in range(11):
        if i in evtOnlyLengthHash:
            print i, evtOnlyLengthHash[i], evtLengthHash[i], evtOnlyLengthHash[i]*100/evtLengthHash[i]
    sortedList = sorted(evtOnlyStatisticHash.items(), key = lambda a:a[1], reverse=True)
    print "****Evt only statistic", sortedList[:50], sortedList[:-1]

def getNEArgs(evtIndex, neTagArr, posTagArr, wordArr):
    if evtIndex is None:
        return None

    tripleIndex = []

    for evtItem in evtIndex:
        [st, ed] = evtItem
        leftNEs = getTaggedEntity(neTagArr, 0, st-1)
        leftNE = None
        if leftNEs is not None:
            leftNE = leftNEs[-1]

        rightNEs = getTaggedEntity(neTagArr, ed+1, len(neTagArr)-1)
#        print "rightNEs", rightNEs
        rightNE = None
        if rightNEs is not None:
            rightNE = rightNEs[-1]
#        print "rightNE", rightNE

        tripleIndex.append((leftNE, evtItem, rightNE))

    return tripleIndex

# BI tagged entity (named entity/event phrase)
# obtain tagged entity in tagArr, range[stIdx, edIdx]
def getTaggedEntity(tagArr, stIdx, edIdx):

#    tagArr_debug = [tagArr[i]+"_"+str(i) for i in range(len(tagArr))]
#    print tagArr_debug

    entityIndex = [] # content: [st, ed] (ed >= st)
    st = stIdx

    while st <= edIdx:
        if tagArr[st] == "O":
            st += 1
            continue
        ## st: start of an evt

        # find end of the evt from st
        ed = st + 1

        while ed <= edIdx  and tagArr[ed].startswith("I-"):
            ed += 1

        ed -= 1
        entityIndex.append((st, ed))
        st = ed + 1

    if len(entityIndex) == 0:
        return None
    return entityIndex


def getEvents(evtTagArr):
    evtIndex = getTaggedEntity(evtTagArr, 0, len(evtTagArr)-1)
#    print "evts:", evtIndex
    return evtIndex


def getRelsFromOneTweet(tagArr, arr, initNPs):

    tagStr = " ".join(tagArr) + " "
    #print "TagStr: " + tagStr

    # get verbs
    verbIdx = getVerbs(tagStr, arr)
    #print verbIdx
    ## merge adjacent verb rels
    newIdx = mergeAdj(verbIdx)
#    print newIdx

    # op1: take nearest NN as argument
    npArr = []
    #resultArr = getArgs_chunk(newIdx, tagArr, arr, npArr)

    # chunk version 0
    # op2: take nearest chunked NP as argument
    #'''
    npArr = initNPs

    #'''
    # op3: take nearest chunked NP(DIY) as argument
    # chunkNew version 1/2/3
    #print npArr
    #print arr
    npArr = getNPDIY(tagArr, npArr, arr)

    resultArr = getArgs_chunk(newIdx, tagArr, arr, npArr)
    return resultArr

########################################################
# replace mention with @usr
def normMen(relArr):
    relArrUSR = []
    for wd in relArr:
#        if wd.find("#") >= 0:
#            continue
        if len(wd) <= 0:
            continue
        if wd[0] == "@" and len(wd) > 1:
            wd = "@usr" # op1
            #continue # op2
        wd = re.sub(r"\|", "", wd) # | is used as separator later for frame
        relArrUSR.append(wd)
    return relArrUSR

def getNPs(chunkedFilename):
    npHash = {}
    # eg. r"/Chunktext_2013-01-" + tStr
    chFile = file(chunkedFilename)
    lineIdx = 0
    while 1:
        lineStr = chFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. NPs obtained." + str(time.asctime())
            break
        lineStr = lineStr[:-1]
        if lineStr[-1:] == "]":
            lineStr = lineStr[:-1] + " ]"
        lineIdx += 1

        arr = lineStr.split(" ")
        #print "**** " + str(arr)
        #wArr = [w[:w.find("/")] for w in arr if w.find("/")>=0]
        bArr = [i for i in range(len(arr)) if arr[i].find("/") < 0]
        #print bArr
        npIdx = [(bArr[2*i]+1-(2*i+1), bArr[2*i+1]-1-(2*i+1)) for i in range(len(bArr)/2)]
        #print npIdx
        #npArr = ["_".join(wArr[item[0]:item[1]+1]) for item in npIdx] 
        #print npArr

        if len(npIdx) > 0:
            npHash[lineIdx-1] = npIdx
        #if lineIdx % 100000 == 0:
            #print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime()) + " npHash: " + str(len(npHash))
            #break
    print "## " + str(len(npHash)) + " tweets contain np are obtained."
    return npHash

def getWord(wordArr, itemIdx):
    if itemIdx is None:
        return ""

    (st, ed) = itemIdx
    words = normMen(wordArr[st:ed+1])
    return "_".join(words)

def getWord_1(wordArr, st, ed):
    if st == -1:
        return ""
    words = normMen(wordArr[st:ed+1])
    return "_".join(words)
    
def normRelation(rel, arg1, arg2):
    relArr = [arg1, rel, arg2]
#    relArr = [normRep(w.lower()) for w in relArr if len(w) > 1]
    relArr = [normRep(w.lower()) for w in relArr]
    #print relArr
    return relArr

def getlnnIdxes(tagArr, st, arr):
    arg1Idx = -1
    lidx = getlnnIdx(tagArr, st)
    if lidx != -1:
        if (lidx-1 >= 0) and (tagArr[lidx-1].startswith("/NN")):
            #arg1 = getWord(arr, lidx-1, lidx)
            arg1Idx = (lidx-1, lidx)
        else:
            #arg1 = getWord(arr, lidx, lidx)
            arg1Idx = (lidx, lidx)
    return arg1Idx

def getrnnIdxes(tagArr, ed, arr):
    arg2Idx = -1
    ridx = getrnnIdx(tagArr, ed)
    if ridx != -1:
        if (ridx+1 < len(tagArr)) and (tagArr[ridx+1].startswith("/NN")):
            #arg2 = getWord(arr, ridx, ridx+1)
            arg2Idx = (ridx, ridx+1)
        else:
            #arg2 = getWord(arr, ridx, ridx)
            arg2Idx = (ridx, ridx)
    return arg2Idx

def getlnnWord(tagArr, st, arr):
    arg1 = ""
    lidx = getlnnIdx(tagArr, st)
    if lidx != -1:
        arg1 = getWord(arr, lidx, lidx)
    return arg1

def getrnnWord(tagArr, ed, arr):
    arg2 = "" 
    ridx = getrnnIdx(tagArr, ed)
    if ridx != -1:
        #arg2 = arr[ridx] 
        #arg2 = arg2[:arg2.rfind("/")]
        arg2 = getWord(arr, ridx, ridx)
    return arg2

def getlnnIdx(tagArr, st):
    lidx = st - 1
    while lidx >= 0:
        if not tagArr[lidx].startswith("/NN"):
            lidx -= 1
            continue
        return lidx
    return -1

def getrnnIdx(tagArr, ed):
    ridx = ed+1
    while ridx < len(tagArr):
        if not tagArr[ridx].startswith("/NN"):
            ridx += 1
            continue
        return ridx
    return -1

def lStripArr(tagArr, item, tag):
    if item is None:
        return None
    st = item[0]
    ed = item[1]
    while tagArr[st] == tag:
        st += 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    return (st, ed)

def rStripArr(tagArr, item, tag):
    #strip tag(/UH) in item range of tagArr
    if item is None:
        return None
    st = item[0]
    ed = item[1]
    while tagArr[ed] == tag:
        ed -= 1
        #print "Tag: " + tag + ": " + str(item)
        if st > ed:
            return None
    return (st, ed)

def stripArr(tagArr, item, tag):
    if item is None:
        return None
    item = lStripArr(tagArr, item, tag)
    item = rStripArr(tagArr, item, tag)
    return item

# separate NP into NPs if punctuations inside NP
def getNewNP(tagArr, item, arr):
    item = stripArr(tagArr, item, "/UH")
    item = stripArr(tagArr, item, "/,")
    item = stripArr(tagArr, item, "/.")
    # following two lines are added in Mar. 13, 2015. chunking result take ( or ) as a np
    item = stripArr(tagArr, item, "/-LRB-")
    item = stripArr(tagArr, item, "/-RRB-")
    # to be added to improve np chunking in twitter
#    if item[1]-item[0] > 0:
#        item = rStripArr(tagArr, item, "URL")
#        item = rStripArr(tagArr, item, "HT")


    if item is None:
        return None

    newItems = []
    st = item[0]
    ed = item[1]

    # split NPs with /, /. tag
    puncArr = [id for id in range(st, ed+1) if (tagArr[id].startswith("/,") or tagArr[id].startswith("/."))]
    if len(puncArr) > 0:
        #print "NP with punc: " + "_".join(arr[item[0]:item[1]+1])
        #if len(puncArr) > 1:
            #print "##Multiple puncs"
        i = 0
        while i < len(puncArr):
            id = puncArr[i]
            if tagArr[id-1].startswith("/NN"):
                if i == 0:
                    newItems.append((st, id-1))
                else:
                    newItems.append((puncArr[i-1]+1, id-1))
            if i == len(puncArr)-1:
                if tagArr[ed].startswith("/NN"):
                    newItems.append((puncArr[i]+1, ed))
            i += 1
    else:
        newItems.append((st, ed))

    #print newItems

#    # chunkNewV1-part2
#    # chunkNewV2 skip this part compared with V1
#    # do not use this part in chunkNewV2 and later chunkNew version(appeared in V4)
#    # lead to worse precision
#    items = []
#    for it in newItems:
#        st = it[0]
#        ed = it[1]
#        # delete chunk without /NN
#        nounArr = [id for id in range(st, ed+1) if tagArr[id].startswith("/NN")]
#        if len(nounArr) < 1:
#            #print "chunk without noun: " + "_".join(arr[st: ed+1])
#            continue
#        usrArr = [id for id in range(st, ed+1) if not arr[id].startswith("@")]
#        # check chunks with length >= 5
#        if ed-st+1 >= 5:
#            if ed-st+1-len(usrArr) < 5: # < 5 when delete @usr(later)
#                items.append((st,ed))
#            if len(nounArr) <= 3:
#                items.append((st,ed))
#        
#    return items

    return newItems
    
def getNPDIY(tagArr, npArr, arr):
    if npArr is None:
        return None
    newNPArr = []
    #print "*************************************"
    #print tagArr
    #print npArr
    for item in npArr:
        newItems = getNewNP(tagArr, item, arr)
        if newItems is not None:
            newNPArr.extend(newItems)
    #print newNPArr
    return newNPArr

# should not be EX, WDT, WP, WP$
def validArg(idx_tuple, arr, tagArr):
    tags_arg = tagArr[idx_tuple[0]:idx_tuple[1]+1]
    tags_arg = [tag[tag.find("/")+1:]for tag in tags_arg]
    inValidTags = ['WDT', 'WP', 'WP$', # relative pronoun, which, that, who, whom, whose
#            '', # who-adverb ??
            'EX'] # existential there
    invalid = [1 for tag in tags_arg if tag in inValidTags]
    if len(invalid) > 0:
        return False
    return True


def getRelationIdx(newIdx, tagArr, arr, npArr):
    relationIdxArr = []
    for st in sorted(newIdx.keys()):
        ed = newIdx[st]

        relIdx = (st, ed)
        [arg1Idx, arg2Idx] = getArgsIdx_chunk(relIdx, tagArr, arr, npArr)

        relationIdxArr.append((relIdx, arg1Idx, arg2Idx))
    return relationIdxArr


def getArgs_chunk_new(newIdx, tagArr, arr, npArr):
    resultArr = []
    # detect argument in left and right
    relationIdxArr = getRelationIdx(newIdx, tagArr, arr, npArr)

    for relationIdx in relationIdxArr:
        [relIdx, arg1Idx, arg2Idx] = relationIdx

        rel = getWord(arr, relIdx[0], relIdx[1])
        arg1 = getWord(arr, arg1Idx[0], arg1Idx[1])
        arg2 = getWord(arr, arg2Idx[0], arg2Idx[1])

        relArr = normRelation(rel, arg1, arg2)
#        if rel not in lexHash: # lexical constraint
#            continue

        if len(relArr) != 3:
            print "Not triple."
            continue

        resultArr.append("|".join(relArr))
    return resultArr


def getArgs_chunk(newIdx, tagArr, arr, npArr):
    global confFeas
    resultArr = []
    for st in sorted(newIdx.keys()):
        ed = newIdx[st]
        arg1 = "" 
        arg2 = "" 

        relIdx = (st, ed)
        rel = getWord(arr, st, ed)
#        if rel not in lexHash: # lexical constraint
#            continue

        [arg1Idx, arg2Idx] = getArgsIdx_chunk(relIdx, tagArr, arr, npArr)

        arg1 = getWord(arr, arg1Idx[0], arg1Idx[1])
        arg2 = getWord(arr, arg2Idx[0], arg2Idx[1])

        relArr = normRelation(rel, arg1, arg2)
#        print rel
#        print "relation: ",
#        print relArr

        # calculate confidence
#        confArr = fea_Conf(arr, tagArr, relArr, rel, st, ed, arg1Idx, arg2Idx)
#
#        for i in range(len(confFeas)):
#            if confArr[i] == 1:
#                confFeas[i] += 1
#        confVal = confidence(confArr)
#        #print confArr
#        if confVal <= 0:
#            #print "Skip " + str(relArr) + "\t" + str(confVal)
#            continue
#        #else:
#            #print "Keep " + str(relArr) + "\t" + str(confVal)

        #if len(relArr) > 0:
            #resultArr.append("|".join(relArr))
        if len(relArr) != 3:
            print "Not triple."
            continue

#        for rel in relArr:
#            if rel.find("|") >= 0:
#                print arr
#                print "| appeared in rel: ", rel


#        global lvHash
#        print "-- relword: ", relArr[1]
#        lvArr = ["is", "do", "give", "have", "make", "take", "get", "was", "were", "are", "did", "does", "gave", "had", "has", "makes", "made", "takes", "took", "gets", "got"]
#        relWords = relArr[1].split("_")
#        if len(relWords)==1 and relArr[1] in lvArr:
#            print "-- verb=lv: ", relArr[1], " ", arr
#            if relArr[1] in lvHash:
#                lvHash[relArr[1]] += 1
#            else:
#                lvHash[relArr[1]] = 1
#        else:
#            for w in relWords:
#                if w in lvArr:
#                    print "-- contain lv-verb: ", relArr[1], " ",arr
#                    tmpWord = "c-"+w
#                    if tmpWord in lvHash:
#                        lvHash[tmpWord] += 1
#                    else:
#                        lvHash[tmpWord] = 1


        # triple structure
        resultArr.append("|".join(relArr))

        # 2-tuple structure
        #resultArr.append("|".join(relArr[0:2]))
        #resultArr.append("|".join(relArr[1:]))
    return resultArr


def getArgsIdx_chunk(relIdx, tagArr, arr, npArr):
    st = relIdx[0]
    ed = relIdx[1]

    arg1Idx = -1
    arg2Idx = -1

    if npArr is not None and len(npArr) > 0:# with chunking results
        idx = len(npArr)-1
        while idx >= 0:
            item = npArr[idx]
            
            if item[1] < st and validArg(item, arr, tagArr):
                #arg1 = getWord(arr, item[0], item[1])
                arg1Idx = item
                break
            idx -= 1
        idx = 0
        while idx < len(npArr):
            item = npArr[idx]
            if item[0] > ed and validArg(item, arr, tagArr):
                #arg2 = getWord(arr, item[0], item[1])
                arg2Idx = item
                break
            idx += 1
    else: # no chunking results
        ## get nearest /NN tagged word
#            arg1 = getlnnWord(tagArr, st, arr)
#            arg2 = getrnnWord(tagArr, ed, arr)

    ## get nearest /NN tagged word[s]
        arg1Idx = getlnnIdxes(tagArr, st, arr)
        arg2Idx = getrnnIdxes(tagArr, ed, arr)

    ## chunkNewV3: if no chunk is found for argument, take nearest nn as argument
    ## get Index 2/24/2014
    if arg1Idx == -1:
        arg1Idx = getlnnIdx(tagArr, st)
        arg1Idx = (arg1Idx, arg1Idx)
    if arg2Idx == -1:
        arg2Idx = getrnnIdx(tagArr, ed)
        arg2Idx = (arg2Idx, arg2Idx)

    ## In chunkNewV3
    # getWord directly
#    if len(arg1) <= 1:
#        ## get nearest /NN tagged word
#        arg1 = getlnnWord(tagArr, st, arr)
#    if len(arg2) <= 1:
#        arg2 = getrnnWord(tagArr, ed, arr)

    ## chunkNewV3_NNs: if no chunk is found for argument, take nearest NN[s] as argument
    # worse than chunkNewV3
#    if len(arg1) <= 1:
#        ## get nearest /NN tagged word[s]
#        arg1 = getlnnWords(tagArr, st, arr)
#    if len(arg2) <= 1:
#        arg2 = getrnnWords(tagArr, ed, arr)


    return arg1Idx, arg2Idx


def isNP(tagArr, wIdx):
    st = wIdx[0]
    ed = wIdx[1]
    if st == -1:
        return False
    if tagArr[ed].startswith("/NNP"):
        return True
    return False
  
####################################
#main
if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        getEvtskl(filename)
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        chunkedFilename = sys.argv[2]
        getEvtskl_chunkArg(filename, chunkedFilename) 
    else:
        print "Usage getEvtSkl.py posFileName [chunkedFileName] "
        sys.exit()
    
    print "Program ends at " + str(time.asctime())
