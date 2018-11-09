#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys
import cPickle
import math

sys.path.append(os.path.expanduser("~")+"/Scripts")
from hashOperation import *

from preProcessTweetText import *
from zpar import ZPar
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeHash, edgeHash):
        self.nodeHash = nodeHash
        self.edgeHash = edgeHash

def statisticDF_fromFile(dataFilename, predefinedUnitHash):
    unitAppHash = {} #unit:df_t_hash
    #df_t_hash --> tweetIDStr:1
    inFile = file(dataFilename)

    tweetNum_t = 0
    while 1:
        lineStr = inFile.readline()
        if not lineStr:
            print "##End of reading file. [statisticDF from text file] ", time.asctime(), inFile.name , " units: ", len(unitAppHash), " tweets:", tweetNum_t
            break

        contentArr = lineStr.rstrip().split("\t")
        # lineStr frame format: tweetIDstr[\t]tweetText
        if len(contentArr) < 2: 
            print "**less than 2 components", contentArr
            continue
        tweetIDstr = contentArr[0]
        tweetText = contentArr[-1].lower()
        tweetNum_t += 1

        # use frame element
        # tweetText: frm1[1space]frm2 frm3...
        # frame: arg1|vp|arg2   frmEle: word1_word2_...
        tweetText = re.sub("\|", " ", tweetText)
        textArr = tweetText.strip().split(" ")

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
                apphash = {}
                if unit in unitAppHash:
                    apphash = unitAppHash[unit]
                apphash[tweetIDstr] = 1
                unitAppHash[unit] = apphash 
        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))
    inFile.close()
    return unitAppHash


def statisticDF(dataFilePath, predefinedUnitHash):
    global twHash,subtwHash
    twContent = file("../ni_data/tweet_id_tw_subtw.txt").readlines()
    twContent = [line.strip().split(" ") for line in twContent]
    twHash = dict(zip(range(len(twContent)), [item[1] for item in twContent]))
    subtwHash = dict(zip(range(len(twContent)), [item[2] for item in twContent]))

    stopFileName = r"../Tools/stoplist.dft"
    stopwordHash = loadStopword(stopFileName)

    unitHash = {} #unit:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1
    windowHash = {} # timeSliceIdStr:tweetNum

    inFile = file(dataFilePath)
    print "### Processing " + inFile.name
    tweetNum_t = 0
    while 1:
        lineStr = inFile.readline()
        if not lineStr:
            break

        contentArr = lineStr.strip().split("\t")
        # lineStr frame format: tweetIDstr[\t]tweetText
        if len(contentArr) < 2: 
            print "**less than 2 components", contentArr
            continue
        
        tweetIDstr = contentArr[0]
        tweetText = contentArr[-1].lower()
        tweetNum_t += 1

        tStr = twHash[int(tweetIDstr)]
        if tStr in windowHash: windowHash[tStr] += 1
        else: windowHash[tStr] = 1

        # use frame element
        # tweetText: frm1[1space]frm2 frm3...
        # frame: arg1|vp|arg2   frmEle: word1_word2_...
        tweetText = re.sub("\|", " ", tweetText)
        textArr = tweetText.strip().split(" ")
        # del stop words
        textArr = tweetArrClean_delStop(textArr, stopwordHash)
        textArr = tweetArrClean_delUrl(textArr)

        for unit in textArr:
            if len(unit) < 1:
                continue
            # for testing bursty methods
            # predefinedUnitHash usually is bursty skl hash
            if predefinedUnitHash is not None:
                #if re.sub(r"\|", "_", unit).strip("_") not in sklHash: # use frame
                if unit not in predefinedUnitHash: # use frame element or segment
                    continue

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

        if tweetNum_t % 500000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))
    inFile.close()
    print "### In total(whole corpora) ", len(unitHash), UNIT, "s are loaded!"
    return unitHash, windowHash

