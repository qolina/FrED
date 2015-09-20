#! /usr/bin/env python
# -*- coding: utf-8 -*-
#author: qolina
#Function: extract structured or string version of skeleton from parsed tweets

import os
import re
import time
import sys
import cPickle

class Parsedtweet:
    def __init__(self, id, wordarr):
        self.id = id
        self.words = wordarr

## depRel in relSet: headWord__headTag||dependentWord__dependentTag||relname
class Skeleton:
    def __init__(self, id, relSet):
        self.id = id
        self.relSet = relSet

#''' -not used, convert to string format
class DepRel:
    def __init__(self, head, dependent, relname):
        self.head = head
        self.dependent = dependent
        self.relname = relname

class TGWord:
    def __init__(self, id, word, tag):
        self.id = id
        self.word = word
        self.tag = tag
#'''

########################################################
## Load users and tweets from files in directory dirPath
def extractSekeleton(filepath, outdirPath):
    global IDMAP
    avgNounNum = 0.0
    relNum = 0
    nounsNumInRel = 0
    wordsNumInRel = 0
    vbnnpNum = 0
    nnpNum = 0
    subFile = file(filepath)
    print "Processing file: " + filepath
    day = filepath[-5:-3]
    idFilepath = r"../data/201301_preprocess/tid_2013-01-"+day
    IDArr = loadID(idFilepath)
    textFilepath = r"../data/201301_preprocess/text_2013-01-"+day
    textWordArr = loadText(textFilepath)
    sklFile = file(outdirPath + "/skl_2013-01-"+day, "wb")
    idmapFile = file(outdirPath + "/IDmap_2013-01-"+day, "w")

    idx = 0
    wordarr = []
    tweetNum = 0
    while True:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        if len(lineStr) <= 0:
            break

        lineStr = lineStr.lower()
        arr = lineStr.split("\t")
        if len(arr) == 4: # get parsedtweet
            arr[3] = arr[3][:-1]
            wordarr.append(arr)
        else: # end of current parsedtweet
            '''
            if lineStr != " ":
                print "---Line " + str(idx) + ": " + lineStr + " -VS-" + str(arr)
            else:
                print "---Normal Line " + str(idx) + ": " + lineStr + " wordNum: " + str(len(wordarr))
            '''
            if wordarr[0][0] == textWordArr[idx].lower():
                print "---Normal Line " + str(idx) + ": " + lineStr + " wordNum: " + str(len(wordarr))
            else:
                print "---Line " + str(idx) + ": " + wordarr[0][0] + "-VS-" + textWordArr[idx]

            tweetid = IDArr[idx]
            IDMAP[idx] = tweetid
            psid = day + str(idx)
            pstweet = Parsedtweet(psid, wordarr)
            '''----print parsedTweets
            print "-------ParsedTweet: " + psid
            for oid in range(0, len(wordarr)):
                print str(oid) + " " + "\t".join(wordarr[oid])
            '''
            if len(wordarr) > 1:
                # get skeleton
                #relSet = getRels_verb(pstweet)
                #[relSet,avgNoun, nouns, words] = getRels_verbCalculateNoun(pstweet)
                #[relSet, vnp, nnp] = getRels_verbPlusNNP(pstweet)
                #relHash = getRels_subtree(pstweet)
                relHash = getRels_mod(pstweet)
                relSet = relHash.keys()
                
                '''----print relSet
                print "----- skeletons"
                print pstweet.id + "\t" + " ".join(relSet)
 #               for oid in xrange(0, len(relSet)):
 #                   print str(oid) + " " + relSet[oid].head.word + " " + relSet[oid].dependent.word + " " + relSet[oid].relname
                print "-------------------------\n"
                '''
                if len(relSet) > 1:
                    ''' #structured skeleton
                    skltweet = Skeleton(pstweet.id, relSet)
                    cPickle.dump(skltweet, sklFile)
                    '''
                    # string version skl
                    #print pstweet.id + "\t" + " ".join(relSet)
                    sklFile.write(pstweet.id + "\t" + " ".join(relSet) + "\n")
                    tweetNum += 1

                    # calculate avgNoun
                    relNum += len(relSet)
                    '''
                    vbnnpNum += vnp
                    nnpNum += nnp
                    avgNounNum += avgNoun
                    wordsNumInRel += words
                    nounsNumInRel += nouns
                    '''
                    if tweetNum % 100000 == 0:
                        print "# tweets processed: " + str(tweetNum) + " at " + str(time.asctime())
                        #break

            idx += 1
            del wordarr[:]
            continue
    cPickle.dump(IDMAP, idmapFile)
    idmapFile.close()
    sklFile.close()
    subFile.close()
    print "Writing skl done, " + str(tweetNum) + " tweets at " + str(time.asctime()) + " to file: " + sklFile.name
    print "Writing tweetID-sklID maps done, " + str(len(IDMAP)) + " at " + str(time.asctime()) + " to file: " + idmapFile.name
    print "## relnum: " + str(relNum) + ", avgRelInTweet" + str(relNum*1.0/tweetNum)
    print "## vbnnpnum: " + str(vbnnpNum) + ", nnp num: " + str(nnpNum)
    print "Avg nouns in rels, " + str(avgNounNum/relNum)
    print "## " + str(wordsNumInRel) + " words in " + str(relNum) + " rels. " + str(nounsNumInRel) + " nouns in these words. ratio: " + str(nounsNumInRel*1.0/wordsNumInRel)
    
