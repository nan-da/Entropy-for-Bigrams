#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 12:06:37 2017

@author: dt
"""

import pandas as pd
import numpy as np

store=pd.HDFStore('bigrams_full.h5')
result = pd.DataFrame({})
for key in store:
    df_all = store[key]
    raw_entropy = -sum(df_all.percentage*np.log(df_all.percentage))
    scaled_entropy = raw_entropy / np.log(len(df_all))
    result = result.append([[key, raw_entropy, scaled_entropy]])
    
result.columns = ['key', 'raw_entropy', 'scaled_entropy']
print(result)