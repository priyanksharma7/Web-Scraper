
# coding: utf-8

# In[1]:


import requests
import bs4
from datetime import datetime
import re
import os
import urllib
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import numpy as np
import pandas as pd

from pandas import Series, DataFrame

initialpage = 'https://www.boxofficemojo.com/yearly/chart/?yr=2017&p=.htm'
res = requests.get(initialpage, timeout=None)
soup = bs4.BeautifulSoup(res.text, 'html.parser')


# In[2]:


pages = []
pagelinks=soup.select('a[href^="/yearly/chart/?page"]')

for i in range(int(len(pagelinks)/2)):
    pages.append(str(pagelinks[i])[9:-14])
    pages[i]=pages[i].replace("amp;","")
    pages[i]= "https://www.boxofficemojo.com" + pages[i]
    pages[i]=pages[i][:-1]
       
        
pages.insert(0, initialpage)
date_dic = {}
movie_links = []
no_of_movies = 0
theater_count = []


for i in range(int(len(pagelinks)/2 + 1)): 
    movie_count=0;
    res1 = requests.get(pages[i])
    souppage=bs4.BeautifulSoup(res1.text, 'html.parser')
    for j in souppage.select('tr > td > b > font > a'):
        link = j.get("href")[7:].split("&")
        str1 = "".join(link)
        final = "https://www.boxofficemojo.com/movies" + str1
        if "/?id" in final: 
            movie_links.append(final)
            movie_count += 1
            no_of_movies += 1
            
    number_of_theaters=souppage.find("tr", bgcolor="#dcdcdc")
    for k in range(movie_count):
        if k!=565:
            theater_count.append(number_of_theaters.next_sibling.contents[4].text)
            number_of_theaters=number_of_theaters.next_sibling
print (no_of_movies)


# In[3]:


np.random.seed(25)
DF_obj = DataFrame(np.random.rand(no_of_movies * 8).reshape((no_of_movies,8)), index=movie_links, columns=['Domestic gross total','Genre','Release Date', 'Production budget', 'Number of Theaters','Number of views', 'Number of editors', 'Number of edits'])
DF_obj = DF_obj.rename_axis('Titles')


# In[4]:


path = os.getcwd()  
path = path + '/movie_pictures'
os.makedirs(path)
os.chdir(path)

titles = []
k=0
while(k < len(movie_links)):
    j = movie_links[k]
    try:
        res1 = requests.get(j)
        soup1 = bs4.BeautifulSoup(res1.text, 'html.parser')
    
        c = soup1.select('td[width="35%"]')
        d=soup1.select('div[class="mp_box_content"]')
   
        genre = soup1.select('td[valign="top"]')[5].select('b')
        image = soup1.select('img')[6].get('src')
        budget = soup1.select('tr > td > b')
        domestic = str(c[0].select('b'))[4:-5]
        release = soup1.nobr.a
        title = soup1.select('title')[0].getText()[:-25]
        
        print ("-----------------------------------------")
        print ("Title: " +title)
        print ("Domestic Total Gross: " +domestic)
        print ("Genre: "+genre[0].getText())
        print ("Release Date: " +release.contents[0])
        print ("Production Budget: " +budget[5].getText())
        
        DF_obj = DF_obj.rename({str(movie_links[k]): title})
        DF_obj.ix[k, 0] = domestic
        DF_obj.ix[k, 1] = genre[0].getText()
        DF_obj.ix[k, 2] = release.contents[0]
        DF_obj.ix[k, 3] = budget[5].getText()
        DF_obj.ix[k, 4] = theater_count[k]
        
        titles.append(title)
        
        year1=str(release.contents[0])[-4:]
        a,b=str(release.contents[0]).split(",")
        month1, day1=a.split(" ")
        datez= year1 + month1 + day1
        new_date= datetime.strptime(datez , "%Y%B%d")
        date_dic[title]=new_date       
    
    
        with open('pic' + str(k) + '.jpg', 'wb') as handle:
            response = requests.get(image, stream=True)
        
            if not response.ok:
                print response

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
    except:
        print("Error Occured, Page Or Data Not Available")
    k+=1


# In[5]:


def subtract_one_month(t):

    import datetime
    one_day = datetime.timedelta(days=1)
    one_month_earlier = t - one_day
    while one_month_earlier.month == t.month or one_month_earlier.day > t.day:
        one_month_earlier -= one_day
    year=str(one_month_earlier)[:4]

    day=str(one_month_earlier)[8:10]
   
    month=str(one_month_earlier)[5:7]

    newdate= year + "-" + month +"-" + day
 
    return newdate


# In[6]:


number_of_errors=0
browser = webdriver.Chrome("/Users/Gokce/Downloads/chromedriver")
browser.maximize_window() 
browser.implicitly_wait(20)

k=-1
for i in titles:
    k += 1
    try:
        release_date = date_dic[i]
        i = i.replace(' ', '_')
        i = i.replace("2017", "2017_film")
    #end = datetime.strptime(release_date, '%B %d, %Y')


        end_date = release_date.strftime('%Y-%m-%d')
        start_date = subtract_one_month(release_date)
        url = "https://tools.wmflabs.org/pageviews/?project=en.wikipedia.org&platform=all-access&agent=user&start="+ start_date +"&end="+ end_date + "&pages=" + i

    
        browser.get(url)
        page_views_count = browser.find_element_by_css_selector(" .summary-column--container .legend-block--pageviews .linear-legend--counts:first-child span.pull-right ")
        page_edits_count = browser.find_element_by_css_selector(" .summary-column--container .legend-block--revisions .linear-legend--counts:first-child span.pull-right ")
        page_editors_count = browser.find_element_by_css_selector(" .summary-column--container .legend-block--revisions .legend-block--body .linear-legend--counts:nth-child(2) span.pull-right ")
        print (i)
    
        print ("Number of Page Views: " +page_views_count.text)
        print ("Number of Edits: " +page_edits_count.text)
        print ("Number of Editors: " +page_editors_count.text)
        
        DF_obj.ix[k, 5] = page_views_count.text
        DF_obj.ix[k, 6] = page_editors_count.text
        DF_obj.ix[k, 7] = page_edits_count.text
        
    except:
        print("Error Occured for this page: " + str(i))
        number_of_errors += 1
    
#.text
time.sleep(5)
browser.quit()


# In[7]:


DF_obj


# In[8]:


DF_obj[DF_obj<1]=np.nan


# In[9]:


DF_obj.to_csv('Final_output5.txt', sep="\t", encoding='utf-8')

