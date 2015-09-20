import sys
import re
import time
import cPickle
from nltk.corpus import framenet as fn
from nltk.stem import WordNetLemmatizer as wnlemmer
from copy import deepcopy
#import extract_word_root as rt

## Preprocess: for all nouns, adj, adv, convert to original form of words
## Definition of event frame(pattern)
# for all gram in 3-gram LM,
# 1) get all words' corresponding framesID (in FrameNet) if exists
# 2) to be added

def word_lemma(word_input, pos_input=None):
    if pos_input in ["NN", "NNP", "NNS", "NNPS", "CD", "DT", "FW"]:
        pos_sign = 'n'
    elif pos_input in ["VB", "VBD", "VBG", "VBP", "VBZ"]:
        pos_sign = 'v'
    elif pos_input in ["JJ", "JJR", "JJS"]:
        pos_sign = 'a'
    elif pos_input in ["RB", "RBR", "RBS", "RP"]:
        pos_sign = 'r'
    else:
        pos_sign = None
    try:
        if pos_sign != None:
            word_root = wnlemmer().lemmatize(word_input, pos=pos_sign)
        else: 
            word_root = wnlemmer().lemmatize(word_input)
    except StandardError as err:
        print(err)
    return(word_root)


def memOf(short, long):
    short = ' ' + short + ' '
    long = ' ' + long + ' '
    if long.find(short) >= 0:
        return True
    return False


def toArr(example, seperator):
    return example.split(seperator)


def wordNum(example, seperator):
    return len(toArr(example, seperator))


def numDiff(x, y):
    #return wordNum(x, ' ')-wordNum(y, ' ')
    return len(x.split(" ")) - len(y.split(" "))


def getName(x):
    return x['name'][:x['name'].rfind(".")]


def getNameTag(x):
    return x['name'][x['name'].rfind(".")+1:]


def exactLU(phrase, lus):
    exactLUs = [x for x in lus if getName(x)==phrase]
    #print "exact: ",
    #print [x['name'] for x in lus if getName(x)==phrase]
    if len(exactLUs) >= 1:
        return exactLUs[0]
    return None


def rndLU(phrase, tag, lus):
    lenOflus = dict([(x['ID'], len(getName(x).split(" "))) for x in lus if memOf(phrase, getName(x))])
    for x in sorted(lenOflus.items(), key = lambda a:a[1]):
        if getNameTag(fn.lu(x[0]))==tag:
            return fn.lu(x[0])
    return None


def getLU_online(phrase, tag):
    lus = fn.lus(r'(?i)%s'%phrase)
    if (tag is None) or (len(lus) == 0):
        return None
    #print "Lus: ",
    #print [x['name'] for x in lus][:min(20, len(lus))]
    exactlu = exactLU(phrase, lus)
    if exactlu:
        return exactlu
    else:
        #print "mulLus: ",
        #print [x['name'] for x in lus][:min(10, len(lus))]
        return rndLU(phrase, tag, lus)


def getLU_local(phrase, tag):
    if tag is None:
        return None
    # exact match(word.tag)
    phstag = phrase+"."+tag
    if phstag in luHash: 
        luids = luHash[phstag]
        if len(luids) == 1:
            return luids[0]
        else: #problem - when one word have multiple Frame matches
            return luids[0]
    
    #No exact match
    #problem- choose one match with same tag as tagOfphrase
    lenOflus = dict([(x, len(x.split(" "))) for x in luHash if memOf(phrase, x[:x.rfind(".")])])
    for item in sorted(lenOflus.items(), key = lambda a:a[1]):
        x = item[0]
        if x[x.rfind(".")+1:]==tag:
            return luHash[x][0]
    return None


def getFrameID(lu):
    if lu:
        return lu['frame']['ID']
    return None


def consistant(tags):
    hash = dict([(x, 1) for x in tags])
    if len(hash) == 1:
        return True
    return False


def shortTag(tag):
    tag = tag.lower()
    if tag.startswith("nn"):
        return 'n'
    elif tag.startswith("vb"):
        return 'v'
    elif tag.startswith("jj"):
        return 'a'
    elif tag.startswith("rb"):
        return 'adv'
    elif tag.startswith("cc"):
        return 'c'
    elif tag.startswith("cd"):
        return 'num'
    elif tag.startswith("in"):
        return 'prep'
    elif tag.startswith("uh"):
        return 'intj'
    else:
        return None


def loadFileIntoDict(filename):
    inputFile = file(filename)
    content = inputFile.readlines()
    hash = dict([(line[:-1], 1) for line in content])
    print "..Content in " + filename + " have been loaded into dict. #Item: " + str(len(hash))
    inputFile.close()
    return hash


def getluHash():
    luHash = {} #luname:luids
    for x in fn.lus():
        #name = x['name'][:x['name'].rfind(".")]
        name = x['name']
        id = x['ID']
        #id = x['frame']['ID']
        if name not in luHash:
            luHash[name] = [id]
        else:
            if id not in luHash[name]:
                luHash[name].append(id)
    print "..All LUs in FrameNet have been loaded into dict. #Item: " + str(len(luHash))
    return luHash

    
