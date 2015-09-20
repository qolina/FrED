
import re
import sys
import time
import cPickle
from getEvent import *
from getEventSegPair import *
from estimatePs_frm import *


def verifyBty(dataFilePath, flag, btyUnitHash):
    btyUnitDFHash = {}

    frmList = loadFrmlist(dataFilePath)
    [frmCluster, clusters] = loadFrmCls(dataFilePath, flag)
    exactFile = file(dataFilePath+"frmExactDF")
    windowHash = cPickle.load(exactFile)
    frmDFHash = cPickle.load(exactFile)
    print "Exact match unit hash is loaded from ", exactFile.name, " at ", time.asctime()
    exactFile.close()
    
    for clusID in clusters:
        frms = clusters[clusID]
        dfHash = dict([(str(t).zfill(2), {}) for t in range(1, 16)])
        for frm in frms:
            tempArr = [dfHash[t].update(frmDFHash[frm][t]) for t in frmDFHash[frm]]
        psProb = getPSval(dfHash, windowHash)
        for frm in frms:
            if frm in btyUnitHash:
                btyUnitDFHash[frm] = dfHash
            if len(btyUnitDFHash) == len(btyUnitHash):
                break

    for frm in frmList:
        if len(btyUnitDFHash) == len(btyUnitHash):
            break
        if frm in btyUnitHash:
            btyUnitDFHash[frm] = frmDFHash[frm]
    print len(btyUnitHash), " frm's df has been calculated. at ", time.asctime()
    exactUnitDFHash = dict([(item, frmDFHash[item]) for item in btyUnitHash])
    return btyUnitDFHash, exactUnitDFHash

def toOriFrm(frm):
    eleArr = frm.split("|")
    eleArr = [vocab2strHash.get(int(ele)) for ele in eleArr]
    #eleArr = [ for ele in eleArr]
    return "|".join(eleArr)

##################################
# main
if __name__ == "__main__":
    print "###program starts at " + str(time.asctime())
    # for debugging bursty methods
    dataFilePath = r"../exp/w2v/"
    global vocab2strHash
    flag = ""
    vocab2strHash = loadEle2StrVocab(dataFilePath)

    '''
    btySklFileName = sys.argv[1]
    [unitHash, unitDFHash, unitInvolvedHash] = loadEvtseg(btySklFileName)

    [btyUnitDFHash, exactUnitDFHash] = verifyBty(dataFilePath, flag, unitHash)
    btyVerifyFile = file(dataFilePath+"btyVery", "w")
    cPickle.dump(btyUnitDFHash, btyVerifyFile)
    cPickle.dump(exactUnitDFHash, btyVerifyFile)
    btyVerifyFile.close()
    print "Verify bursty skl file is dumpted into ", btyVerifyFile.name
    '''

    btyVerifyFile = file(dataFilePath+"btyVery")
    btyUnitDFHash = cPickle.load(btyVerifyFile)
    exactUnitDFHash = cPickle.load(btyVerifyFile)
    btyVerifyFile.close()
    print "Verify bursty skl file is loaded from ", btyVerifyFile.name

    #print btyUnitDFHash.keys()
    noneArr1 = [1 for item in btyUnitDFHash if item.startswith("0|")]
    noneArr2 = [1 for item in btyUnitDFHash if item.endswith("|0")]
    isArr = [1 for item in btyUnitDFHash if item.find("|34|")>0]
    usrArr = [1 for item in btyUnitDFHash if toOriFrm(item).find("@usr")>=0]
    print "All: ", len(btyUnitDFHash)
    print "NoneArg [arg1, arg3]: ", [len(noneArr1), len(noneArr2)]
    print "Verb (is): ", len(isArr)
    print "@usr: ", len(usrArr)

    sys.exit()
    for item in sorted(btyUnitDFHash.keys()):
        frm = toOriFrm(item)
        #frm = item
        dfHash = btyUnitDFHash[item]
        exactdfHash = exactUnitDFHash[item]
        print "******************", item, " ", frm, " " 
        print [len(dfHash[t]) for t in sorted(dfHash.keys())]
        print [len(exactdfHash[t]) for t in sorted(exactdfHash.keys())]
        #print [(t, len(dfHash[t])) for t in sorted(dfHash.keys())]
        #print [(t, len(exactdfHash[t])) for t in sorted(exactdfHash.keys())]

    print "###program ends at " + str(time.asctime())