# calculate ps
def calunitps(unitHash, windowHash):
    unitpsHash = {}
    unitNum = 0
    for unit in sorted(unitHash.keys()):
        unitNum += 1
        df_hash = unitHash[unit]

        prob_hash = dict([(t, len(df_hash[t])*1.0/windowHash[t]) for t in df_hash if len(df_hash[t])>0])
        l = len(prob_hash)
        probTemp = sum(prob_hash.values())
        prob = probTemp/l

        unitpsHash[unit] = prob

        if unitNum % 500000 == 0:
            print "### " + str(unitNum) + " units' ps are processed at " + str(time.asctime())
    return unitpsHash

############################
## calculate sigmoid
def sigmoid(x):
    return 1.0/(1.0+math.exp(-x))


def calbursty(unitHash, unitpsHash, tStr, N_t):
    burstySegHash = {}
    unitInvolvedHash = {}
    for unit in unitHash:
        if tStr not in unitHash[unit]: continue
        ps = unitpsHash.get(unit)
        if ps is None: continue

        f_st = len(unitHash[unit][tStr])*1.0
        e_st = N_t * ps
        if f_st <= e_st: # non-bursty segment or word
            continue
        # bursty segment or word
        sigma_st = math.sqrt(e_st*(1-ps))
        zscore = (f_st - e_st) / sigma_st
        burstySegHash[unit] = zscore

    print "Bursty units obtained", len(burstySegHash), " in tw", tStr
    K = max(int(math.sqrt(N_t))+1, 200)
    print "Select top K (num of event " + UNIT + "): " + str(K)
    sortedList = sorted(burstySegHash.items(), key = lambda a:a[1], reverse = True)
    sortedList = sortedList[0:K]

    segList = []
    for key in sortedList:
        eventSeg = key[0]
        apphash = dict([(tid, 1) for tid in unitHash[eventSeg][tStr]])

        unitInvolvedHash.update(apphash)
        f_st = len(unitHash[eventSeg][tStr])
        segList.append((f_st, key[1], eventSeg))
    return segList, unitInvolvedHash

############################
## represent text string into tf-idf vector
def textSim(feaHash1, norm1, feaHash2, norm2):
    tSim = 0.0
    for seg in feaHash1:
        if seg in feaHash2:
            w1 = feaHash1[seg]
            w2 = feaHash2[seg]
            tSim += w1 * w2
    tSim = tSim / (norm1 * norm2)
#    print "text similarity: " + str(tSim)
#    if tSim == 0.0:
#        print "Error! textSimilarity is 0!"
#        print "vec1: " + str(norm1) + " ",
#        print feaHash1
#        print "vec2: " + str(norm2) + " ",
#        print feaHash2
    return tSim

############################
## represent text string into tf-idf vector
def toTFIDFVector(text, tStr, wordDFHash):
    #[GUA] twitterText(segment segment ...)###twitterText###...
    #[GUA] segmentDFHash mapping: twitterNum
    docArr = text.split("###")
    docId = 0
    # one word(unigram) is a feature, not segment
    feaTFHash = {}
    featureHash = {}
    norm = 0.0
    for docStr in docArr:
        docId += 1
        docStr = re.sub("\|", " ", docStr)
        segArr = docStr.split(" ")
        for segment in segArr:

            #[GUA] feaTFHash mapping: segment -> segmentFreq
            wordArr = segment.split("_")
            for word in wordArr:
                if len(word) < 1:
                    continue
                if word in feaTFHash:
                    feaTFHash[word] += 1
                else:
                    feaTFHash[word] = 1
    for word in feaTFHash:
#        tf = math.log(feaTFHash[word]*1.0 + 1.0)
        tf = feaTFHash[word] 
        if word not in wordDFHash or tStr not in wordDFHash[word]:
            #print "## word not existed in wordDFhash: " + word
            continue
        idf = math.log(TWEETNUM/wordDFHash[word][tStr])
        weight = tf*idf
        featureHash[word] = weight
        norm += weight * weight
    norm = math.sqrt(norm)
    #[GUA] featureHash mapping: segment -> tf-idf
    return featureHash, norm

