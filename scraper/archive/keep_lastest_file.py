#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 04:35:44 2017

@author: dt
"""

import os
import platform
import glob

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
        
if __name__ == '__main__':
    print('Keep lastest file called!')
    bid_pre = ''
    fn_pre = ''
    for fn in glob.glob('download/*.txt'):
        print(fn)
        bid = fn.split('/')[1].split('-')[0]
        if bid == bid_pre:
            if fn_pre and creation_date(fn)>creation_date(fn_pre):
                rm_name = fn_pre
            else:
                rm_name = fn            
            os.remove(rm_name)
            print('remove',rm_name)
            
        bid_pre = bid
        fn_pre = fn