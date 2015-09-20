#! /usr/bin/env python
#coding=utf-8
from pubHeader import *
from lshSim import *

############################
## load frame element embedding (vector)
def getdlVec(filename, unitHash):
    vecHash = {}
    vecfile = file(filename)
    lineIdx = 1
    firstLine = vecfile.readline()[:-1].split(" ")
    wnum = firstLine[0]
    vecLen = firstLine[1]
    while 1:
        lineStr = vecfile.readline()
        if not lineStr:
            print "Loading units' vectors done. [wnum, vecLen] ",firstLine, " vecHash: ", len(vecHash), 
            if unitHash is None:
                print " NoLocalUnits",
            else:
                print " with localUnits: ", len(unitHash),
            print " at ", str(time.asctime())
            break
        if lineIdx == 1: # firstline: [\s]
            lineIdx += 1
            continue
        arr = lineStr[:-1].strip().split(" ")

        wordid = vocabHash.get(arr[0])# digitized key
        if wordid is None:
            #print arr[0], " not in vocabulary."
            continue

        vec = [float(val) for val in arr[1:]]

        if unitHash is None:
            # load global vec
            #vecHash[arr[0]] = vec
            vecHash[wordid] = vec 
        else:
            # load local vec
            if wordid in unitHash:
            #if arr[0] in unitHash:
                vecHash[wordid] = vec # digitized key

        lineIdx += 1
        #if lineIdx % 10000:
            #break
    vecfile.close()
    return vecHash


############################
## whether two unit can be matched. cosine similarity > threshould. unit is represented as distributed vector (word2vec)
def match(unit1, unit2, matchFlag, vecHash):
    global maxSim, minSim
    arr1 = [int(id) for id in unit1.split("|")]
    arr2 = [int(id) for id in unit2.split("|")]

    if matchFlag=="1": # same elements count > 1
        sameArr = [1 for i in range(3) if (arr1[i]==arr2[i]) and (arr1[i]*arr2[i]!=0)]
        if len(sameArr) > 1:
            return True
        return False
    elif matchFlag=="0": # cosine sim
        simArr = [cosineSim(arr1[i], arr2[i]) for i in range(3) if arr1[i]*arr2[i] != 0]
        #print "Sims between [", unit1, "] and [", unit2, "] ", simArr
        simSum = sum(simArr)
        if simSum is None:
            print "None sim between [", unit1, "] and [", unit2, "] ", simArr
            return False
        '''
        if simSum > maxSim:
            maxSim = simSum
        if simSum < minSim:
            minSim = simSum
        '''

        if simSum > matchThreshould:
            return True
        return False
    else:
        print "Choose a match strategy. 0(cosine sim > threshould) or 1(more than 2 same elements)"


def cosineSim(vecHash, item1, item2):
    vec1 = vecHash.get(item1)
    vec2 = vecHash.get(item2)
    if (vec1 is None) or (vec2 is None):
        sim = 0.0
    else:
        sim = 1.0 - dist.cosine(vec1, vec2) # 1-distance
    return sim


def updateDFDayHash(unitHash, unit, tStr, tweetIDstr):
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
    return unitHash
                        
############################
## load event segments from file
def loadBtyFrm(filePath):
    inFile = file(filePath)
    frmList = cPickle.load(inFile)
    inFile.close()
    frmHash = dict([(frmList[i], i) for i in range(len(frmList))])
    print "### " + str(time.asctime()) + " " + str(len(frmHash)) + " event units are loaded from " + inFile.name
    return frmHash

def getItemsFromFile(filename):
    localItems = {}
    sklFile = file(filename)
    while 1:
        lineStr = sklFile.readline()
        if not lineStr:
            print "Local items obtained. ", len(localItems), " at ", time.asctime()
            break
        contentArr = lineStr[:-1].split("\t")
        if len(contentArr) < 2:
            continue
        
        textArr = re.sub("\|", " ", contentArr[1]).split(" ")
        for unit in textArr:
            if len(unit) < 1:
                continue
            if unit not in localItems:
                localItems[unit] = 1
    sklFile.close()
    return localItems

def getPair(id1, id2):
    if str(id1) <= str(id2):
        return str(id1)+"-"+str(id2)
    return str(id2)+"-"+str(id1)

def getFrmPair(id1, id2):
    ids = [str(id1), str(id2)]
    ids.sort()
    return "-".join(ids)


