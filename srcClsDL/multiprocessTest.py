
import os
import time
import random
import math
import multiprocessing
from lshtest import *
import sys

def getPair(id1, id2):
    ids = [str(id1), str(id2)]
    ids.sort()
    return "-".join(ids)

def calLens(itemHash, vecHash):
    print "begin calculating len of items. #item: ", len(itemHash), " at ", time.asctime()
    for item in itemHash:
        vec = vecHash.get(int(item))
        if vec is None:
            itemHash[item] = None
            continue
        vec2 = [val*val for val in vec]
        length = math.sqrt(sum(vec2))
        itemHash[item] = length
        if i % 100000 == 0:
            print "i ", i, " items are processed at ", time.asctime()
    return itemHash

def calSims(itemHash):
    simHash = {}
    #print "begin calculating sim of pairs. #item: ", len(itemHash), " at ", time.asctime()
    itemList = itemHash.keys()
    itemList.sort()
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

        '''
        if i < 1000:
            print "i ", i, " items are processed at ", time.asctime()
        elif i <= 1000 and i % 10 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        elif i > 1000 and i % 10000 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        if i % 100 == 0:
            print "i ", i, " items are processed at ", time.asctime()
        '''
    return simHash

def generateData(result, num):
    arg1Hash = {}
    vecHash = {}
    for i in range(num):
        vec = [random.uniform(-1, 1) for j in range(200)]
        arg1Hash[i] = i
        vecHash[i] = vec
    result.put(vecHash)
    result.put(arg1Hash)

### main
print "Program starts at ", time.asctime()

#[arg1Hash, vecHash] = generateData(1000)
#[arg2Hash, vecHash2] = generateData(1000)

'''
d = 2**7
dim = 200
rvecHash = calSig(arg1Hash, vecHash, d, dim)
lshsimHash1 = callshSim(rvecHash, d)
print "lsh sim done"
'''

#arg1Hash = calLens(arg1Hash, vecHash)
#arg2Hash = calLens(arg2Hash, vecHash2)

queue = multiprocessing.Queue()
process = multiprocessing.Process(target=generateData, args=(queue, 1000, ))
process.start()
process.join()
[arg1Hash, vecHash1] = [queue.get(), queue.get()]
print arg1Hash
print vecHash1
#vecHash = queue.get()

sys.exit()

process = multiprocessing.Process(calLens, [arg1Hash, vecHash])
process.start()
process.join()


#pool = multiprocessing.Pool(processes=5)
#result = pool.apply(calSims, [arg1Hash]) no return value
#result = pool.apply_async(calSims, [arg1Hash])
#simHash = result.get()
#simHash = pool.map(calSims, [arg1Hash])[0]
#result = pool.map_async(calSims, [arg1Hash], 5)
#simHash = result.get()[0]
#pool.close()
#pool.join()
#simHash = calSims(arg1Hash)

#print simHash
#print len(lshsimHash1)
print "Program ends at ", time.asctime()
