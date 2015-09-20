import sys
import cPickle
import time

idx = 0
datahash = {}

'''
filename = sys.argv[1]
datafile = file(filename)
while 1:
    lineStr = datafile.readline()
    if not lineStr:
        break
    val = lineStr[:-1].split("\t")[2]
    val = val[:3]
    if val in datahash:
        datahash[val] += 1
    else:
        datahash[val] = 1
    idx += 1
    if idx % 1000000 == 0:
        print idx
        #break
'''


dataFilePath = sys.argv[1]
simVocabFile = file(dataFilePath+"/frmSimVocab")
lshsimHash = cPickle.load(simVocabFile)
simVocabFile.close()
print "lshfrmsimHash loading done at ", time.asctime(), " #num: ", len(lshsimHash)

for key in lshsimHash:
    val = lshsimHash[key]
    val = "%.1f"%val
    if val in datahash:
        datahash[val] += 1
    else:
        datahash[val] = 1
    idx += 1
    if idx % 1000000 == 0:
        print idx
        #break

all = sum(datahash.values())
for item in sorted(datahash.items(), key = lambda a:a[0]):
    print item[0],
    print item[1]*1.0/all