# replace each frame element to one id; digitize all data
def digitizeCorpus(dataFilePath):
    #vocabHash = {"None":0} # frame elements hash in all data
    vocabHash = {} # frame elements hash in all data- filter out none-3-elements frm
    fileList = os.listdir(dataFilePath)
    fileList = sorted(fileList)

    for item in fileList:
        if item.find("relSkl_2013") != 0:
            continue
        sklFile = file(dataFilePath + item)
        tStr = item[-2:]
        digitSklFile = file(dataFilePath+"digitSklText-"+tStr, "w")
        lineIdx = 0
        while 1:
            lineStr = sklFile.readline()
            if not lineStr:
                print "File processing done. ", sklFile.name, " current vocab size: ", len(vocabHash)
                break
            contentArr = lineStr[:-1].split("\t")
            if len(contentArr) < 2:
                continue
            tweetIDstr = contentArr[0]
            tweetText = contentArr[1]

            digitFrms = []
            #print "----", tweetText
            for frm in tweetText.split(" "):
                digitEles = []
                elesInfrm = frm.split("|")
                #print "---", elesInfrm
                if len(elesInfrm) > 3:
                    #print "--- >3 eles: ", elesInfrm, " frm: ", frm
                    # some frms contain more than 3 elements. problem with getRelSkl.py| Some words contain character '|', which is separator between elements in a frm.
                    continue
                for ele in elesInfrm:
                    # op1: replace Empty_element with None
                    '''
                    if len(ele)<1:
                        digitEles.append("0")
                        continue
                    '''
                    # op2: delete frms with Empty_element
                    if len(ele)<1:
                        break

                    eleIdx = elesInfrm.index(ele)
                    if ele not in vocabHash:
                        eleID = len(vocabHash)
                        vocabHash[ele] = eleID
                    else:
                        eleID = vocabHash[ele]
                    digitEles.append(str(eleID))
                digitFrms.append("|".join(digitEles))
                #print elesInfrm, "--------", digitEles
            #print tweetText, "---------", digitFrms
            digitSklFile.write(tweetIDstr + "\t" + " ".join(digitFrms) + "\n")
            lineIdx += 1
            '''
            if lineIdx % 10 == 0:
                break
            '''
        sklFile.close()
        digitSklFile.close()

    if 1: # whether to output vocab. output it once
        vocabFile = file(dataFilePath+"/vocab", "w")
        cPickle.dump(vocabHash, vocabFile)
        print "Digital vocabulary(elements) is stored into ", vocabFile.name, " vocab size: ", len(vocabHash), " at ", time.asctime()
        vocabFile.close()
    return vocabFile.name

def getEleNum(frm):
    eleArr = frm.split("|")
    return len([ele for ele in eleArr if ele != '0'])

def exactfrmDF(dataFilePath):
    unitHash = {}
    fileList = os.listdir(dataFilePath)
    fileList = sorted(fileList)
    frmLenHash = {}
    for item in fileList:
        if item.find("digitSklText-") != 0:
            continue
        sklFile = file(dataFilePath + item)
        print "### Processing " + sklFile.name
        tStr = item[-2:]
        print "Time window: " + tStr

        tweetNum_t = 0
        while 1:
            #[GUA] seggedFile name: * + TimeWindow, format: twitterID, twitterText(segment|segment|...), ...
            lineStr = sklFile.readline()
            if not lineStr:
                break
            contentArr = lineStr[:-1].split("\t")
            if len(contentArr) < 2:
                continue
            tweetIDstr = contentArr[0]
            tweetText = contentArr[1]
            tweetNum_t += 1

            textArr = tweetText.split(" ")
            for segment in textArr:
                if len(segment) < 1:
                    continue
                unit = segment

                # statistic num of eles
                '''
                num = getEleNum(unit)
                if num in frmLenHash:
                    frmLenHash[num] += 1
                else:
                    frmLenHash[num] = 1
                if num > 3:
                    print "Illegal frm: ", unit, " ", num
                '''
                # statistic segment ps
                # exact match pattern
                unitHash = updateDFDayHash(unitHash, unit, tStr, tweetIDstr)

            if tweetNum_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed! units: " + str(len(unitHash))
                #break # debug
        sklFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded. unitNum: " + str(len(unitHash))
        #break # debug
    print "### In total corpus " + str(len(unitHash)) + " " + UNIT + "s are loaded! at ", time.asctime()
    #eleNumArr = [frmLenHash[i]*1.0/sum(frmLenHash.values()) for i in sorted(frmLenHash.keys())]
    #print "EleNum in Frms: ", eleNumArr

    newUnitHash = dict([(item, unitHash[item]) for item in unitHash if statDF(unitHash[item]) > 4])
    frmList = newUnitHash.keys()
    print "After filtering (df>=5) #unit: ", len(frmList), " at ", time.asctime()

    '''
    windowHash = dict([(str(t).zfill(2), {}) for t in range(1, 16)])
    for frm in newUnitHash:
        dfHash = newUnitHash[frm]
        for t in dfHash:
            windowHash[t].update(dfHash[t])
    windowHash = dict([(t, len(windowHash[t])) for t in windowHash])
    print "Valid tweets, ",  windowHash
    exactFile = file(dataFilePath+"frmExactDF", "w")
    cPickle.dump(windowHash, exactFile)
    cPickle.dump(newUnitHash, exactFile)
    print "Exact match unit hash is stored into ", exactFile.name, " at ", time.asctime()
    exactFile.close()
    '''
    return frmList

def statDF(itemHash):
    dfArr = [len(itemHash[day]) for day in itemHash]
    return sum(dfArr)
        
