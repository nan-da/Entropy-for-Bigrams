# -*- coding: utf-8 -*-

# Scrapy settings for archive project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'archive'

SPIDER_MODULES = ['archive.spiders']
NEWSPIDER_MODULE = 'archive.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'archive (+http://www.yourdomain.com)'
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 20
DOWNLOAD_DELAY = 0.5

DEFAULT_REQUEST_HEADERS = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
}


LOG_LEVEL = "CRITICAL"