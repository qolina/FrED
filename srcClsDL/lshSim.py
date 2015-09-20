
import os
import time
import random
import math
import numpy

def getPair(id1, id2):
    ids = [str(id1), str(id2)]
    ids.sort()
    return "-".join(ids)

def calLens(itemHash):
    #print "begin calculating len of items. #item: ", len(itemHash), " at ", time.asctime()
    for item in itemHash:
        vec = vecHash.get(int(item))
        if vec is None:
            itemHash[item] = None
            continue
        vec2 = [val*val for val in vec]
        length = math.sqrt(sum(vec2))
        itemHash[item] = length
    return itemHash

def tobits(num):
    binarr = list(bin(num)[2:])
    binarr = [int(it) for it in binarr]
    return binarr

def tonum(arr):
    arr = [str(it) for it in arr]
    return int("".join(arr), 2)

def callshfastSim(itemHash, d, q, B, hamThreshold):
    simHash = {}
    print "begin calculating sim of pairs. #item: ", len(itemHash), " at ", time.asctime()
    itemList = itemHash.keys()
    itemList.sort()
    rvecs = list([tobits(itemHash[id]) for id in itemList])
    #rvecs = list([itemHash[id] for id in itemList])

    zippedRvecs = zip(*rvecs)
    for qidx in range(q):
        print "Random permutation begin round: ", qidx, " at ", time.asctime()
        #'''
        random.shuffle(zippedRvecs)
        newrvecs = zip(*zippedRvecs)
        print "shuffle done. at ", time.asctime()
        newItemHash = dict([(itemList[idx], tonum(newrvecs[idx])) for idx in range(len(itemHash))])
        #'''
        # (ax+b)mod P
        #a = random.uniform(1, P-1)
        #b = random.randint(0, P-1)
        #newItemHash = dict([(id, (a*itemHash[id]+b)%P) for id in itemHash])
        sortedVecList = sorted(newItemHash.items(), key = lambda a:a[1])
        print "sorting shuffled digit vecs done. at ", time.asctime()
        for sidx in range(len(sortedVecList)):
            sitem = sortedVecList[sidx]
            id1 = sitem[0]
            rvec1 = sitem[1]
            idxRange = range(sidx-B/2, sidx+B/2 +1)
            for idx2 in idxRange:
                if idx2<0 or idx2>=len(sortedVecList):
                    break
                if idx2==sidx:
                    continue
                sitem2 = sortedVecList[idx2]
                id2 = sitem2[0]
                rvec2 = sitem2[1]

                xor = rvec1^rvec2
                if nnz(xor) < hamThreshold:
                    sim = (d-nnz(xor))/float(d)
                    sim = math.cos((1-sim)*math.pi)
                    pairId = getPair(id1, id2)
                    if pairId not in simHash:
                        simHash[pairId] = sim

            if sidx % 10000 == 0:
                print sidx, " items are processed at ", time.asctime()
        print "Random permutation ends. #itempair: ", len(simHash), " at ", time.asctime()

    print "End calculating sim of pairs. #item pairs: ", len(simHash), " at ", time.asctime()
    return simHash

def callshSim(itemHash, d):
    simHash = {}
    #print "begin calculating sim of pairs. #item: ", len(itemHash), " at ", time.asctime()
    itemList = itemHash.keys()
    itemList.sort()
    for i in range(len(itemList)):
        item1 = itemList[i]
        rvec1 = itemHash.get(item1)
        #print rvec1, " ----- " 
        for j in range(i+1, len(itemList)):
            item2 = itemList[j]
            #continue

            #'''
            rvec2 = itemHash.get(item2)
            #print rvec2
            xor = rvec1^rvec2
            sim = (d-nnz(xor))/float(d)
            sim = math.cos((1-sim)*math.pi)
            #'''

            #sim = 0.0
            pairId = getPair(item1, item2)
            simHash[pairId] = sim

        '''
        if i < 1000:
            print "i ", i, " items are processed at ", time.asctime()
        elif i <= 1000 and i % 10 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        elif i > 1000 and i % 10000 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        if i % 10000 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        '''
    return simHash

# get number of '1's in binary
# running time: O(# of '1's)
def nnz(num):
    if num == 0:
        return 0
    res = 1
    num = num & (num-1)
    while num:
        res += 1
        num = num & (num-1)
    return res


# LSH signature generation using random projection
def get_signature(user_vector, rand_proj): 
    res = 0
    for p in (rand_proj):
        res = res << 1
        val = numpy.dot(p, user_vector)
        if val >= 0:
            res |= 1
    return res

def calSig(itemHash, vecHash, d, dim):

    print "begin calculating signatures of pairs. #item: ", len(itemHash), " #vecs", len(vecHash)," at ", time.asctime()
    randv = numpy.random.randn(d, dim)
    rvecHash = {}
    idx = 0
    for id in itemHash:
        idx += 1
        vec = vecHash.get(id)
        if vec is None:
            continue
        rvecHash[id] = get_signature(vec, randv)
        if idx % 100000 == 0:
            print idx, " items got signature. at ", time.asctime()
    print "signatures obtained #item: ", len(rvecHash), " at ", time.asctime()
    return rvecHash

### main
if __name__ == "__main__":
    print "Program starts at ", time.asctime()

    arg1Hash = {}
    vecHash = {}
    for i in range(1000):
        vec = [random.uniform(-1, 1) for j in range(200)]
        arg1Hash[i] = i
        vecHash[i] = vec

    print "similarity calculating begin at ", time.asctime()

    dim = 200
    d = 2**7
    rvecHash = calSig(arg1Hash, vecHash, d, dim)
    #simHash = callshSim(rvecHash, d)

    q = 5
    B = 100
    hamThreshold = dim*0.2
    simHash = callshfastSim(rvecHash, d, q, B, hamThreshold)

    #print simHash
    print len(simHash)

    print "Program ends at ", time.asctime()