def calcosSims(itemHash, vecHash):
    print "begin calculating len of items. #item: ", len(itemHash), " at ", time.asctime()
    for item in itemHash:
        vec = vecHash.get(int(item))
        if vec is None:
            itemHash[item] = None
            continue
        vec2 = [val*val for val in vec]
        length = math.sqrt(sum(vec2))
        itemHash[item] = length
    print "begin calculating sim of pairs. #item: ", len(itemHash), " at ", time.asctime()
    itemList = itemHash.keys()
    itemList.sort()
    simHash = {}
    for i in range(len(itemList)):
        item1 = itemList[i]
        for j in range(i+1, len(itemList)):
            item2 = itemList[j]
            #continue

            vec1 = vecHash.get(int(item1))
            vec2 = vecHash.get(int(item2))
            if (vec1 is None) or (vec2 is None):
                sim = 0.0
            else:
                dotmul = [vec1[id]*vec2[id] for id in range(len(vec1))]
                sim = sum(dotmul)/(itemHash[item1]*itemHash[item2])
            pairId = getPair(item1, item2)
            simHash[pairId] = sim

        if i < 100 and i%10==0:
            print "i ", i, " items are processed at ", time.asctime()
        elif i <= 1000 and i % 100 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        elif i > 1000 and i % 10000 == 0:
            print "i ", i, " items are processed at ", time.asctime()
    return simHash


def mergeFrms(frmSimHash):
    frmCluster = {} # frm:clsID
    clusters = {} # clsID: frms
    newClsID = 0

    i = 0
    for frmpair in frmSimHash:
        frm1 = frmpair[:frmpair.find("-")]
        frm2 = frmpair[frmpair.find("-")+1:]
        i += 1

        clsId1 = frmCluster.get(frm1)
        clsId2 = frmCluster.get(frm2)

        if (clsId1 is None) and (clsId2 is None):
            frmCluster[frm1] = newClsID
            frmCluster[frm2] = newClsID
            clusters[newClsID] = [frm1, frm2]
            #print "New: ", newClsID, " ", clusters[newClsID]
            newClsID += 1
        elif (clsId1 is not None) and (clsId2 is None):
            # test whether similarity has transitivity
            for frm in clusters[clsId1]:
                pair = getFrmPair(frm, frm2)
                sim = frmSimHash.get(pair)
                if sim is not None and sim < 0.6:
                    print [frm1, frm2], " ", frmSimHash[frmpair]
                    print "Wrong assumption: ", pair, " ", sim
            #print "append frm2 to ", clsId1, " ", clusters[clsId1]
            frmCluster[frm2] = clsId1
            clusters[clsId1].append(frm2)
        elif (clsId1 is None) and (clsId2 is not None):
            #print "append frm1 to ", clsId2, " ", clusters[clsId2]
            frmCluster[frm1] = clsId2
            clusters[clsId2].append(frm1)
        elif (clsId1 is not None) and (clsId2 is not None):
            #print "merge two set ", [clsId1, clsId2], " to ", clsId1, " ", clusters[clsId1]
            if clsId1 == clsId2:
                continue
            else:
                clusters[clsId1].extend(clusters[clsId2])
                for frm in clusters[clsId2]:
                    frmCluster[frm] = clsId1
                del clusters[clsId2]

        #print "******* ", i
        if i % 10000 == 0:
            print i, " items has been processed at ", time.asctime(), " #cls: ", len(clusters)
    print "Merging done #frm: ", len(frmCluster) , " #clusters: ", len(clusters), " at ", time.asctime()
    sizeCls = dict([(i, len(clusters[i])) for i in clusters])
    if len(sizeCls) > 20:
        print "clusters: ", sorted(sizeCls.items(), key = lambda a:a[0])[:20]
        print "|cluster|: ", sorted(sizeCls.items(), key = lambda a:a[1], reverse = True)[:20]
    else:
        print sorted(sizeCls.items(), key = lambda a:a[1], reverse = True)
    return frmCluster, clusters

def mergeFrms2(frmList, vecHash): # would be very slow
    frmCluster = {} # frm:clsID
    clusters = {} # clsID: frms
    newClsID = 0
    frmCluster[frmList[0]] = newClsID
    clusters[newClsID] = [frmList[0]]
    newClsID += 1
    for i in range(len(frmList)):
        frm1 = frmList[i]
        for j in range(i+1, len(frmList)):
            frm2 = frmList[j]

            clsId1 = frmCluster.get(frm1)
            clsId2 = frmCluster.get(frm2)

            if match(frm1, frm2, "1", vecHash): # 0: cosine; 2: same ele count
                if clsId1 is None:
                    print frm1, " not found in frmClusters."
                    continue
                if clsId2 is None:
                    frmCluster[frm2] = clsId1
                    clusters[clsId1] = clusters[clsId1].append(frm2)
                elif clsId2 is not None:
                    clusters[clsId1].extend(clusters[clsId2])
                    for frm in clusters[clsId2]:
                        frmCluster[frm] = clsId1
                    del clusters[clsId2]
            else:
                if clsId1 is None:
                    print frm1, " not found in frmClusters."
                    continue
                if clsId2 is None:
                    frmCluster[frm2] = newClsID
                    clusters[newClsID] = [frm2]
                    newClsID += 1
        #if i % 100 == 0:
        print i, " items has been processed at ", time.asctime(), " #cls: ", len(clusters)
    print "Merging done ", len(frmList), " items. at ", time.asctime()
    print "#clusters ", len(clusters)
    sizeCls = dict([(i, len(clusters[i])) for i in clusters])
    if len(sizeCls) > 20:
        print sorted(sizeCls.items(), key = lambda a:a[0])[20]
        print sorted(sizeCls.items(), key = lambda a:a[1], reverse = True)[20]
    else:
        print sorted(sizeCls.items(), key = lambda a:a[1], reverse = True)
    return clusters                 


