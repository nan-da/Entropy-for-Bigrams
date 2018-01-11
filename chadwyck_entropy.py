#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 20:02:07 2017

"""
# In[1]:
import glob
import re
from tqdm import tqdm
from entropy import text_entropy
import pandas as pd
from collections import Counter
import os
import numpy as np

pat_gut_start = re.compile(r'.*START OF.{0,5} PROJECT GUTENBERG EBOOK.*?\*\*\*',re.DOTALL)
produce_by = re.compile(r'Produced by .*?\n', re.IGNORECASE)
pat_google_start = re.compile(r"This is a digital copy.*?the full text of this book on the web",re.DOTALL)
pat_gut_end = re.compile(r'End of .*?Project Gutenberg.*', re.IGNORECASE | re.DOTALL)
google_url = re.compile(r".*http: //books \.google \.com/I",re.DOTALL)
google_url_2 = re.compile(r".*at \|http : //books \. google \. com/",re.DOTALL)
gut_start_print = re.compile(r'.*\*END\*.*\*END\*', re.DOTALL)
gut_start_any = re.compile(".*Project Gutenberg", re.IGNORECASE | re.DOTALL)
gut_end_any = re.compile("Project Gutenberg.*", re.IGNORECASE | re.DOTALL)
digitize_by_google = re.compile(r'Digitized by Google', re.IGNORECASE )

start_pattern = [pat_gut_start, produce_by, gut_start_print,gut_start_any,pat_google_start, google_url, google_url_2]
end_pattern = [pat_gut_end, gut_end_any]

result_df = pd.DataFrame({})


def preprocessing(in_path, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    for fn in tqdm(glob.glob(in_path)):
        fn_short = fn.replace('.txt','').split('-')[1]
        if len(fn_short.split())<5:
            continue
        
        text = open(fn, 'r').readlines()
        
        head = ' '.join(text[:300])
        for pattern in start_pattern:
            head = pattern.sub('',head)
        text = [head] + text[300:]
    
        end = ' '.join(text[-500:])
        for pattern in end_pattern:
            end = pattern.sub('',end)
            
        text = text[:-500] + [end]
        
        text = ' '.join(text)
        text = digitize_by_google.sub('',text)
        fn = fn.rsplit('/',maxsplit=1)[-1]
        open(out_path+fn, 'w').write(text)

preprocessing("scraper/archive/download/*", "scraper/archive/cleaned/")

# In[2]:
def corpus_top_bigram(in_folder, out_path=None, rm_stop=True, top=None, single_work=False):
    
    total_bigram = Counter()
    works_df = pd.DataFrame({})
    for fn in tqdm(list(glob.glob(in_folder))):
        work_bigram = text_entropy(fname = fn, asprob = True, rm_stop=rm_stop)
        if single_work:
            works_df = works_df.append([[fn.split('/')[-1], len(work_bigram), sum(work_bigram.values())]])
        else:
            total_bigram += work_bigram
        
    works_df.columns = ['title','distinct','total']
    if single_work:
        return works_df
        
    if not top:
        common = total_bigram.most_common()
    else:
        common = total_bigram.most_common()[:top]
    result_bigram = pd.DataFrame(common, columns=['bigram','count'])
    result_bigram['percentage'] = result_bigram['count']/sum(total_bigram.values())
    entropy = -sum(result_bigram.percentage * np.log(result_bigram.percentage) / np.log(len(result_bigram)))
    if out_path:
        if out_path[-2:] == 'h5':
            result_bigram.to_hdf(out_path, key=in_folder.replace('*',''), mode='a', append=False, complib='zlib')
        elif out_path[-3:] == 'csv':
            result_bigram.to_csv(out_path)
        else:
            raise NameError("Unexpected suffix")
    
    print("Entropy: ", entropy)
    return result_bigram, entropy

chadwyck = corpus_top_bigram("scraper/Chadwyck Healey Canon/cleaned/*", single_work=True, rm_stop=False)
archive = corpus_top_bigram("scraper/archive/cleaned/*", single_work=True, rm_stop=False)

corpus_top_bigram("scraper/Chadwyck Healey Canon/cleaned/*",'top_bigram_no_stopword Chadwyck.csv', rm_stop=True)
corpus_top_bigram("scraper/Chadwyck Healey Canon/cleaned/*",'top_bigram_with_stopword Chadwyck.csv', rm_stop=False)


# In[3]:

def KL_Divergence(p_path, q_path, normalize = False):
    """
    normalize: change the log base to length of P
    """
    chadwyck, entropy_chadwyck = corpus_top_bigram(p_path, 'bigrams_full.h5', rm_stop=False, top=None)
    archive, entropy_archive = corpus_top_bigram(q_path, 'bigrams_full.h5', rm_stop=False, top=None)
    store = pd.HDFStore("bigrams_full.h5")
    chadwyck = store[p_path[:-2]]
    archive = store[q_path[:-2]]
    chadwyck['rank'] = chadwyck['count'].rank(ascending=False)
    archive['rank'] = archive['count'].rank(ascending=False)
    m = chadwyck.merge(archive, 'inner', on='bigram')
    
    threshold = 0
    m = m[(m.count_x>threshold)]
    
    m['diff']=m.percentage_x / m.percentage_y
    m['div']=np.log(m['diff'])*m['percentage_x']
    m['count'] = (m.count_x+m.count_y)/2
    m = m.sort_values('count',ascending=False)
    m['group'] = (m.index / (len(m)/10)).astype(int)
    print(m.groupby('group').mean()[['div','count']])
    
    kl_div = sum(m['div'])
    
    if normalize:
        kl_div /= np.log(len(chadwyck))
    print("KL Divergence:", kl_div)
    if threshold:
        print('With threshold:', threshold)
    return m
    
m = KL_Divergence("scraper/Chadwyck Healey Canon/cleaned/*", "scraper/archive/cleaned/*")
#KL_Divergence("scraper/archive/cleaned/*", "scraper/Chadwyck Healey Canon/cleaned/*", normalize=True)
print(m)

#sum of bigrams: 
#     chadwyck: 35149397
#     archive : 49096879
