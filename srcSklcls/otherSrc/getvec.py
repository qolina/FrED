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
            break
        if lineIdx == 1:
            lineIdx += 1
            continue
        arr = lineStr[:-1].split(" ")
        vecHash[arr[0]] = arr[1:]

        lineIdx += 1
    vecfile.close()
    return vecHash

######################
#main
filename = sys.argv[1]

vecHash = getVec(filename)
print "program finished. ",len(vecHash)