def separateVocab(frmList):
    roleHash = {0:{}, 1:{}, 2:{}}
    for frm in frmList:
        arr = frm.split("|")
        arr = [int(item) for item in arr]
        for idx in range(3):
            if arr[idx] not in roleHash[idx]:
                roleHash[idx][arr[idx]] = 1
    vocabPartFile = file(dataFilePath+"/vocab-part", "w")
    for idx in range(3):
        cPickle.dump(roleHash[idx], vocabPartFile)
    print "separate vocabulary is stored into ", vocabPartFile.name, " at ", time.asctime()
    print "#num of separate vocabs: ", [len(roleHash[idx]) for idx in range(3)]
    vocabPartFile.close()

def getPSval(df_hash, windowHash):
    df_hash = dict([(t, len(df_hash[t])*1.0/windowHash[t]) for t in df_hash if len(df_hash[t])>0])
    prob = sum(df_hash.values())/len(df_hash)
    return prob

def loadEleVocab(dataFilePath):
    global vocabHash
    vocabFile = file(dataFilePath+"vocab")
    vocabHash = cPickle.load(vocabFile)
    vocabFile.close()
    print "Global Vocab loading done. ", len(vocabHash), " at ", time.asctime()

def loadSepVocab(dataFilePath):
    vocabPartFile = file(dataFilePath+"/vocab-part")
    arg1Hash = cPickle.load(vocabPartFile)
    verbHash = cPickle.load(vocabPartFile)
    arg2Hash = cPickle.load(vocabPartFile)
    vocabPartFile.close()
    print "Separate Vocab loading done. ", [len(arg1Hash), len(verbHash), len(arg2Hash)], " at ", time.asctime()
    return arg1Hash, verbHash, arg2Hash


def calEleSigs(vecFilename, arg1Hash, verbHash, arg2Hash, d, dim):
    # calculate signatures of vectors
    vecHash1 = getdlVec(vecFilename, arg1Hash)
    rvecHash1 = calSig(arg1Hash, vecHash1, d, dim)
    print "rvec calculating done. ", len(rvecHash1), " at ", time.asctime()
    vecHash2 = getdlVec(vecFilename, verbHash)
    rvecHash2 = calSig(verbHash, vecHash2, d, dim)
    print "rvec calculating done. ", len(rvecHash1), " at ", time.asctime()
    vecHash3 = getdlVec(vecFilename, arg2Hash)
    rvecHash3 = calSig(arg2Hash, vecHash3, d, dim)
    print "rvec calculating done. ", len(rvecHash1), " at ", time.asctime()

    rvecFile = file(dataFilePath+"/rvec", "w")
    cPickle.dump(rvecHash1, rvecFile)
    cPickle.dump(rvecHash2, rvecFile)
    cPickle.dump(rvecHash3, rvecFile)
    rvecFile.close()
    print "rvec calculating done. ", [len(rvecHash1), len(rvecHash2), len(rvecHash3)], " at ", time.asctime(), " to ", rvecFile.name

def calEleSims(dataFilePath):
    #loadEleVocab(dataFilePath)

    # separate vocab into arg1Hash, verbHash, arg2Hash. Calculate their similarity separately
    #[arg1Hash, verbHash, arg2Hash] = loadSepVocab(dataFilePath)

    dim = 200
    d = 100
    #calEleSigs(vecFilename, arg1Hash, verbHash, arg2Hash, d, dim)

    # calculate similarities of vectors given their signatures vectors
    rvecFile = file(dataFilePath+"/rvec")
    rvecHash1 = cPickle.load(rvecFile)
    rvecHash2 = cPickle.load(rvecFile)
    rvecHash3 = cPickle.load(rvecFile)
    rvecFile.close()
    print "rvec loading done. ", [len(rvecHash1), len(rvecHash2), len(rvecHash3)], " at ", time.asctime(), " from ", rvecFile.name

    q = 20
    B = 50
    hamThreshold = dim*0.3
    if sys.argv[2] == '1':
        lshsimHash1 = callshfastSim(rvecHash1, d, q, B, hamThreshold)
        #lshsimHash1 = callshSim(rvecHash1, d)
        print "lshsimHash1 calculating done at ", time.asctime()
        simVocabFile = file(dataFilePath+"/simVocab1", "w")
        cPickle.dump(lshsimHash1, simVocabFile)
        simVocabFile.close()
    elif sys.argv[2] == '2':
        lshsimHash2 = callshfastSim(rvecHash2, d, q, B, hamThreshold)
        #lshsimHash2 = callshSim(rvecHash2, d)
        print "lshsimHash2 calculating done at ", time.asctime()
        simVocabFile = file(dataFilePath+"/simVocab2", "w")
        cPickle.dump(lshsimHash2, simVocabFile)
        simVocabFile.close()
    elif sys.argv[2] == '3':
        lshsimHash3 = callshfastSim(rvecHash3, d, q, B, hamThreshold)
        #lshsimHash3 = callshSim(rvecHash3, d)
        print "lshsimHash3 calculating done at ", time.asctime()
        simVocabFile = file(dataFilePath+"/simVocab3", "w")
        cPickle.dump(lshsimHash3, simVocabFile)
        simVocabFile.close()

