import sys
import os

sys.path.append("/home/yxqin/Scripts")
from strOperation import * # normRep normMen


####################################
#get relation skeletons from relation file(extracted by reverb.jar)
def getRelskl_fromRel(filename):
    print "Processing " + filename
    relFile = file(filename)
    outputDir = os.path.split(filename)[0]
    tStr = filename[-2:]
    outputFile = file(outputDir + r"/relSkl_2013-01-" + tStr, "w")
    lineIdx = 0
    previousTid = tStr + "0"
    previousText = ""
    while 1:
        lineStr = relFile.readline()
        if len(lineStr) <= 0:
            print str(lineIdx) + " lines are processed. End of file. " + str(time.asctime())
            break
        lineIdx += 1
        arr = lineStr.split("\t")
        relArr = []
        #print arr

        tid = tStr+arr[1]
        arg1 = getArg(arr[-3])
        rel = "_".join(arr[-2].split(" "))
        arg2 = getArg(arr[-1][:-1])
        conf = float(arr[11])

        relArr.append(tid)
        relArr.append(normRep(arg1))
        relArr.append(normRep(rel))
        relArr.append(normRep(arg2))
        relArr.append(conf)
        print relArr
        text = "_".join(relArr[1:-1])
        if tid != previousTid:
            if len(previousText) > 1:
                outputFile.write(previousTid + "\t" + previousText + "\n")
            #print "## " + previousTid + " " + previousText
            previousTid = tid
            previousText = text
        else:
            previousText += (" "+text)
        
        if lineIdx % 100000 == 0:
            print "# tweets processed: " + str(lineIdx) + " at " + str(time.asctime())
    outputFile.close()
    relFile.close()

# normMen to be processed
def getArg(item):
    if len(item) > 0:
        return "_".join(normMen(item.split(" ")))
    else:
        return item

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage ore_reverbJar.py inputFileName"
    else:
        filename = sys.argv[1]
        # extract skl from Relation file(reverb.jar)
        getRelskl_fromRel(filename) 
