#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 10:39:28 2017

@author: dt
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

store=pd.HDFStore('bigrams_full.h5')
for key in store:
    df_all = store[key][['bigram','percentage']]
    df = df_all[:1000]
    df.index = range(1, len(df)+1)
    fig = plt.figure()
    plt.xlabel('nth bigram')
    plt.ylabel('probability distribution')
    plt.grid(True)
    ax=plt.gca() 
    df.plot(ax=ax,loglog=True,style='.',grid=True)
    
    slope, intercept, r_value, p_value, std_err = linregress(np.log10(df.index), np.log10(df.percentage))
    xfix = np.logspace(0, 3, base=10)
    linear_df = pd.DataFrame({'fitted': np.power(10, intercept)*(df.index)**slope},index=df.index)
    linear_df.plot(ax=ax)
    print('y={}*x+{}'.format(slope, intercept))
    
    
    fig=plt.figure()
    plt.xlabel('nth bigram')
    plt.ylabel('probability distribution')
    df.plot()
    