# verify effectiveness of lsh similarity
def lshSimTuning(itemList, vecFilename):
    # determin d
    itemHash = dict([(itemList[i], 1) for i in range(1000)])
    vecHash = getdlVec(vecFilename, itemHash)
    cossimHash1 = calcosSims(itemHash)
    dim = 200
    dvalArr = [20, 50, 100, 150, 200, 300, 400, 500, 1000] # d = 100
    for d in dvalArr:
        print "*********Value d: ", d, 
        rvecHash = calSig(itemHash, vecHash, d, dim)
        lshsimHash1 = callshSim(rvecHash, d)
        diffs = [abs(lshsimHash1[pair]-cossimHash1[pair]) for pair in lshsimHash1 if pair in cossimHash1]
        if len(diffs) > 0:
            print len(diffs), " ", max(diffs), " ", min(diffs), " ", sum(diffs)/len(diffs)

    qArr = [5, 10, 20, 50, 100, 300, 500, 1000]
    BArr = [50, 100, 200, 300, 500]
    hamArr = [i/10.0 for i in range(1, 11)]
    q_init = 20
    B = 50
    hamThreshold = dim*0.3
    rvecHash = calSig(itemHash, vecHash, d, dim)
    lshsimHash_gold = callshfastSim(rvecHash, d, 1, 1000, dim)
    lshsimHash_gold = dict([(item, lshsimHash_gold[item]) for item in lshsimHash_gold if lshsimHash_gold[item]>0.15])
    #for B in BArr: # determin B with q_init
        #print "*********Value B: ", B, " with q_init: ", q_init,
    #for hamThreshold in hamArr: # determin ham with B_determined, q_init
        #print "*********Value fixed B: ", B, " with q_init: ", q_init, " hamThre: ", hamThreshold,
        #q = q_init
    for q in qArr: # determin ham with B_determined, ham_determined 
        print "*********Value fixed B: ", B, " with q: ", q, " fixed hamThre: ", hamThreshold,
        lshsimHash1 = callshfastSim(rvecHash, d, q, B, hamThreshold*dim)
        print " lengthOfsims: ", len(lshsimHash1), " ", len(cossimHash1)
        recall = [item for item in lshsimHash_gold if item in lshsimHash1]
        print "recall: ", len(recall)*100/len(lshsimHash_gold)
        diffs = [abs(lshsimHash1[pair]-cossimHash1[pair]) for pair in lshsimHash1 if pair in cossimHash1]
        if len(diffs) > 0:
            print len(diffs), " ", max(diffs), " ", min(diffs), " ", sum(diffs)/len(diffs), " ", 
            diffs = [val*val for val in diffs]
            print math.sqrt(sum(diffs))/len(diffs)


def getOrderedFrms(dataFilePath):
    frmList = exactfrmDF(dataFilePath)
    # load needs 13mins; dump needs 20 mins

    frmList.sort()
    print "Frames are sorted. at ", time.asctime()
    frmsFile = file(dataFilePath + "/frmList", "w")
    cPickle.dump(frmList, frmsFile)
    frmsFile.close()
    print "Frmlist is dumped into ", frmsFile.name, " at ", time.asctime()