#segTextHash # segId:seg's context text in time window
def calpairsim(tStr, segList, segTextHash, wordDFHash, segDFHash):
    segPairHash = {} #segId1|segId2:sim
    segVecNormHash = {} # subtw:tw_segVecNormHash
                        # tw_segVecNormHash    segId:seg vec norm
    segTVecHash = {} # subtw: tw_segTVecHash
                     # tw_segTVecHash      segId:seg's tfidf vec
    segfWeiHash = {} # subtw: tw_segfWeiHash
                     # tw_segfWeiHash      segId:seg's doc freq weight
    segNum = len(segList)
    for segId, seg in enumerate(segList):
        tw_segTVecHash = {}
        tw_segVecNormHash = {}
        tw_segfWeiHash = {}
        df_val = sum(segDFHash[segId].values())
        for subtw in segTextHash[segId]:
            tw_segfWeiHash[subtw] = segDFHash[segId][subtw]*1.0/df_val
            tw_segContextText = segTextHash[segId][subtw]
            [featureHash, norm] = toTFIDFVector(tw_segContextText, tStr, wordDFHash)
            tw_segTVecHash[subtw] = featureHash
            tw_segVecNormHash[subtw] = norm
        segTVecHash[segId] = tw_segTVecHash
        segVecNormHash[segId] = tw_segVecNormHash
        segfWeiHash[segId] = tw_segfWeiHash
        
    for i in range(0,segNum):
        for j in range(i+1,segNum):
            segPair = str(i) + "|" + str(j)
            subtwSet = set(segTVecHash[i].keys())&set(segTVecHash[j].keys())
            #print subtwSet
            if len(subtwSet) > 0:
                tSim = [textSim(segTVecHash[i][subtw], segVecNormHash[i][subtw], segTVecHash[j][subtw], segVecNormHash[j][subtw]) for subtw in subtwSet]
                segPairHash[segPair] = segfWeiHash[i][subtw]*segfWeiHash[j][subtw]*(sum(tSim)/len(tSim))
            else:
                segPairHash[segPair] = 0.0
    return segPairHash 

def calsegText(segList, unitHash, unitInvolvedHash, tStr):
    segTextHash = {}
    segDFHash = {}
    content = file("../ni_data/tweet_text.txt").readlines()
    content = [line.strip().lower() for line in content]
    involvedTweets = dict([(tid, content[int(tid)]) for tid in unitInvolvedHash])
    for segId, seg in enumerate(segList):
        seg_rel_tweets = [(tid, involvedTweets[tid], subtwHash[int(tid)]) for tid in unitHash[seg[2]][tStr]]
        tw_textHash = {}
        tw_dfHash = {}
        for subtw in set([item[2] for item in seg_rel_tweets]):
            tw_tweets = [item[1] for item in seg_rel_tweets if item[2]==subtw]
            tw_textHash[subtw] = "###".join(tw_tweets)
            tw_dfHash[subtw] = len([item[0] for item in seg_rel_tweets if item[2]==subtw])
        segTextHash[segId] = tw_textHash
        segDFHash[segId] = tw_dfHash
    return segTextHash, segDFHash

def calWordDF():
    wordDFHash = {} #word:(tStr:df)
    content = file("../ni_data/tweet_text.txt").readlines()
    for lineid, line in enumerate(content):
        tw = twHash[lineid]
        arr = line.strip().lower().split(" ")
        for word in arr:
            word_df_hash = {}
            tw_word_df_hash = {}
            if word in wordDFHash:
                word_df_hash = wordDFHash[word]
                if tw in word_df_hash:
                    tw_word_df_hash = word_df_hash[tw]
            tw_word_df_hash[lineid]=1
            word_df_hash[tw]=tw_word_df_hash
            wordDFHash[word] = word_df_hash
    for word in wordDFHash:
        wordDFHash[word] = dict([(item, len(wordDFHash[word][item])) for item in wordDFHash[word]])
    return wordDFHash

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash

