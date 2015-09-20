import os
import sys
import re


def getVocab(filename, outputfilename):
    wordHash = {}
    relfile = file(filename)
    outfile = file(outputfilename, "wb")
    lineIdx = 1
    wordNum = 0
    while 1:
        lineStr = relfile.readline()
        if not lineStr:
            print "Writing done. ", len(wordHash), " words are writen to ", outputfilename
            print "words number: ", wordNum
            break
        # for relSkl
        #arr = lineStr[:-1].strip().split("\t")
        #content = arr[1]
        # for w2v text
        content = lineStr[:-1].strip()
        content = re.sub("\|", " ", content)
        content = re.sub("\s+", " ", content)
        wordArr = content.strip().split(" ")
        wordNum += len(wordArr)
        for w in wordArr:
            if w not in wordHash:
                wordHash[w] = 1

        lineIdx += 1

    vocabStr = "\t".join(wordHash.keys())
    outfile.write(vocabStr)
    relfile.close()
    outfile.close()
    

######################
#main
filename = sys.argv[1]
outputfilename = sys.argv[2]

getVocab(filename, outputfilename)
print "program finished. "
