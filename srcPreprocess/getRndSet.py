import sys
import random

if len(sys.argv) != 4:
    print "usage: python getRndSet.py inputfilename dataSize outfilename \n func: randomly get dataSize lines from inputfilename."
    sys.exit(0)

dataSize = int(sys.argv[2])
rndIdx = random.sample(range(1145802), dataSize)
print rndIdx
rndIdx.sort()
print rndIdx

datafile = file(sys.argv[1])
outfile = file(sys.argv[3], "w")
idx = 0
while 1:
    lineStr = datafile.readline()
    if not lineStr:
        break
    if idx in rndIdx:
        outfile.write(lineStr)
    idx += 1


datafile.close()
outfile.close()
