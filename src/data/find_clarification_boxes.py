#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 18:30:17 2019

@author: isoamylacetate
"""

#internal modules
import sys
import re

#external modules
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

#my modules
#sys.path.append('./src/data')
import xpaths

def parse_yt_num(s:str) -> int:
    m = re.search('^([0-9]+)', s)
    if m is None:
        return None
    elif len(m.groups()) == 1:
        return int(m.group(1).replace(',', ''))
    else:
        return None
        

def get_video_data(url: str, browser):
    wait = WebDriverWait(browser, 10)
    
    
    browser.get(url)
    
    def get_xpath(xpath: str):
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    
    ret = dict()
    
    #get video title
    ret['title'] = get_xpath(xpaths.VIDEO_TITLE).text
    
    #get view count
    
    
    #get n likes, dislikes
    temp = get_xpath(xpaths.VIDEO_LIKES).get_attribute('aria-label')
    ret['likes'] = parse_yt_num(temp)
    
    return ret

#b = webdriver.PhantomJS()
#browser.get('https://www.youtube.com/watch?v=X7Nk3W-2egk')

#dat = get_video_data('https://www.youtube.com/watch?v=X7Nk3W-2egk', b)

#browser.close()