# sim(frm1, frm2) = sum(sim_i(frmele1i, frmele2i))
# slow - may need 100hour with 10 process running on 2 server. Each process needs 20G mem
def calculateFrmSims(dataFilePath, simThreshould):
    #getOrderedFrms(dataFilePath)

    frmsFile = file(dataFilePath + "/frmList")
    frmList = cPickle.load(frmsFile)
    frmsFile.close()
    print "Frmlist is loaded from ", frmsFile.name, " at ", time.asctime()

    splitfrmList = [item.split("|") for item in frmList]
    print "Frames are splited. at ", time.asctime()

    #'''
    # load elements' sim
    vocabSimHash = {}
    for i in range(1, 4):
        simVocabFile = file(dataFilePath+"/simVocab"+str(i))
        lshsimHash = cPickle.load(simVocabFile)
        simVocabFile.close()
        vocabSimHash[i-1] = lshsimHash
        print "part Sims loading done. #pairNum: ", len(lshsimHash), " at ", time.asctime()
    pairNum = [len(vocabSimHash[i]) for i in range(len(vocabSimHash))]
    print "Sims loading done. ", pairNum, " at ", time.asctime()
    #'''

    #length = 100000
    length = len(frmList)
    begin = int(sys.argv[2])
    end = int(sys.argv[3])
    if end > length:
        end = length
    simFrmFile = file(dataFilePath+"/simFrm."+str(begin)+"-"+str(end), "w")
    print "Begin calculating sim of frm pairs. #frm:", [begin, end]," at ", time.asctime()
    frmPairNum = 0
    for i in range(begin, end):
        arr1 = splitfrmList[i]
        for j in range(i+1, length):
            arr2 = splitfrmList[j]
            simArr = []
            for eleIds in range(3):
                if arr1[eleIds]=='0' or arr2[eleIds] == '0':
                    simArr.append(None)
                else:
                    simArr.append(vocabSimHash[eleIds].get(getPair(arr1[eleIds], arr2[eleIds])))
            frmPair = getFrmPair(frmList[i], frmList[j])
            frmPairNum += 1
            simArr = [item for item in simArr if item is not None]
            if len(simArr) > 0:
                sim = sum(simArr)
                #'''
                if sim >= simThreshould:
                    frmSimStr = str(i)+"-"+str(j)+"\t"+frmPair + "\t" + str(sim)
                    simFrmFile.write(frmSimStr + "\n")
                #'''
        if i % 10 == 0:
            print "Frm ", i, " has been processed. at ", time.asctime(), " frmpair: ", frmPairNum
    print "SimFrmpair: ", frmPairNum, " has been written to ", simFrmFile.name, " at ", time.asctime()
    simFrmFile.close()

def getEleVec(dataFilePath):
    eleVocabs = dict([(int(frm.split("|")[j]), 1) for frm in frmList for j in range(3)])
    print "Element Vocab calculating done. ", len(eleVocabs), " at ", time.asctime()

    loadEleVocab(dataFilePath)

    # merge three element's vector to one as frame's vector
    eleVecHash = getdlVec(vecFilename, eleVocabs)
    print "EleVec calculating done. ", len(eleVecHash), " at ", time.asctime()

    vecFile = file(dataFilePath+"/eleVec", "w")
    cPickle.dump(eleVecHash, vecFile)
    vecFile.close()
    print "Ele vec dumping done. ", len(eleVecHash), " at ", time.asctime(), " to ", vecFile.name

def getFrmVec(dataFilePath, frmList, dim, flag):
    vecFile = file(dataFilePath+"/eleVec")
    eleVecHash = cPickle.load(vecFile)
    vecFile.close()
    print "Ele vec loading done. ", len(eleVecHash), " at ", time.asctime(), " from ", vecFile.name

    frmVecHash = {}
    for frm in frmList:
        eleArr = [int(frm.split("|")[j]) for j in range(3)]
        frmVec = [0]*dim
        for i in range(3):
            ele = eleArr[i]
            eleVec = eleVecHash.get(ele)
            if eleVec is None:
                eleVec = [0]*dim
            # op1 200*3-> 600 dimension
            #frmVec.extend(eleVec)
            # op2 operationg(200) -> 200 dimension
            # op2-sum
            #frmVec = [(frmVec[idx]+eleVec[idx]) for idx in range(len(eleVec))]
            # op2-max
            #frmVec = [max(frmVec[idx], eleVec[idx]) for idx in range(len(eleVec))]
            # op2-min
            frmVec = [min(frmVec[idx], eleVec[idx]) for idx in range(len(eleVec))]
        # op2-avg
        #frmVec = [item/3.0 for item in frmVec]
        frmVecHash[frm] = frmVec
    print "FrmVec calculating done. ", len(frmVecHash), " at ", time.asctime()

    frmVecFile = file(dataFilePath+"/frmVec"+flag, "w")
    cPickle.dump(frmVecHash, frmVecFile)
    frmVecFile.close()
    print " frame vec dumping done. ", len(frmVecHash), " at ", time.asctime(), " to ", frmVecFile.name

def calFrmSig1(dataFilePath, frmList, d, dim, flag): # not finished... to be continue if used
    # calculate signatures of ele vectors method 1
    #getEleVec(dataFilePath)
    getFrmVec(dataFilePath, frmList, dim, flag)
    #sys.exit()

    frmVecFile = file(dataFilePath+"/frmVec"+flag)
    frmVecHash = cPickle.load(frmVecFile)
    frmVecFile.close()
    print " frame vec loading done. ", len(frmVecHash), " at ", time.asctime(), " to ", frmVecFile.name

    frmrVecHash = calSig(frmList, frmVecHash, d, dim)
    print "Frm rvec calculating done. ", len(frmrVecHash), " at ", time.asctime()

    frmrVecFile = file(dataFilePath+"/frmrVec"+flag, "w")
    cPickle.dump(frmrVecHash, frmrVecFile)
    frmrVecFile.close()
    print "frame rvec dumping done. ", len(frmrVecHash), " at ", time.asctime(), " to ", frmrVecFile.name


