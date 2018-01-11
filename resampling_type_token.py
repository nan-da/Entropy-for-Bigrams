#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 18:53:06 2017

"""
from __future__ import division
import nltk
import re
import codecs
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
import glob

path = "jockers.txt"

def read_stopwords(path):
    #going to have to update stop_words list to include personal names (if we are including bag-of-words)
    text = codecs.open(path, "r", "utf-8")
    raw = text.read()
    #need to turn stopwords into a list
    raw = nltk.word_tokenize(raw)
    jockers_stopwords = []
    for word in raw:
        jockers_stopwords.append(word)
    return jockers_stopwords

#global jockers_stopwords 
#jockers_stopwords = read_stopwords(path) 

#cleaner functions
def cleaner(text, tokenize = False, lower=True):
    text = re.sub(r'[0-9]', '', text)
    text = re.sub(r'[,.;:"?!*()\']', '', text)
    text = re.sub(r'-', ' ', text)
    text = re.sub(r'[\n\t]', ' ', text)
    text = re.sub(r'[^a-zA-Z ]+', '', text)
    
    if lower:
        text = text.lower()
        
    if tokenize:
        text = nltk.word_tokenize(text)
        
    return text

def rmv_stopwords(text, stopword_list):
    if type(text) == str:
        chunk = nltk.word_tokenize(text)
    else:
        chunk = text
    new_chunk = []
    count = 0
    for word in chunk:
        if word not in stopword_list:
            new_chunk.append(word)
        else:
            count += 1
    return new_chunk, count

#returns type/token ratio without stopwords
def tt_ratio_no_stopwords(chunk):
    chunk = cleaner(chunk)
    chunk, stopword_count = rmv_stopwords(chunk.lower(), jockers_stopwords)
    types = len(set(chunk))
    if types == 0:
        return 0.0
    else:
        return [' '.join(chunk), types, len(chunk), stopword_count, types/len(chunk)]
    
    
def main():
    corpus = pd.read_excel('Turbulent flow_Stopwords Count.xlsx')
    corpus['types1'], corpus['token1'], corpus['stopword_count1'], corpus['tt_ratio_no_stop1'] = zip(*corpus.chunk.apply(tt_ratio_no_stopwords))
    corpus['types2'], corpus['token2'], corpus['stopword_count2'], corpus['tt_ratio_no_stop2'] = zip(*corpus.chunk2.apply(tt_ratio_no_stopwords))
    corpus.to_excel('Turbulent flow_tt ratio std stopwords.xlsx')
    print("saved")
    
def customized_test_case(characters = 1500, chunk_n = 300):
    corpus = pd.DataFrame({})
    for fname in glob.glob("/Users/dt/Documents/UChicago/Literature/2. Gender and verbs/data/archive/download/*"):
        with open(fname) as fn:
            text = fn.read()
            while text>characters and chunk_n:
                chunk,text = text[:characters],text[characters:]
                tmp = text.split(' ',1)
                chunk += tmp[0]
                text = tmp[1]
                corpus = corpus.append([[len(chunk)] + tt_ratio_no_stopwords(chunk)]) # fname.rsplit('/',1)[-1],
                chunk_n -= 1
    corpus.index = range(len(corpus))
    corpus.columns = [ 'chunk characters','chunk', 'types', 'token', 'stopword_count', 'tt_ratio_no_stop']
    corpus.to_excel('Out sample 3000-char chunk test.xlsx', encoding='utf8')
    
    print("saved")
    return corpus
    
if __name__ == "__main__":
    corpus = customized_test_case()