# get segments' k nearest neighbor
def getKNN(segPairHash, kNeib):
    kNNHash = {}
    for pair in segPairHash:
        sim = segPairHash[pair]
        segArr = pair.split("|")
        segId1 = int(segArr[0])
        segId2 = int(segArr[1])
        nodeSimHash = {}
        if segId1 in kNNHash:
            nodeSimHash = kNNHash[segId1]
        nodeSimHash[segId2] = sim
        if len(nodeSimHash) > kNeib:
            nodeSimHash = getTopItems(nodeSimHash, kNeib)
        kNNHash[segId1] = nodeSimHash

        nodeSimHash2 = {}
        if segId2 in kNNHash:
            nodeSimHash2 = kNNHash[segId2]
        nodeSimHash2[segId1] = sim
        if len(nodeSimHash2) > kNeib:
            nodeSimHash2 = getTopItems(nodeSimHash2, kNeib)
        kNNHash[segId2] = nodeSimHash2
        
    print "### " + str(time.asctime()) + " " + str(len(kNNHash)) + " event segments' " + str(kNeib) + " neighbors are got."
    return kNNHash

# cluster similar segments into events
def getClusters(kNNHash, segPairHash):
    eventHash = {}
    eventIdx = 0
    nodeInEventHash = {} # segId:eventId # which node(seg) is already been clustered
    for segId1 in kNNHash:
        nodeSimHash = kNNHash[segId1]
#           print "#############################segId1: " + str(segId1)
#           print nodeSimHash
        for segId2 in nodeSimHash:
            if segId2 in nodeInEventHash:
                # s2 existed in one cluster, no clustering again
                continue
#               print "*************segId2: " + str(segId2)
#               print kNNHash[segId2]
            #[GUA] should also make sure segId2 in kNNHash[segId1]
            if segId1 in kNNHash[segId2]:
                # s1 s2 in same cluster
                #[GUA] edgeHash mapping: segId + | + segId -> simScore
                #[GUA] nodeHash mapping: segId -> edgeNum
                #[GUA] nodeInEventHash mapping: segId -> eventId
                eventId = eventIdx
                nodeHash = {}
                edgeHash = {}
                event = None
                if segId1 in nodeInEventHash:
                    eventId = nodeInEventHash[segId1]
                    event = eventHash[eventId]
                    nodeHash = event.nodeHash
                    edgeHash = event.edgeHash
                    nodeHash[segId1] += 1
                else:
                    eventIdx += 1
                    nodeInEventHash[segId1] = eventId
                    event = Event(eventId)
                    nodeHash[segId1] = 1

                nodeHash[segId2] = 1
                if segId1 < segId2:
                    edge = str(segId1) + "|" + str(segId2)
                else:
                    edge = str(segId2) + "|" + str(segId1)
                edgeHash[edge] = segPairHash[edge]
                event.updateEvent(nodeHash, edgeHash)
                eventHash[eventId] = event
                nodeInEventHash[segId2] = eventId

        # seg1's k nearest neighbors have been clustered into other events Or
        # seg1's k nearest neighbors all have long distance from seg1
        if segId1 not in nodeInEventHash:
            eventId = eventIdx
            eventIdx += 1
            nodeHash = {}
            edgeHash = {}
            event = Event(eventId)
            nodeHash[segId1] = 1
            event.updateEvent(nodeHash, edgeHash)
            eventHash[eventId] = event
            nodeInEventHash[segId1] = eventId
    print "### " + str(time.asctime()) + " " + str(len(eventHash)) + " events are got with nodes " + str(len(nodeInEventHash))
    return eventHash

############################
## newsWorthiness
def frmNewWorth(frm):
    frm = frm.strip("|")
    segArr = frm.split("|")
    worthArr = [segNewWorth(seg) for seg in segArr]
    #return sum(worthArr)/len(worthArr)
    return sum(worthArr)

def segNewWorth(segment):
    wordArr = segment.split("_")
    wordNum = len(wordArr)
    if wordNum == 1:
        if segment in wikiProbHash:
            return math.exp(wikiProbHash[segment])
        else:
            return 0.0
    maxProb = 0.0

    for i in range(0, wordNum):
        for j in range(i+1, wordNum+1):
            subArr = wordArr[i:j]
            prob = 0.0
            subS = " ".join(subArr)
            if subS in wikiProbHash:
                prob = math.exp(wikiProbHash[subS]) - 1.0
            if prob > maxProb:
                maxProb = prob
