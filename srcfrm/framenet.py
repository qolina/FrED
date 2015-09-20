from nltk.corpus import framenet as fn

'''
#functional test of framenet
print len(fn.frames())
print len(fn.lus())

fid = 256
f = fn.frame(fid)
print f.name
print f.frameRelations
print f.FE
print f.lexUnit
luIDs = [x['ID'] for x in f.lexUnit.values()]
print luIDs

print [x['frame']['name'] for x in fn.lus(r'(?i)a little')]
'''


'''
# n-gram test
# we choose 3-gram LM as most LUs(words) are 1-3 grams.
# LUs 11829 = [11251, 496, 58, 20, 3, 1]
# Frames(event type) 1019 = [442, 369, 156, 41, 10, 1]

lengthList = [len(x['name'].split(" ")) for x in fn.lus()]
print "All: ",
print len(lengthList)

one = len([1 for i in lengthList if i == 1])
two = len([1 for i in lengthList if i == 2])
three = len([1 for i in lengthList if i == 3])
four = len([1 for i in lengthList if i == 4])
five = len([1 for i in lengthList if i == 5])
other = len([1 for i in lengthList if i > 5])

print [one, two, three, four, five, other]
cList = [x['name'] for x in fn.frames() if len(x['name'].split(" ")) > 3]
print cList
'''


'''
frmList = [x['ID'] for x in fn.frames() if len(x['lexUnit']) > 0]
print "#Frame with lexUnits: "

#frmList = [x['ID'] for x in fn.frames() if len(x['lexUnit']) == 0]
#print "#Frame with empty lexUnits: "

print len(frmList)
frmList = sorted(frmList)
for i in frmList:
    f = fn.frame(i)
    print i,
    print ": " + f.name
    print f.definition.encode('gbk', 'ignore')
    print f.FE.keys()
    print f.lexUnit.keys()
    print
'''


'''
luHash = {}
for x in fn.lus():
    #name = x['name'][:x['name'].rfind(".")]
    name = x['name']

    fid = x['frame']['ID']
    if name not in luHash:
        luHash[name] = [fid]
    else:
        if fid not in luHash[name]:
            luHash[name].append(fid)

print len(luHash)
for it in sorted(luHash.items(), key = lambda a:a[0]):
    print it[0],
    print it[1]

'''