##################################################
def loadID(filepath):
    idFile = file(filepath)
    idarr = idFile.readlines()
    idarr = list(id[:-1] for id in idarr)
    idFile.close()
    print "Loading ids done, " + str(len(idarr)) + " at " + str(time.asctime()) + " from file: " + filepath 
    return idarr
    
##################################################
def loadText(filepath):
    textFile = file(filepath)
    textarr = []
    tweetNum = 0
    while True:
        lineStr = textFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        if len(lineStr) <= 0:
            break
        arr = lineStr.split(" ")
        textarr.append(arr[0])
        tweetNum += 1
    textFile.close()
    print "Loading texts done, " + str(len(textarr)) + " at " + str(time.asctime()) + " from file: " + filepath 
    return textarr

########################################################
# got dependents for words with specific tag
# tag "all" means get dependents for all words
def getTagDepts(pstweet, tagname):
    wordarr = pstweet.words
    tagDeptHash = {}
    for id in xrange(0, len(wordarr)):
        if tagname == "all":
            tagDeptHash[id] = []
        else:
            if wordarr[id][1].startswith(tagname):
                tagDeptHash[id] = []
    for id in xrange(0, len(wordarr)):
        headid = int(wordarr[id][2])
        if headid in tagDeptHash:
            tagDeptHash[headid].append(id)
    newHash = dict([(id, tagDeptHash[id]) for id in tagDeptHash if len(tagDeptHash[id]) > 0])
    #print tagname + " related depts: " + str(newHash)
    return newHash

########################################################
# replace mention with @usr
def normMen(relArr):
    relArrUSR = []
    for wd in relArr:
        if wd[0] == "@":
            wd = "@usr"
        relArrUSR.append(wd)
    return relArrUSR
    
########################################################
# all rels matching [[nmod] sub] root [obj]
def getRels_sub(pstweet):
    debug = False
    wordarr = pstweet.words
    relSet = []
    for id in xrange(0, len(wordarr)):
        if wordarr[id][3] != "root":
            continue
        for pid in xrange(id, -1, -1):
            if wordarr[pid][3] != "sub":
                continue
            for psid in xrange(pid, -1, -1):
                if wordarr[psid][3] != "nmod":
                    continue
                nmodRel = getRel(pstweet, psid)
                relSet.append(nmodRel)
                break
            subRel = getRel(pstweet, pid)
            relSet.append(subRel)
        rootRel = getRel(pstweet, id)
        relSet.append(rootRel)
        for fid in xrange(id, len(wordarr)):
            if wordarr[fid][3] != "obj":
                continue
            objRel = getRel(pstweet, fid)
            relSet.append(objRel)
    if debug:
        print "relSet get in Func getRels_sub " + "###".join(relSet)
    return relSet
                