def analyzePOSNERText(text):
    arr = text.split(" ")
    words = [item.split("/")[0] for item in arr]
    neTags = [item.split("/")[1] for item in arr]
    tags = [item.split("/")[2] for item in arr]
    return words, tags, neTags


def analyzePOSText(text):
    arr = text.split(" ")
    words = [item.split("/")[0] for item in arr if item[0].find("@")==-1]
    tags = [item.split("/")[1] for item in arr if item[0].find("@")==-1]
    words = [illegalFilter(item) for item in words]
    return words, tags


def illegalFilter(example):
    # ( or ) appeares in front or end of word
    # [ or ] may appear in any position
    example = re.sub(r"[\(\)\[\]\{\}]", "", example)
    example = re.sub(r"[\*\?\+\^\.\$\#\!\-\\\/]", "", example)
    return example


def locParen(example):
    if example.find("(") > 0:
        return 1
    elif example.find("(") == 0:
        return 0
    if example.find(")") >= 0:
        if example.find(")") == len(example)-1:
            return 0
        if example.find(")") < len(example)-1:
            return 1
    return -1


# extract event pattern from a string
def getPatternFromStr(text):
    #global frmHash, savNum
    [words, tags] = analyzePOSText(text)
    newWords = [word_lemma(words[k], tags[k]) for k in range(len(words))]
    #print newWords
    ptns = []
    puncArr = ['dt', '.', 'uh', ',', 'in']
    uselessArr = [None, 'c', 'scon', 'prep', 'intj']
    #cond1
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            if j-i > 3: #3-gram LM
                break
            if (j==i+1) and (tags[i] in puncArr):
                break
            if len([x for x in tags[i:j] if shortTag(x) in uselessArr]) > 0:
                break

            #if (j>i+1) and (not consistant(tags[i:j])):
                #break

            phrase = ' '.join(newWords[i:j])
            '''
            if phrase not in frmHash:
            #print "********** " + phrase
                # online with framenet
                #lu = getLU_online(phrase, shortTag(tags[j-1]))
                # local with framenet
                lu = None
                luid = getLU_local(phrase, shortTag(tags[j-1]))
                if luid:
                    lu = fn.lu(luid)
                frmHash[phrase] = lu
            else:
                savNum += 1
                lu = frmHash[phrase]
            '''
            # online with framenet
            #lu = getLU_online(phrase, shortTag(tags[j-1]))
            # local with framenet
            lu = None
            luid = getLU_local(phrase, shortTag(tags[j-1]))
            if luid:
                lu = fn.lu(luid)

            if lu:
                fid = getFrameID(lu)
                ptn = "_".join(words[i:j])+"."+str(fid)
                ptns.append(ptn)
                #print lu['name'],
                #print fn.frame(fid)['name']
    return " ".join(ptns)


# extract event pattern from a file
def getPatternFromFile(infilename, outfilename):
    inputFile = file(infilename)
    outputFile = file(outfilename, "w")
    #global frmHash
    #frmHash = {}
    keptLineHash = {}# only part of tweets contain event patterns (from 0)
    idx = 0
    while 1:
        text = inputFile.readline()[:-1]
        if len(text) < 1:
            print "..End of " + infilename + ". #Line: " + str(idx)
            break
            
        text = text.lower()
        #print "**********************",
        #print idx
        #print text

        '''
        #parenthesis test --> parenthesis appeared in front or end of word
        parens = [locParen(w) for w in words if locParen(w)!=-1]
        '''

        #'''
        ptnStr = getPatternFromStr(text)
        if len(ptnStr) > 1:
            #outputFile.write(str(idx) + "\t" + ptnStr + "\n")
            #print ptnStr
            keptLineHash[idx] = 1
            outputFile.write(ptnStr + "\n")
        #'''

        # for comparison of pos and pos_old
        #outputFile.write(text + "\n")

        idx += 1
        if idx % 100 == 0:
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime())
            #print len(frmHash)
            #break

    kptLnFile = file(outfilename+".kptln", "w")
    cPickle.dump(keptLineHash, kptLnFile)
    kptLnFile.close()
        
    inputFile.close()
    outputFile.close()


if __name__ == "__main__":

    print "Program FramesExtraction starts at " + str(time.asctime())

    text_example = "see/VB you/PRP later/RB shitlords/NN !/. bye/UH 2012/UH Saw/VBZ Baidu/NNP in/DT explosion/NN today/RB ./."

    '''
    # test analyzePOSNERText
    print text_example
    [words, tags, neTags] = analyzePOSNERText(text_example)
    print words
    print tags
    print neTags
    '''

    '''
    # test getPatternFromStr
    ptnStr = getPatternFromStr(text_example)
    '''

    #'''
    # test getPatternFromFile
    if len(sys.argv) != 3:
        print "Usage: evtptn.py inputfilename outputfilename"
        sys.exit()

    global luHash
    luHash = getluHash()
    getPatternFromFile(sys.argv[1], sys.argv[2])
    #'''
    print "Program FramesExtraction ends at " + str(time.asctime())
