import os
import sys


def getVec(filename):
    vecHash = {}
    vecfile = file(filename)
    lineIdx = 1
    firstLine = vecfile.readline()[:-1].split(" ")
    wnum = firstLine[0]
    vecLen = firstLine[1]
    while 1:
        lineStr = vecfile.readline()
        if not lineStr:
            print "Loading done. [wnum, vecLen] ",firstLine, " vecHash: ", len(vecHash)
            print maxSim, " ", minSim
            break
        if lineIdx == 1:
            lineIdx += 1
            continue
        arr = lineStr[:-1].split(" ")

        # get range of vectors similarities
        if len(vecHash) > 0:
            for item in vecHash:
                sim = cosineSim(vecHash[item], arr[1]) 
                if sim > maxSim[0]:
                    simTemp = [val for val in maxSim]
                    simTemp.append(sim)
                    simTemp.sorted()
                    maxSim = simTemp[-3:]
                if sim < minSim[-1:]:
                    simTemp = [val for val in minSim]
                    simTemp.append(sim)
                    simTemp.sorted()
                    minSim = simTemp[:3]
                    
        vecHash[arr[0]] = arr[1:]

        lineIdx += 1
        if lineIdx % 100000 == 0:
            print lineIdx, " lines are processed. ", maxSim, " ", minSim
    vecfile.close()
    return vecHash

######################
#main
global maxSim, minSim
maxSim = [-9999.0]*3 # [3rd, 2nd, largest]
minSim = [9999.0]*3 # [smallest, 2nd, 3rd]

filename = sys.argv[1]

vecHash = getVec(filename)

print "Largest sim betweet frames: ", sum(maxSim)
print "Smallest sim betweet frames: ", sum(minSim)

print "program finished. ",len(vecHash)