#    if maxProb > 0:
#        print "Newsworthiness of " + segment + " : " + str(maxProb)
    return maxProb


def eventScoring(eventHash, reverseSegHash, segList):
    score_max = 0.0
    score_eventHash = {}
    newWorthScore_nodeHash = {}
    for eventId in sorted(eventHash.keys()):
        event = eventHash[eventId]
        nodeList = event.nodeHash.keys()
        edgeHash = event.edgeHash
        nodeNum = len(nodeList)
 
        # part1
        nodeZScoreArr = [segList[segId][1] for segId in nodeList]
        zscore_nodes = sum(nodeZScoreArr)

        # part2
        nodeStrList = [reverseSegHash[nodeid] for nodeid in nodeList]
        node_NewWorthScoreArr = [frmNewWorth(nodeStr) for nodeStr in nodeStrList]
        newWorthScore_nodes = sum(node_NewWorthScoreArr)

        newWorthScore_nodeHash.update(dict([(nodeStrList[i], node_NewWorthScoreArr[i]) for i in range(nodeNum)]))

        # part3
#        if nodeNum == 1:
#            simScore_edge = 0.00000001
#        else:
        simScore_edge = sum(edgeHash.values())

#        score_event = zscore_nodes/nodeNum
        scoreParts_eventArr = [newWorthScore_nodes, simScore_edge, zscore_nodes]
        score_event = (newWorthScore_nodes/nodeNum) * (simScore_edge/nodeNum)# * (zscore_nodes/nodeNum)

        if score_event <= 0:
            #print "##0-score event", eventId, nodeStrList, scoreParts_eventArr
            continue

        score_eventHash[eventId] = score_event
        if score_event > score_max:
            score_max = score_event

#    zscore_nodeHash = dict([(reverseSegHash[segId], unitScoreHash[segId]) for segId in unitScoreHash])

    score_eventHash = dict([(eventId, score_max/score_eventHash[eventId]) for eventId in score_eventHash])
    score_nodeHash = newWorthScore_nodeHash
    print "###Score of events and nodes are obtained. ", len(score_eventHash), len(score_nodeHash), score_max

    return score_eventHash, score_nodeHash

