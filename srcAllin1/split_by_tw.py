import sys
from collections import Counter

def splitfile(filename):
    textfile = file(filename)

    currtw = ""
    textArr = []
    lineIdx = 0
    while 1:
        text = textfile.readline()
        if not text:
            day_textfile = file(filename+"_"+tw.zfill(2), "w")
            for item in textArr:
                day_textfile.write(item+"\n")
            day_textfile.close()
            print "# write to file", filename+"_"+tw.zfill(2), len(textArr)
            break
        tw = twHash[lineIdx]
        #subtw = subtwHash[lineIdx]
        if tw == currtw: textArr.append(text.strip())
        else: 
            if currtw != "": 
                day_textfile = file(filename+"_"+currtw.zfill(2), "w")
                for item in textArr:
                    day_textfile.write(item+"\n")
                day_textfile.close()
                print "# write to file", filename+"_"+currtw.zfill(2), len(textArr)
            textArr = []
            textArr.append(text.strip())
            currtw = tw
        lineIdx += 1
        if lineIdx % 500000 == 0: print "Processed tweet", lineIdx, currtw

def loadtw(filename):
    global twHash,subtwHash
    twHash = {}
    twfile = file(filename)
    lineIdx = 0
    while 1:
        line = twfile.readline()
        if not line: break
        twHash[lineIdx] = line.strip().split(" ")[1]
        lineIdx += 1
    twfile.close()
    print "#tweet ", len(twHash)
    print Counter(twHash.values()).most_common()


if __name__ == "__main__":
    print "Usage: python .py tweet_id_tw_subtw.txt tweet_text.txt tweet_text_pos_v2 tweet_text_chunked"
    
    loadtw(sys.argv[1])

    splitfile(sys.argv[2])
    splitfile(sys.argv[3])
    splitfile(sys.argv[4])