def calFrmSig(dataFilePath, frmList, flag):
    # calculate signatures of ele vectors method 2

    '''
    eleVocabs = dict([(i, 1) for i in eleVecHash])
    elerVecHash = calSig(eleVocabs, eleVecHash, d, dim)
    print "Ele rvec calculating done. ", len(elerVecHash), " at ", time.asctime()
    eleVecHash.clear()
    '''

    elerVecHash = {}
    rvecFile = file(dataFilePath+"/rvec")
    elerVecHash[0] = cPickle.load(rvecFile)
    elerVecHash[1] = cPickle.load(rvecFile)
    elerVecHash[2] = cPickle.load(rvecFile)
    rvecFile.close()
    print "ele rvec loading done. ", [len(elerVecHash[i]) for i in range(3)], " at ", time.asctime(), " from ", rvecFile.name

    frmrVecHash = {}
    for frm in frmList:
        eleArr = [int(frm.split("|")[j]) for j in range(3)]
        frmVec = []
        for i in range(3):
            ele = eleArr[i]
            eleVec = elerVecHash[i].get(ele)
            if eleVec is None:
                eleVec = [0]*dim
            else:
                eleVec = tobits(eleVec)
            frmVec.extend(eleVec)
        frmrVecHash[frm] = frmVec
    print "FrmrVec calculating done. ", len(frmrVecHash), " at ", time.asctime()

    rvecFile = file(dataFilePath+"/frmrVec"+flag, "w")
    cPickle.dump(frmrVecHash, rvecFile)
    rvecFile.close()
    print " frame rvec dumping done. ", len(frmrVecHash), " at ", time.asctime(), " to ", rvecFile.name

def loadFrmlist(dataFilePath):
    frmsFile = file(dataFilePath + "/frmList")
    frmList = cPickle.load(frmsFile)
    frmsFile.close()
    print "Frmlist is loaded from ", frmsFile.name, " at ", time.asctime()
    return frmList

###############
# calculate sim(frm1, frm2) with lsh sim algorithm.
#op1: rvec(frm) = [].append(rvec(eles))
#op2: vec(frm) = [].append(vec(eles))
# op1 should be similar to op2
def calculateFrmSims_lsh(dataFilePath, simThreshould, flag):
    frmList = loadFrmlist(dataFilePath)

    dim = 200
    d = 100
    #calFrmSig(dataFilePath, frmList, flag)
    calFrmSig1(dataFilePath, frmList, d, dim, flag)
    #sys.exit()

    ''
    # calculate similarities of vectors given their signatures vectors
    rvecFile = file(dataFilePath+"/frmrVec"+flag)
    rvecHash = cPickle.load(rvecFile)
    rvecFile.close()
    print " frame rvec loading done. ", len(rvecHash), " at ", time.asctime(), " from ", rvecFile.name
    #rvecHash = dict([(item, rvecHash[item]) for item in rvecHash.keys()[:1000]])

    #dim = dim*3 # for calfrmsig method 2 with 600 dimension
    q = 20
    B = 50
    hamThreshold = 60 # determined by dim*0.? 
    # when dim=200 hamThreshould = 0.3
    # when dim=600 hamThreshould = 0.3 makes low efficiency

    lshsimHash = callshfastSim(rvecHash, d, q, B, hamThreshold)
    #lshsimHash = callshSim(rvecHash, d)
    print "lshsimHash calculating done at ", time.asctime(), " #pair: ", len(lshsimHash)
    lshsimHash = dict([(item, lshsimHash[item]) for item in lshsimHash if lshsimHash[item] >= simThreshould])
    print "lshsimHash(filtered) is calculating done at ", time.asctime(), " #pair: ", len(lshsimHash), " simThreshould: ", simThreshould
    simVocabFile = file(dataFilePath+"/frmSimVocab"+flag, "w")
    cPickle.dump(lshsimHash, simVocabFile)
    simVocabFile.close()
    print "lshsimHash dumping done at ", time.asctime()
    #'''

    '''
    ## filtering again with simThreshould
    simVocabFile = file(dataFilePath+"/frmSimVocab")
    lshsimHash = cPickle.load(simVocabFile)
    simVocabFile.close()
    print "lshsimHash loading done at ", time.asctime(), " #pair: ", len(lshsimHash)
    lshsimHash = dict([(item, lshsimHash[item]) for item in lshsimHash if lshsimHash[item] >= simThreshould])
    print "lshsimHash(filtered) is calculating done at ", time.asctime(), " #pair: ", len(lshsimHash), " simThreshould: ", simThreshould
    simVocabFile = file(dataFilePath+"/frmSimVocab", "w")
    cPickle.dump(lshsimHash, simVocabFile)
    simVocabFile.close()
    print "lshsimHash dumping done at ", time.asctime()
    '''