########################################################
# all rels related to ROOT
def getRels_root(pstweet):
    wordarr = pstweet.words
    relSet = []
    for id in xrange(0, len(wordarr)):
        if wordarr[id][3] != "root":
            continue
        rootRel = getRel(pstweet, id)
        relSet.append(rootRel)
        for pid in xrange(0, len(wordarr)):
            if wordarr[pid][2] != str(id):
                continue
            if wordarr[pid][3] == 'p':
                continue
            rootlinkRel = getRel(pstweet, pid)
            relSet.append(rootlinkRel)
    return relSet

########################################################
# all verb, and nearby related words
# delete punctuations in relStr
# replace all mention with @uar
def getRels_verb(pstweet):
    wordarr = pstweet.words
    relSet = []
    vbDeptHash = getTagDepts(pstweet, "vb")
    for headid in vbDeptHash:
        deptNum = 0
        for deptid in vbDeptHash[headid]:
            hheadid = int(wordarr[headid][2])
            relIDs = sorted(list([hheadid, headid, deptid]))
            deptNum += 1
            relArr = list([wordarr[id][0] for id in relIDs if ((id >= 0) and (wordarr[id][1] != "."))])
            relArrUSR = normMen(relArr)
            relStr = "_".join(relArrUSR)
            relSet.append(relStr)
        if deptNum == 0:
            relSet.append(wordarr[headid][0])
    return relSet

########################################################
# besides getRels_verb. Added calculate number of nouns in verb-related rels
def getRels_verbCalculateNoun(pstweet):
    relSet = []
    avgNoun = 0.0
    nouns = 0
    words = 0
    wordarr = pstweet.words
    vbDeptHash = getTagDepts(pstweet, "vb")
    for headid in vbDeptHash:
        deptNum = 0
        for deptid in vbDeptHash[headid]:
            hheadid = int(wordarr[headid][2])
            relIDs = sorted(list([hheadid, headid, deptid]))
            deptNum += 1
            relArr = list([wordarr[id][0] for id in relIDs if ((id >= 0) and (wordarr[id][1] != "."))])
            relArrUSR = normMen(relArr)
            relStr = "_".join(relArrUSR)
            relSet.append(relStr)
            # calculate number of nouns related to rels
            nounsList = list([1 for id in relIDs if ((id >= 0) and (wordarr[id][1] != ".") and (wordarr[id][1].startswith("nn")))])
            avgNoun += sum(nounsList)*1.0/len(relArr)
            nouns += sum(nounsList)
            words += len(relArr)
        if deptNum == 0:
            relSet.append(wordarr[headid][0])
            words += 1
    return relSet, avgNoun, nouns, words

########################################################
# besides getRels_verb. Added [nmod] + NNP + nearest verb
def getRels_verbPlusNNP(pstweet):
    vnp = 0
    relSet = getRels_verb(pstweet)
    wordarr = pstweet.words
    nnpDeptHash = getTagDepts(pstweet, "nnp")
    for headid in nnpDeptHash:
        deptNum = 0
        for deptid in nnpDeptHash[headid]:
            if (wordarr[deptid][3] != "nmod") and (not wordarr[deptid][1].startswith("vb")):
                continue
            deptNum += 1
            if wordarr[deptid][1].startswith("vb"):
                vnp += 1
            hheadid = int(wordarr[headid][2])
            relIDs = sorted(list([hheadid, headid, deptid]))
            relArr = list([wordarr[id][0] for id in relIDs if ((id >= 0) and (wordarr[id][1] != "."))])
            relArrUSR = normMen(relArr)
            relStr = "_".join(relArrUSR)
            relSet.append(relStr)
        if deptNum == 0:
            relSet.append(wordarr[headid][0])
    return relSet, vnp, len(nnpDeptHash)

########################################################
# extract all modifiers with a word
def getRels_mod(pstweet):
    relSet = {}
    wordarr = pstweet.words
    deptHash = getTagDepts(pstweet, "all")
    for headid in range(len(wordarr)):
        if headid not in deptHash:
            relIDs = list([headid])
        else:    
            depArr = deptHash[headid]
            relIDs = list([id for id in depArr])
            relIDs.append(headid)
        relStr = getRelStr(wordarr, relIDs)
        relSet[relStr] = 1
    return relSet