def writeEvent2File(eventHash, score_eventHash, score_nodeHash, reverseSegHash, tStr, kNeib, taoRatio, elefrmHash):
    outputEvents = []
    eventFile = file("../ni_data/out.Events"+tStr + "_k" + str(kNeib) + "t" + str(taoRatio), "w")
    sortedEventlist = sorted(score_eventHash.items(), key = lambda a:a[1])
    eventNum = 0
    # for statistic
    nodeLenHash = {} 
    eventNumHash = {}

    for eventItem in sortedEventlist:
        eventNum += 1
        eventId = eventItem[0]
        event = eventHash[eventId]

        edgeHash = event.edgeHash
        nodeHash = event.nodeHash
        nodeList = event.nodeHash.keys()

        rankedNodeList_byId = sorted(nodeHash.items(), key = lambda a:a[1], reverse = True)
        nodeList_byId = [item[0] for item in rankedNodeList_byId]

        segList = [reverseSegHash[id] for id in nodeList_byId]

        nodeNewWorthHash = dict([(segId, score_nodeHash[reverseSegHash[segId]]) for segId in nodeList])
        rankedNodeList_byNewWorth = sorted(nodeNewWorthHash.items(), key = lambda a:a[1], reverse = True)
        segList_byNewWorth = [reverseSegHash[item[0]] for item in rankedNodeList_byNewWorth]
        frmList_byNewWorth = [elefrmHash.get(seg) if seg in elefrmHash else seg for seg in segList_byNewWorth]

        # for statistic
        nodes = len(nodeList)
        if nodes in nodeLenHash:
            nodeLenHash[nodes] += 1
        else:
            nodeLenHash[nodes] = 1
        ratioInt = int(eventItem[1])
        if ratioInt <= 10:
            if ratioInt in eventNumHash:
                eventNumHash[ratioInt] += 1
            else:
                eventNumHash[ratioInt] = 1

        if ratioInt >= taoRatio and eventNum > 5:
            continue

        outputEvents.append(frmList_byNewWorth)

        if False:
        #if True:
            print "#################### event " + str(eventId) + " ratio: " + str(eventItem[1]),
            print " " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges."
            print nodeList_byId
            print " ".join(segList)
            print segList_byNewWorth
            print str(edgeHash)
        eventFile.write("****************************************\n###Event " + str(eventNum) + " ratio: " + str(eventItem[1]))
        eventFile.write(" " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
        eventFile.write(str(nodeList_byId) + "\n")
        eventFile.write(" ".join(segList) + "\n")
        eventFile.write(" ".join(segList_byNewWorth) + "\n")
        eventFile.write(" ".join(frmList_byNewWorth) + "\n")
        eventFile.write(str(edgeHash) + "\n")

#    # for statistic
#    print "*************** " + str(len(eventHash)) + " events, taoRatio " + str(taoRatio) + ", k " + str(kNeib)
#    print "Event num < ratio: ",
#    for ratioInt in sorted(eventNumHash.keys()):
#        if ratioInt-1 in eventNumHash:
#            eventNumHash[ratioInt] += eventNumHash[ratioInt-1]
#    print sorted(eventNumHash.items(), key = lambda a:a[0])
#    print "Event contained nodes num distribution: ",
#    print sorted(nodeLenHash.items(), key = lambda a:a[1], reverse = True)

    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events detected are stored into " + eventFile.name
    eventFile.close()
    return outputEvents

############################
## load wikiGram
def loadWiki(filepath):
    wikiProbHash = {}
    content = file(filepath,"r").readlines()
    for lineStr in content:
        lineStr = lineStr.strip()
        prob = float(lineStr[0:lineStr.find(" ")])
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
#        print gram + "\t" + str(prob)
        wikiProbHash[gram] = prob
    print "### " + str(time.asctime()) + " " + str(len(wikiProbHash)) + " wiki grams' prob are loaded."
    return wikiProbHash

def linkelefrm(tStr):
    frmeleAppHash = {} #ele:{frm:1, frm:1}

    content = file(sys.argv[1]).readlines()
    tw_tids = [int(tid) for tid in twHash if twHash[tid]==tStr]
    start_tid, end_tid = min(tw_tids), max(tw_tids)

    for line in content[start_tid:end_tid+1]:
        frmArr = line.strip().split("\t")[1].split(" ")
        for frm in frmArr:
            for ele in frm.split("|"):
                if ele in frmeleAppHash:
                    frmsofele = frmeleAppHash[ele]
                else:
                    frmsofele = []
                frmsofele.append(frm)
                frmeleAppHash[ele] = frmsofele

    for ele in frmeleAppHash:
        frm = Counter(frmeleAppHash[ele]).most_common()[0][0]
        frmeleAppHash[ele] = frm
    return frmeleAppHash

def getgoldevents():
    zparModel = ZPar('english-models')
    #tagger = zparModel.get_tagger()
    depparser = zparModel.get_depparser()
    #stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()

    gevents = file("../ni_data/event_descriptions.tsv").readlines()
    gevents = [line.strip().split("\t")[1].strip("\"") for line in gevents]
    gold_events = []
    for line in gevents:
        parsed_sent = depparser.dep_parse_sentence(line)   
        items = parsed_sent.strip().split("\n")
        items = [item.strip().split("\t") for item in items]
        words = [item[0] for item in items]
        tags = [item[1].lower() for item in items]
        links = [int(item[2]) for item in items]
        deps = [item[3].lower() for item in items]
   
        valid_words = [words[idx] for idx, tag in enumerate(tags) if tag[:2] in ["nn", "vb", "jj", "cd", "rb"] if deps[idx] in ["root", "sub", "obj", "vc", "vmod", "nmod", "pmod"]]
        #stemmed_words = [stemmer.stem(word.lower()) for word in valid_words if word not in ["is", "are", "a", "an", "be", "had", "ha"]]
        stemmed_words = [wordnet_lemmatizer.lemmatize(word.lower()) for word in valid_words if word not in ["is", "are", "a", "an", "be", "had", "ha"]]
        print "-gold", stemmed_words 
        gold_events.append(list(set(stemmed_words)))
    return gold_events

def evalrecall(output_events, gold_events):
    #stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()
    matched_matrix = []
    for oevtid, oevent in enumerate(output_events):
        matched_gold = []
        oevent = " ".join(list(set(oevent)))
        oevent = re.sub("\|", " ", oevent)
        oevent = re.sub("_", " ", oevent)
        owords = list(set(oevent.split(" ")))
        #stem_owords = [stemmer.stem(word) for word in owords]
        stem_owords = [wordnet_lemmatizer.lemmatize(word) for word in owords]
        for gevtid, gwords in enumerate(gold_events):
            commonwords = set(stem_owords)&set(gwords)
            if len(commonwords) <= 1: continue
            print "----", oevtid, gevtid, commonwords
            print "-", oevtid, stem_owords
            print "-", gevtid, gwords
            matched_gold.append(gevtid)
        matched_matrix.append(matched_gold)
    return matched_matrix

def detection(unitHash, windowHash, unitpsHash, wordDFHash, kNeib, taoRatio):
    gold_events = getgoldevents()
    eval_matrix = []
    global TWEETNUM
    for tStr in sorted(windowHash.keys()):
        N_t = windowHash[tStr]
        TWEETNUM = N_t
        print "###########################Processing events in ", tStr, " #tweet", N_t
        segList, unitInvolvedHash = calbursty(unitHash, unitpsHash, tStr, N_t)
        segTextHash, segDFHash = calsegText(segList, unitHash, unitInvolvedHash, tStr)
        segPairHash = calpairsim(tStr, segList, segTextHash, wordDFHash, segDFHash)

        kNNHash = getKNN(segPairHash, kNeib)
        eventHash = getClusters(kNNHash, segPairHash)

        reverseSegHash = dict([(segId, seg[2]) for segId, seg in enumerate(segList)])
        [score_eventHash, score_nodeHash] = eventScoring(eventHash, reverseSegHash, segList)
        elefrmHash = linkelefrm(tStr)
        output_events = writeEvent2File(eventHash, score_eventHash, score_nodeHash, reverseSegHash, tStr, kNeib, taoRatio, elefrmHash)
        t_matched_matrix = evalrecall(output_events, gold_events)
        eval_matrix.append(t_matched_matrix)
        #break
    recall_gold = set([gevtid for dayitem in eval_matrix for evtitem in dayitem for gevtid in evtitem])
    recall = len(recall_gold)*100.0/len(gold_events)
    print "##Recall", "%.4f"%recall, len(recall_gold), len(gold_events)
    print sorted(list(recall_gold))

global UNIT
UNIT = "skl"
#UNIT = "word"

if __name__ == "__main__":
    print "Usage python eventdetection.py datafilepath (default: ../ni_data/frames.txt)"
    print "###program starts at " + str(time.asctime())
    dataFilePath = sys.argv[1]
    [unitHash, windowHash] = statisticDF(dataFilePath, None)
    unitpsHash = calunitps(unitHash, windowHash)

    wordDFHash = calWordDF()
    wikiPath = "../ni_data/anchorProbFile_all"
    global wikiProbHash
    wikiProbHash = loadWiki(wikiPath)

    kNeib = int(sys.argv[2]) if len(sys.argv)>2 else 5
    taoRatio = int(sys.argv[3]) if len(sys.argv)>3 else 2
    detection(unitHash, windowHash, unitpsHash, wordDFHash, kNeib, taoRatio)
    
    print "###program ends at " + str(time.asctime())
