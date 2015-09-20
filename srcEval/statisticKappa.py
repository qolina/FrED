import os
import sys
import cPickle

def getEval(filename, scoreTags, lblTags):
    inFile = file(filename)
    arr = inFile.readlines()
    arr = [line[:-1].split("\t")[:2] for line in arr]
    scoreArr = []
    lblArr = []

    for it in arr:
        if it[0] == scoreTags[0]:
            scoreArr.append(1)
        elif it[0] == scoreTags[1]:
            scoreArr.append(2)

        if it[1] == lblTags[0]:
            lblArr.append(0)
        elif it[1] == lblTags[1]:
            lblArr.append(1)

    #print arr
    #print scoreArr
    #print lblArr
    inFile.close()
    return scoreArr, lblArr


def getDisagree(arr1, gold):
    disagree = []
    disagreeNum = 0
    for i in range(len(arr1)):
        if arr1[i] != gold[i]:
            disagree.append(str(i+2))
            disagreeNum += 1
        else:
            disagree.append('-')
    print "#Disagree: " + str(disagreeNum)
    return disagree


def getPre(arr1, gold, tags):
    cls1 = 0
    cls2 = 0
    for i in range(len(arr1)):
        if arr1[i] == gold[i]:
            if gold[i] == tags[0]:
                cls1 += 1
            else:
                cls2 += 1
    cls1Pre = cls1*1.0/len(arr1)
    cls2Pre = cls2*1.0/len(arr1)
    #return [cls1, cls2, sum(arr1), sum(gold), len(arr1)]
    return [cls1Pre, cls2Pre]


def getAvg(arr):
    return sum(arr)*1.0/len(arr)


def getKappa(arr1, arr2, tags):
    pArr = [[0, 0], [0, 0]]
    for i in range(len(arr1)):
        lbl1 = arr1[i]
        lbl2 = arr2[i]
        if lbl1 == lbl2:
            if lbl1 == tags[0]:
                pArr[0][0] += 1
            if lbl1 == tags[1]:
                pArr[1][1] += 1
        else:
            if lbl1 == tags[0]:
                pArr[0][1] += 1
            if lbl1 == tags[1]:
                pArr[1][0] += 1
    #print pArr
    num = sum([sum(it) for it in pArr])*1.0
    #pArr = [[20, 5], [10, 15]] #test arr

    # method 1
#    pArr = [[x/num for x in it] for it in pArr]
#    pa = pArr[0][0] + pArr[1][1]
#    pe = sum(pArr[0])*(pArr[0][0]+pArr[1][0]) + sum(pArr[1])*(pArr[0][1]+pArr[1][1])

    # definition in wikipedia
    pa = (pArr[0][0] + pArr[1][1])/num
    a0 = sum(pArr[0])/num
    b0 = (pArr[0][0] + pArr[1][0])/num
    pe = a0*b0 + (1-a0)*(1-b0)

    kappa = (pa-pe)/(1.0-pe)

    return sum([x for x in pArr], []), kappa


def sepToSys(arr, idTosys):
    tArr = []
    fArr = []
    for i in range(len(arr)):
        if idTosys[i].startswith("t"):
            tArr.append(arr[i])
        elif idTosys[i].startswith("f"):
            fArr.append(arr[i])
        '''
        print idTosys[i],
        print len(tArr),
        print len(fArr)
        '''
    return tArr, fArr

        
def loadIDToSys(filename):
    sysTagFile = file(filename)
    idTosys = cPickle.load(sysTagFile)
    tagsAll = cPickle.load(sysTagFile)
    sysTagFile.close()
    return idTosys, tagsAll
    

def outKappaWithinUsers(lbl_li, lbl_duan, lbl_yao, lbl_qin, tagArr):
    print "....Li vs Yao: ",
    print getKappa(lbl_li, lbl_yao, tagArr)
    print "....Li vs Duan: ",
    print getKappa(lbl_li, lbl_duan, tagArr)
    print "....Li vs Qin: ",
    print getKappa(lbl_li, lbl_qin, tagArr)
    print "....Yao vs Duan: ",
    print getKappa(lbl_yao, lbl_duan, tagArr)
    print "....Yao vs Qin: ",
    print getKappa(lbl_yao, lbl_qin, tagArr)
    print "....Duan vs Qin: ",
    print getKappa(lbl_duan, lbl_qin, tagArr)


def getTags(eventListFilename):
    eventListFile = file(eventListFilename)
    content = eventListFile.readlines()
    eventListFile.close()

    eventTagList = []
    for line in content:
        if not line.startswith("###"):
            continue
        arr = line.strip("###").split("###")
        if arr[0] in ["t", "T", "M", "m"]:
            tag = 1
        elif arr[0][0] in ["f", "F", "?"]:
            tag = 0
        else:
            print "Special tag in : ", line
            tag = 0

        eventTagList.append(tag)

    print len(eventTagList), " events' tag are obtained from ", eventListFilename

    return eventTagList


###############
#main
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: python statisticKappa.py eventList_Filename_annotater1 eventList_Filename_annotater2"
        sys.exit()

    eventListFilename_usr1 = sys.argv[1]
    eventListFilename_usr2 = sys.argv[2]

    eventTagList_usr1 = getTags(eventListFilename_usr1)
    eventTagList_usr2 = getTags(eventListFilename_usr2)

    [tagArr , kappa] = getKappa(eventTagList_usr1, eventTagList_usr2, [0, 1])
    print "Kappa value: ", kappa, tagArr
    print "Precision: ", tagArr[-1]*1.0/(tagArr[0]+tagArr[-1])


    print "..Disagreed items: "
    print " ".join(getDisagree(eventTagList_usr1, eventTagList_usr2))

