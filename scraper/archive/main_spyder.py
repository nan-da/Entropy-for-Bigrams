"""
Created on Fri Mar 3 02:17:07 2017

To run this spider:
    1. cd scraper/archive/
    2. scrapy runspider main_spyder.py
    
Spyder version: 3.1.4
"""

from scrapy.spiders import Spider
from settings import *
from scrapy.http import FormRequest
import pandas as pd
from urllib.parse import quote
import scrapy
import re
from difflib import SequenceMatcher
import os
import glob
import shutil

url_root = 'https://archive.org'
bookdf =  pd.read_excel("../../Archive books_Entropy Scores.xlsx")
#bookdf =  pd.read_excel("../../Chadwyck Healey Canon List_bigrams.xlsx")

# In[ ]:
def preprocess_title(title):
    punct = r"""[,.;:"'?!*()/\\]"""
    for pattern in [r"In .{1,7} Volumes", r"\(.*\)",r"\[.*\]", r'[Bb]y .*', r"With .*Illustrations", r'A Novel', punct]:
        title = re.sub(pattern, '', title)
    title = title.strip()
    title = ' '.join(title.split()[:5])
    return title

bookdf.Title = bookdf.Title.apply(preprocess_title)
bookdf.Author = bookdf.Author.apply(preprocess_title)

# In[ ]:
def get_search_url(title, author=None):
    basic_title = url_root+'/details/texts?&and[]={}&and[]=mediatype%3A%22texts%22'.format(quote(title))
    if not author:
        return basic_title
    else:
        author = preprocess_title(author)
        add_name = '&and[]=creator%3A"{}"'.format(quote(author))
        return basic_title+add_name
    
bookdf['url'] = bookdf.apply(lambda x: get_search_url(x.Title, x.Author), axis=1)
bookdf['BOOK_ID'] = bookdf.index.astype(str)
bookdf.to_csv('metadata Archive books_Entropy Scores.csv',index=0)


# In[ ]:
def clear_old_file(path):
    file_list = list(glob.glob(path+'*'))
    if file_list:
        input("Enter to confirm removing any old file in "+path)
        #shutil.rmtree(path)
        for fn in file_list:
            os.remove(fn)
        print('remove',path)

clear_old_file("download/")    

# In[ ]:
def is_not_volume(x):
    if len(x)<4 or re.match(r'^Vol 1-\d+:', x):
        return True
    elif x[:4]=='Vol ':
        return False
    else:
        return True

# In[ ]:
f_error = open('1_Errors.csv','w')
f_success = open('0_Search_results.csv','w')
f_success.write('index,bid,title,url,view,author,True title,similarity,isnotVol,status,used \n')


