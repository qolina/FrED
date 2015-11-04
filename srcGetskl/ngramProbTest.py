#! /usr/bin/env python
#coding=utf-8

import urllib
import urllib2
import os
import re
import time
import sys

## main
print "Program starts at time:" + str(time.asctime())
#"are_dunes_on_saturn's_-kidscantravel"
#saturn
#finished_wants_to
#finished

#gramStr = "estes_punto_de_besarla_nombre"
gramStr = "finished"
gramStr = urllib.quote(gramStr)
'''
try:
    probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',gramStr)).read()
except:
    print "Error with gram: " + gramStr
    probStr = "-1"
#print probStr
'''

# redmond server
print "redmond server(token1), word: " + gramStr
probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6ad01338-a036-4184-acc5-380e9aad7fb4',gramStr)).read()
print probStr
# token2
print "redmond server(token2), word: " + gramStr
probStr = urllib2.urlopen(urllib2.Request('http://weblm.research.microsoft.com/weblm/rest.svc/bing-body/apr10/5/jp?u=6c5bffbd-e43c-44ab-8c69-acf0439a7a6b',gramStr)).read()
print probStr

# beijing server  -- down, not working
#print "Beijing server, word: " + gramStr
#probStr = urllib2.urlopen(urllib2.Request('http://msraml-s003/ngram-lm/rest.svc/bing-body/apr10/5/jp?u=msrauser001',gramStr)).read()
#print probStr

print "Program ends at time:" + str(time.asctime())

