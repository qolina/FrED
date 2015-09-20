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

    '''
    # method 1
    pArr = [[x/num for x in it] for it in pArr]
    pa = pArr[0][0] + pArr[1][1]
    pe = sum(pArr[0])*(pArr[0][0]+pArr[1][0]) + sum(pArr[1])*(pArr[0][1]+pArr[1][1])
    '''

    #'''
    # wikipedia
    pa = (pArr[0][0] + pArr[1][1])/num
    a0 = sum(pArr[0])/num
    b0 = (pArr[0][0] + pArr[1][0])/num
    pe = a0*b0 + (1-a0)*(1-b0)
    #'''

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


###############
#main
if len(sys.argv) != 6:
    print "Usage: li yao duan qin sysTagFile"
    sys.exit()

filename_li = sys.argv[1]
filename_yao = sys.argv[2]
filename_duan = sys.argv[3]
filename_qin = sys.argv[4]
filename_sysTag = sys.argv[5]

[idTosys, tagsAll] = loadIDToSys(filename_sysTag)

scoreTags = ["1", "2"]
lblTags = ["0", "1"]
[score_qin, lbl_qin] = getEval(filename_qin, scoreTags, lblTags)
[score_li, lbl_li] = getEval(filename_li, scoreTags, lblTags)
[score_duan, lbl_duan] = getEval(filename_duan, scoreTags, lblTags)

scoreTags = ["hard", "easy"]
lblTags = ["no", "yes"]
[score_yao, lbl_yao] = getEval(filename_yao, scoreTags, lblTags)

print "Mixure kappa:"
print "..Label"
outKappaWithinUsers(lbl_li, lbl_duan, lbl_yao, lbl_qin, [0, 1])
#getKappa(score_li, score_yao, [1, 2])

[tlbl_qin, flbl_qin] = sepToSys(lbl_qin, idTosys)
'''
print len(tlbl_qin),
print len(flbl_qin)
'''
[tlbl_li, flbl_li] = sepToSys(lbl_li, idTosys)
[tscore_li, fscore_li] = sepToSys(score_li, idTosys)
[tlbl_yao, flbl_yao] = sepToSys(lbl_yao, idTosys)
[tscore_yao, fscore_yao] = sepToSys(score_yao, idTosys)
[tlbl_duan, flbl_duan] = sepToSys(lbl_duan, idTosys)
[tscore_duan, fscore_duan] = sepToSys(score_duan, idTosys)

print "..Twevent: "
#print getKappa(tscore_li, tscore_yao, [1, 2])
outKappaWithinUsers(tlbl_li, tlbl_duan, tlbl_yao, tlbl_qin, [0, 1])
print "....Precision of Yao: "
print getPre(tlbl_yao, tlbl_qin, [0, 1])
print "....Precision of Li: "
print getPre(tlbl_li, tlbl_qin, [0, 1])
print "....Readability"
print [getAvg(tscore_li), getAvg(tscore_duan), getAvg(tscore_yao)]

print "..FrED: "
#print getKappa(fscore_li, fscore_yao, [1, 2])
outKappaWithinUsers(flbl_li, flbl_duan, flbl_yao, flbl_qin, [0, 1])
print "....Precision of Yao: "
print getPre(flbl_yao, flbl_qin, [0, 1])
print "....Precision of Li: "
print getPre(flbl_li, flbl_qin, [0, 1])
print "....Readability"
print [getAvg(fscore_li), getAvg(fscore_duan), getAvg(fscore_yao)]


print "..Disagreed items: Li vs Qin"
print " ".join(getDisagree(lbl_li, lbl_qin))
print "..Disagreed items: Yao vs Qin"
print " ".join(getDisagree(lbl_yao, lbl_qin))
print "..Disagreed items: Duan vs Qin"
print " ".join(getDisagree(lbl_duan, lbl_qin))