# In[ ]:
class archiveSpider(Spider):
    name = 'archive'
    
    def start_requests(self):            
        for index, x in bookdf.iterrows():
            request = scrapy.Request(x.url, meta={'info': x}, callback = self.parse, headers=DEFAULT_REQUEST_HEADERS, errback=self.errback_record)
            yield request

    def parse(self, response): #search page
        bid, real_title, real_author = response.meta['info'][['BOOK_ID','Title','Author']]
        divs = response.xpath("//div[@class='item-ia']")
        result_df = pd.DataFrame({})

        for div in divs:
            title = div.xpath(".//div[@class='C234']/div/a/div[@class='ttl']/text()").extract()
            title = title[0].strip() if title else ''
            url = div.xpath(".//div[@class='C234']/div/a/@href").extract()
            url = url[0] if url else ''
            view  = div.xpath(".//div[@class='statbar']/h6/nobr/text()").extract()
            view  = int(view[0].replace(',','')) if view else ''
            author = div.xpath(".//div[@class='C234']/div[@class='by C C4']/span[2]/text()").extract()
            author = author[0] if author else ''
            row = [[bid,title, url, view, author]]
            result_df = result_df.append(pd.DataFrame(row, columns=['bid','title', 'url', 'view', 'author']), ignore_index=True)
        
        if len(result_df):
            result_df['similarity'] = result_df.title.apply(lambda x: SequenceMatcher(None, x,response.meta['info']['Title']).ratio())
            result_df.drop(result_df[result_df.similarity<0.3].index, inplace=1)
            result_df['True title'] = real_title
            result_df['isnotVol'] = result_df.title.apply(is_not_volume)
        
        
        print("BID:{}, result_df num:{}".format(bid, len(result_df)))
        if not len(result_df):
            new_request = self.level1_cut_title_and_search(response)
            if new_request:
                yield new_request
            return
        
        for request in self.level2_select_top_from_search(response.meta['info'], result_df):
            yield request
            
        result_df.to_csv('0_Search_results.csv',mode='a',header=False)
            
    def level1_cut_title_and_search(self, response):
        bid, real_title, real_author = response.meta['info'][['BOOK_ID','Title','Author']]
        if real_author.find(' ')!=-1:
            real_author = real_author.rsplit(maxsplit=1)[0]
            request = scrapy.Request(get_search_url(real_title, real_author), meta={'info': response.meta['info']}, callback = self.parse, headers=DEFAULT_REQUEST_HEADERS, errback=self.errback_record)
            request.meta['info']['Author'] = real_author
            return request
            
        elif real_title.find(' ')!=-1:
            real_title = real_title.rsplit(maxsplit=1)[0]
            request = scrapy.Request(get_search_url(real_title), meta={'info': response.meta['info']}, callback = self.parse, headers=DEFAULT_REQUEST_HEADERS, errback=self.errback_record)
            response.meta['info']['Title'] = real_title
            return request
        
        else:
            self.errback_to_csv(response, "Level 1 error: No search result")
        return 
        
    def level2_select_top_from_search(self, info, result_df):
        if sum(result_df.isnotVol):
            print('OK!')
            index = [result_df[result_df.isnotVol].sort('similarity',ascending=0).index[0]] # view or similarity?
            result_df['status'] = 'Normal'
        else:
            print('The book is seperated into Vols.')
            index = result_df[result_df.similarity==result_df.groupby('similarity').count().sort_values('url').index[0]].index
            result_df['status'] = 'Seperate into Volumes'
#            print(result_df.groupby('similarity').count().reset_index().sort('url'))
        result_df.loc[index, 'used'] = 1
        
        for k, row in result_df.loc[index, :].iterrows():
            request = scrapy.Request(url = url_root + row.url, meta={'info': info}, callback=self.parse_page2, headers=DEFAULT_REQUEST_HEADERS, errback=self.errback_record)
            request.meta['alternative'] = result_df[~result_df.index.isin(index)]
            yield request

    def parse_page2(self, response): #click one item in search page
        url_2s = response.xpath("//div[@class='boxy quick-down']/div/a/@href").extract()
        url_2 = list(filter(lambda x: len(x)>4 and x[-4:]=='.txt', url_2s))
        if not url_2:
            url_2s = response.xpath("//div[@class='boxy quick-down']/div/div/div/a/@href").extract()
            url_2 = list(filter(lambda x: len(x)>4 and x[-4:]=='.txt', url_2s))
            if not url_2:
                if len(response.meta['alternative']):
                    print("using alternative")
                    for request in self.level2_select_top_from_search(response.meta['info'], response.meta['alternative']):
                        yield request
                else:
                    new_request = self.level1_cut_title_and_search(response)
                    if new_request:
                        yield new_request
                    else:
                        self.errback_to_csv(response, "Level 2 error: No txt found")
                return 
                    
        request = scrapy.Request(url = url_root + url_2[0], meta={'info': response.meta['info']}, callback=self.parse_page3, headers=DEFAULT_REQUEST_HEADERS)
        yield request

    def parse_page3(self, response): #text detail
        try:
            text = '\n'.join(response.xpath("//div[@class='container container-ia']/pre/text()").extract())
            if not text:
                if type(response.body) == bytes:
                    text = response.body.decode("utf-8", "ignore")
                else:
                    text = response.body
            print('saved', response.meta['info']['BOOK_ID'])
            open('download/{}.txt'.format('-'.join(response.meta['info'][['BOOK_ID','Title']].tolist())),'a+').write(text) # a+ for some books are seperated into volumes
        except Exception as e:
            self.errback_to_csv(response, "Level 3 error: "+str(e))
        
    def errback_to_csv(self, response, err_msg):
        meta_list = response.meta['info'][['BOOK_ID','Title','Author']].tolist()
        f_error.write('"'+'","'.join(meta_list + [response.url,err_msg])+'"\n')
        print()
        print(response.meta['info']['BOOK_ID'], response.url)
        print(err_msg)
        print()

    def errback_record(self, failure):
        print(dir(failure))
        self.logger.error(repr(failure))
        