########################################################
# extract all 2-degree subtrees 1-degree
def getRels_subtree(pstweet):
    relSet = {}
    wordarr = pstweet.words
    deptHash = getTagDepts(pstweet, "all")
    for headid in deptHash:
        '''
        # 0-degree
        relStr0 = getRelStr(wordarr, list([headid]))
        relSet[relStr0] = 1
        '''
        hheadid = int(wordarr[headid][2])
        relIDs_hd = list([hheadid, headid])
        if hheadid != -1:
            hhheadid = int(wordarr[hheadid][2])
            relIDs_hd.append(hhheadid)
        if headid not in deptHash:
            relStr = getRelStr(wordarr, relIDs_hd)
            relSet[relStr] = 1
            #'''
            # 1-degree
            relStr1 = getRelStr(wordarr, list([hheadid, headid]))
            relSet[relStr1] = 1
            #'''
            continue
        for deptid in deptHash[headid]:
            relIDs_hddp = list([id for id in relIDs_hd])
            relIDs_hddp.append(deptid)
            #'''
            # 1-degree
            relStr1 = getRelStr(wordarr, list([hheadid, headid, deptid]))
            relSet[relStr1] = 1
            #'''
            if deptid not in deptHash:
                relStr = getRelStr(wordarr, relIDs_hddp)
                relSet[relStr] = 1
            else:
                for ddeptid in deptHash[deptid]:
                    relIDs_hddpdp = list([id for id in relIDs_hddp])
                    relIDs_hddpdp.append(ddeptid)
                    relStr = getRelStr(wordarr, relIDs_hddpdp)
                    relSet[relStr] = 1
    return relSet

def getRelStr(wordarr, relIDs):
    relIDs_filtered = list([id for id in relIDs if ((id>=0) and (wordarr[id][1] not in list(['.',',',':'])) and (wordarr[id][1]!="uh"))])
    #print relIDs_filtered
    relArr = list([wordarr[id][0] for id in sorted(relIDs_filtered)])
    relArrUSR = normMen(relArr)
    relStr = "_".join(relArrUSR)
    return relStr

########################################################
'''wordarr: word wordTag headid relname
'''
def getRel(pstweet, depid):
    debug = False
    wordarr = pstweet.words
    depArr = wordarr[depid]
    dependent = TGWord(depid, depArr[0], depArr[1])
    dependent = getWord(depid, depArr)
    relname = depArr[3]

########################################################
'''wordarr: word wordTag headid relname
'''
def getRel(pstweet, depid):
    debug = False
    wordarr = pstweet.words
    depArr = wordarr[depid]
    dependent = TGWord(depid, depArr[0], depArr[1])
    dependent = getWord(depid, depArr)
    relname = depArr[3]
    if relname == 'root':
        head = getWord(-1, list(["None","None","None","None"]))
    else:
        head = getWord(int(depArr[2]), wordarr[int(depArr[2])])
    if debug:
        print "DepArr: " + str(depArr)
        print "Dept: " + dependent
        print "Head: " + head
    #rel = DepRel(head, dependent, relname)
    #rel = "||".join(list([head, dependent, relname]))
    rel = "_".join(list([dependent, head]))
    return rel

########################################################
'''wArr: word wordTag headid relname
'''
def getWord(depid, wArr):
    #Use TagWord
    #word = TGWord(depid, wArr[0], wArr[1])

    #Use wordContent__wordTag
    #depRep: headWord__headTag||dependentWord__dependentTag||relname
    #word = "__".join(wArr[0:2])

    #Use wordContent
    #depRep: headWord||dependentWord||relname
    word = wArr[0]
    return word

########################################################
## the main Function
print "Program starts at time:" + str(time.asctime())

IDMAP = {}
if len(sys.argv) == 2:
    extractSekeleton(sys.argv[1], "./")
elif len(sys.argv) == 3:
    extractSekeleton(sys.argv[1] + r"/" + sys.argv[2], sys.argv[1])
else:
    print "Usage: python getSkeleton.py -dirpath -filename\n e.g.: python getSkeleton.py ../parsedTweet Tagtext_2013-01-01.ps"
    print "       To change format of depRel(Tagword|wordContent__wordTag|wordContent), refer to getWord() "

print "Program ends at time:" + str(time.asctime())