def loadfrmSim(dataFilePath, flag):
    simVocabFile = file(dataFilePath+"/frmSimVocab"+flag)
    lshsimHash = cPickle.load(simVocabFile)
    simVocabFile.close()
    print "lshfrmsimHash loading done at ", time.asctime()
    return lshsimHash

def loadFrmCls(dataFilePath, flag):
    frmClsFile = file(dataFilePath+"frmCluster"+flag)
    frmCluster = cPickle.load(frmClsFile)
    clusters = cPickle.load(frmClsFile)
    frmClsFile.close()
    print "Frmclusters are loaded from ", frmClsFile.name, " at ", time.asctime()
    return frmCluster, clusters

def calculatePS(dataFilePath, flag):
    frmList = loadFrmlist(dataFilePath)

    '''
    # calculate similar frames
    frmSimHash = loadfrmSim(dataFilePath)# load frmsims first
    print "Merging begins #item: ", len(frmList), " with #simpair: ", len(frmSimHash), " at ", time.asctime()
    [frmCluster, clusters] = mergeFrms(frmSimHash)
    frmClsFile = file(dataFilePath+"frmCluster"+flag, "w")
    cPickle.dump(frmCluster, frmClsFile)
    cPickle.dump(clusters, frmClsFile)
    frmClsFile.close()
    print "Frmclusters are dumpted into ", frmClsFile.name, " at ", time.asctime()
    '''

    [frmCluster, clusters] = loadFrmCls(dataFilePath, flag)

    #frmList = exactfrmDF(dataFilePath) # run once
    exactFile = file(dataFilePath+"frmExactDF")
    windowHash = cPickle.load(exactFile)
    frmDFHash = cPickle.load(exactFile)
    print "Exact match unit hash is loaded from ", exactFile.name, " at ", time.asctime()
    exactFile.close()
    
    psFile = file(dataFilePath + UNIT + "_ps"+flag, "w")

    for clusID in clusters:
        frms = clusters[clusID]
        dfHash = dict([(str(t).zfill(2), {}) for t in range(1, 16)])
        for frm in frms:
            tempArr = [dfHash[t].update(frmDFHash[frm][t]) for t in frmDFHash[frm]]
        psProb = getPSval(dfHash, windowHash)
        for frm in frms:
            psFile.write(str(psProb) + "\t" + frm + "\n")

    for frm in frmList:
        if frm in frmCluster:
            continue
        dfHash = frmDFHash[frm]
        psProb = getPSval(dfHash, windowHash)
        psFile.write(str(psProb) + "\t" + frm + "\n")
    psFile.close()
    print len(frmList), " frm's ps has been calculated. at ", time.asctime()

    print "### frms' ps values are written to " + psFile.name

##################################
# main
if __name__ == "__main__":
    print "###program starts at " + str(time.asctime())
    global vocabHash
    global matchThreshould
    global UNIT
    global flag
    dataFilePath = r"../parsedTweet/"
    matchThreshould = 2.0

    unitHash = {} #unit:df_hash
    #df_hash --> timeSliceIdStr:df_t_hash
    #df_t_hash --> tweetIDStr:1

    argsArr = sys.argv
    if "-dir" in argsArr:
        dataFilePath = argsArr[argsArr.index("-dir")+1]
    else:
        print "Usage estimatePs.py -dir datafilepath (default: ../parsedTweet/) [-flag flag] [-match matchThreshould (default 2.0)]"
        sys.exit()
    if "-flag" in sys.argv:
        flag = argsArr[argsArr.index("-flag")+1]
    if "-match" in sys.argv:
        matchThreshould = argsArr[argsArr.index("-match")+1]
        matchThreshould = float(matchThreshould)

    UNIT = "skl"
    vecFilename = dataFilePath+"w2vText.tvec"

    # digitize all frame elements in corpus. frame is eleid1_eleid2_eleid3 (eleid = 0, if frame element is empty)
    vocabFilename = digitizeCorpus(dataFilePath)
    sys.exit()

    #separate vocab 
    frmList = exactfrmDF(dataFilePath)
    frmLenHash = {}
    for frm in frmList:
        num = getEleNum(frm)
        if num in frmLenHash:
            frmLenHash[num] += 1
        else:
            frmLenHash[num] = 1
    eleNumArr = [frmLenHash[i]*1.0/sum(frmLenHash.values()) for i in sorted(frmLenHash.keys())]
    print "EleNum in Frms: ", frmLenHash
    print eleNumArr
    sys.exit()
    #separateVocab(frmList)


    # parameters tuning
    #itemList = verbHash.keys()
    #lshSimTuning(itemList, vecFilename)

    simThreshould = 0.9 # determined
    #calEleSims(dataFilePath)
    #calculateFrmSims(dataFilePath, simThreshould) # method1 not tested
    #calculateFrmSims_lsh(dataFilePath, simThreshould, flag) # method 2

    calculatePS(dataFilePath, flag)

    print "###program ends at " + str(time.asctime())
