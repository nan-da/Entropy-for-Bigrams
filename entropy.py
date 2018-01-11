#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 15:13:56 2017

@author: dt
"""

from resampling_type_token import cleaner, rmv_stopwords, read_stopwords
from collections import Counter
from math import log

stopword_list = read_stopwords('standard_stopwords_en.txt')
def text_entropy(fname = None, chunk = None, base = 2, asprob = True, rm_stop=False):
    """
    fname:  read file name and store in chunk
    chunk:  must provide at least one of fname and chunk
    asprob: return the transformation probability if True, 
            return entropy if False
    """
    if fname:
        with open(fname) as fn:
            chunk = fn.read()
    
    chunk = cleaner(chunk, tokenize=True)
    if rm_stop:
        chunk, _ = rmv_stopwords(chunk, stopword_list)
    
    open('cleaned.txt', 'w').write(' '.join(chunk))
    
    total_len = len(chunk) - 1
    
    transform_prob = Counter()
    for i, word in enumerate(chunk):
        if not i:
            pre = word
            continue
        transform_prob[(pre, word)] += 1
        pre = word
    
    if asprob:
        return transform_prob   
    
    log_n = log(total_len, base)
    entropy = sum([-x*(log(x,base) - log_n) for x in transform_prob.values()])
    
#    max_key = max(transform_prob, key=transform_prob.get)
#    print(max_key, transform_prob[max_key])

    return entropy/total_len


if __name__ == '__main__':
    text_entropy("scraper/archive/cleaned/0-Emmeline the Orphan of the Castle.txt", rm_stop=1)


