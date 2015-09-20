import sys
import re
import time
import cPickle
from nltk.corpus import framenet as fn
from nltk import stem as stem
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
            word_root = stem.WordNetLemmatizer().lemmatize(word_input, pos=pos_sign)
        else: 
            word_root = stem.WordNetLemmatizer().lemmatize(word_input)
    except StandardError as err:
        print(err)
    return(word_root)


def memOf(short, long):
    short = ' ' + short + ' '
    long = ' ' + long + ' '
    idx = long.find(short)
    if (idx > 0) and (long[idx+1]==' '):
        return True
    return False


def toArr(example, seperator):
    return example.split(seperator)


def wordNum(example, seperator):
    return len(toArr(example, seperator))


def numDiff(x, y):
    return wordNum(x, ' ')-wordNum(y, ' ')


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
    if tag==None:
        return None
    lenDiff = dict([(x['ID'], numDiff(getName(x), phrase)) for x in lus if memOf(phrase, getName(x))])
    if len(lenDiff) == 0:
        return None
    minlenDiff = min(lenDiff.values())
    simlus = [fn.lu(x) for x in lenDiff if lenDiff[x] == minlenDiff if getNameTag(fn.lu(x))==tag]
    #print simlus
    if len(simlus) > 0:
        return simlus[0]


def getLU(phrase, tag):
    lus = fn.lus(r'(?i)%s'%phrase)
    if len(lus) == 0:
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


def getFrameID(phrase, tag):
    lu = getLU(phrase, tag)
    if lu:
        id = lu['frame']['ID']
        return id
    else:
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


def analyzePOSNERText(text):
    arr = text.split(" ")
    words = [item.split("/")[0] for item in arr]
    neTags = [item.split("/")[1] for item in arr]
    tags = [item.split("/")[2] for item in arr]
    return words, tags, neTags


def analyzePOSText(text):
    arr = text.split(" ")
    words = [item.split("/")[0] for item in arr]
    tags = [item.split("/")[1] for item in arr]
    words = [illegalFilter(item) for item in words]
    return words, tags


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


def illegalFilter(example):
    # ( or ) appeares in front or end of word
    # [ or ] may appear in any position
    if (example.find("(")==-1) or (example.find(")")==-1):
        example = re.sub(r"[\(\)]", "", example)
    if (example.find("[")==-1) or (example.find("]")==-1):
        example = re.sub(r"[\[\]]", "", example)
    example = re.sub("[\*|]", "", example)
    return example


# extract event pattern from a string
def getPatternFromStr(text):
    [words, tags] = analyzePOSText(text)
    newWords = [word_lemma(words[k], tags[k]) for k in range(len(words))]
    ptns = []
    puncArr = ['dt', '.', 'uh', ',', 'in']
    #cond1
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            if j-i > 3: #3-gram LM
                break
            if (j==i+1) and (tags[i] in puncArr):
                break
            '''
            if (j>i+1) and (not consistant(tags[i:j])):
                break
            if len([x for x in tags[i:j] if x in ['.', 'UH']]) > 0:
                break
            '''
            phrase = ' '.join(newWords[i:j])
            fid = getFrameID(phrase, shortTag(tags[i]))
            if fid:
                ptn = "_".join(words[i:j])+"."+str(fid)
                ptns.append(ptn)
            '''
            print "********** " + phrase
            lu = getLU(phrase, shortTag(tags[j-1]))
            if lu:
                fid = getFrameID(phrase, shortTag(tags[i]))
                print lu['name'],
                print fn.frame(fid)['name']
            '''
    return " ".join(ptns)


# extract event pattern from a file
def getPatternFromFile(infilename, outfilename):
    inputFile = file(infilename)
    outputFile = file(outfilename, "w")
    keptLineHash = {}# only part of tweets contain event patterns (from 0)
    idx = 0
    while 1:
        text = inputFile.readline()[:-1]
        if len(text) < 1:
            print "..End of " + infilename + ". #Line: " + str(idx)
            break
            
        text = text.lower()
        print "**********************",
        print idx
        print text

        '''
        #parenthesis test --> parenthesis appeared in front or end of word
        parens = [locParen(w) for w in words if locParen(w)!=-1]
        '''

        #'''
        ptnStr = getPatternFromStr(text)
        if len(ptnStr) > 1:
            #outputFile.write(str(idx) + "\t" + ptnStr + "\n")
            print ptnStr
            keptLineHash[idx] = 1
            outputFile.write(ptnStr + "\n")
        #'''

        # for comparison of pos and pos_old
        #outputFile.write(text + "\n")

        idx += 1
        if idx % 10000 == 0:
            #break
            print ".... " + str(idx) + " lines are processed at " + str(time.asctime())

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
    getPatternFromFile(sys.argv[1], sys.argv[2])
    #'''
    print "Program FramesExtraction ends at " + str(time.asctime())
