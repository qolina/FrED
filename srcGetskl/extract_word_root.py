#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
import os
import nltk
import sys
import re
import copy
import time
sys.setrecursionlimit(1000000)  # 系统递归深度设置这里设置为一百万
path = os.path.split(os.path.realpath(__file__))[0]


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
            word_root = nltk.stem.WordNetLemmatizer().lemmatize(word_input, pos=pos_sign)
        else: 
            word_root = nltk.stem.WordNetLemmatizer().lemmatize(word_input)
    except StandardError as err:
        print(err)
    return(word_root)


    
def word_affix(word_input, pos_input=None):
    affix = ""
    if pos_input != None:
        word_root = word_lemma(word_input, pos_input)
    else:
        word_root = word_lemma(word_input)
    affix = word_input.replace(word_root, '')
    return(affix)


def word_pl(word_input, pos_input=None):
    affix = word_affix(word_input, pos_input)
    if affix != "":
        return("pl")
    else: 
        return("sg")

