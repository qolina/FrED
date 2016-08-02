#! /usr/bin/env python
#coding=utf-8
# function: for calculating similarity between two segments/skeletons when clustering them
import time
import re
import os
import cPickle
import sys

sys.path.append("/home/yxqin/Scripts/")
from hashOperation import *

sys.path.append("/home/yxqin/FrED/srcSklcls/")
from estimatePs_smldata import statisticDF_fromFile
from estimatePs_smldata import statisticDF

sys.path.append("/home/yxqin/SED/src/")
from getSnP500 import loadSnP500

############################
## main Function
if __name__ == "__main__":

    if len(sys.argv) == 2:
        inputDir = sys.argv[1]
        outputDir = inputDir
    elif len(sys.argv) == 3:
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
    else:
        print "Usage: python statisticWordDf.py inputDir(eg. ~/corpus/data_twitter201301/201301_clean) [outputDir default:=inputDir]"
        sys.exit(0)

    sym_names = loadSnP500("/home/yxqin/corpus/obtainSNP500/snp500_ranklist_20160801")
    snpSym = ["$"+item[0].lower() for item in sym_names]
    #print "## snpSyms:", snpSym[:5]

###################################################################
    [snpCompHash, windowHash] = statisticDF(inputDir, snpSym)
    compDFHash = {}
    for comp in snpCompHash:
        avg_df = sum(snpCompHash.get(comp).values())/float(len(windowHash))
        compDFHash[comp] = avg_df

    #sortedList = sortHash(compDFHash, 1, True)
    #for item in sortedList:#[:50]
    for sym in snpSym:
        if sym not in snpCompHash:
            continue
        sorted_df = sortHash(snpCompHash.get(sym), 0, False)
        df_sorted = [str(dfItem[1]) for dfItem in sorted_df]
        print sym, "\t", compDFHash.get(sym), "\t", "\t".join(df_sorted)
        #print "\t".join(df_sorted)

###################################################################
#    wordAppHash = {}
#    wordDFHash = {}
#
#    for tStr in xrange(1, 32):
#        tStr = str(tStr).zfill(2)
#        textFilename = inputDir + r"/tweetCleanText"+tStr
##        textFilename = inputDir + r"/text_2013-01-"+tStr
##        textFilename = inputDir + r"/relSkl_2013-01-"+tStr
#        content = open(textFilename, "r").readlines()
#
#        wordAppHash_t = {}
#        content = [line[:-1] for line in content]
#        for lineStr in content:
#            arr1 = lineStr.strip().split("\t")
#            tid = arr1[0]
#            #text = re.sub(r"_", " ", arr1[1])
#            text = arr1[-1]
#            arr = text.lower().split()
#
#            for w in arr:
#                #if len(w) == 0 or w[0] != "$": # only statistic company df
#                if w not in snpSym: # only statistic company df
#                    continue
#                if w in wordAppHash_t:
#                    wordAppHash_t[w].update(dict([(tid, 1)]))
#                else:
#                    wordAppHash_t[w] = dict([(tid, 1)])
#
#        wordAppHash.update(wordAppHash_t)
#        wordDFHash_t = dict([(w, len(wordAppHash_t.get(w))) for w in wordAppHash_t])
#
#        print "## loading done. ", time.asctime(), textFilename, len(wordAppHash_t)
#        print "total #tweet", sum(wordDFHash_t.values())
#        print "avg #tweet/company", sum(wordDFHash_t.values())/float(len(wordDFHash_t))
#
#        sortedList = sortHash(wordDFHash_t, 1, True)
#        for item in sortedList[:50]:
#            print item[0], "\t", item[1]
#
#
#
#    
#    #wordDFHash = dict([(w, len(wordAppHash.get(w))) for w in wordAppHash])
##
##    wordDFFile = file(outputDir + r"/wordDF", "w")
##    cPickle.dump(wordDFHash, wordDFFile)
##    wordDFFile.close()
#
##    print "Program ends. " + str(time.asctime()) + " " + str(len(wordDFHash)) + " words are obtained! Writen into " + wordDFFile.name
