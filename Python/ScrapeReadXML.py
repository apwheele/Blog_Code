#My attempt to see if RSS feeds were dead
#Takes an exported reader xml file
#see https://www.dropbox.com/s/lef6lodeqp483n5/digg_reader_subscriptions.xml?dl=0
#For an example file

#This takes an exported XML feed and identifies the most recent date a post was made
from bs4 import BeautifulSoup
import urllib2
from urllib2 import URLError
from datetime import datetime
import email.utils
import time
import pandas as pd

#Directory where you file is at
MyDir = r'C:\Users\axw161530\Dropbox\Documents\BLOG\ReaderXML'

###########
#Get XML file, scrape the website RSS feed

MyFeed = open(MyDir + r'\digg_reader_subscriptions.xml')
textFeed = MyFeed.read()
print textFeed[0:100]

#Parsing it using BeautifulSoup
FeedParse = BeautifulSoup(textFeed, 'xml')
MyFeed.close()

#Making a structured list of tuples to grab the feed urls
subLi = []
fold = ''
for i in FeedParse.find_all('outline'):
    if i.get('type') is None:
        fold = i.get('title')
    else:
        x = (fold,i.get('text'),i.get('xmlUrl'))
        subLi.append(x)

#print subLi[0:3]

###########
#BeautifulSoup, grab the most recent date for all of my feeds

def MostRecPub(feed_url):
    time.sleep(2) #waits a few seconds
    try:
        r = urllib2.urlopen(feed_url)
    except URLError, e:
        return ('Url Error', 0)
    parseUrl = BeautifulSoup(r, 'xml')
    dates = parseUrl.find_all('pubDate')
    datesAlt = parseUrl.find_all('published')
    datesAlt2 = parseUrl.find_all('date')
    datesAlt3 = parseUrl.find_all('updated')
    dT = []
    if len(dates) != 0:
        for i in dates:
            stD = i.get_text()
            DP = email.utils.parsedate(stD)
            dN = time.mktime(DP) #datetime.fromtimestamp(dN)
            dT.append((stD,dN))
        sL = sorted(dT, key=lambda tup: tup[1])
        return sL[0]
    elif len(datesAlt) != 0:
        for i in datesAlt:
            stD = i.get_text()
            DP = datetime.strptime(stD[0:19],'%Y-%m-%dT%H:%M:%S') #ignores offset
            dN = time.mktime(DP.timetuple())
            dT.append((stD,dN))
        sL = sorted(dT, reverse=True, key=lambda tup: tup[1])
        return sL[0]
    elif len(datesAlt2) != 0:
        for i in datesAlt2:
            stD = i.get_text()
            DP = datetime.strptime(stD[0:19],'%Y-%m-%dT%H:%M:%S') #ignores offset
            dN = time.mktime(DP.timetuple())
            dT.append((stD,dN))
        sL = sorted(dT, reverse=True, key=lambda tup: tup[1])
        return sL[0]
    elif len(datesAlt3) != 0:
        for i in datesAlt3:
            stD = i.get_text()
            DP = datetime.strptime(stD[0:19],'%Y-%m-%dT%H:%M:%S') #ignores offset
            dN = time.mktime(DP.timetuple())
            dT.append((stD,dN))
        sL = sorted(dT, reverse=True, key=lambda tup: tup[1])
        return sL[0]
    else:
        return ('No Date Parsed',0)


#Saving the results to a set of data
resDates = []

#Takes a bit
for i in subLi:
    res = MostRecPub(i[2])
    #convert res[1] to a year-date
    if res[1] != 0:
        dTRes = datetime.fromtimestamp(res[1])
        niceD = dTRes.strftime('%m-%d-%Y')
    else:
        niceD = 'Missing'
    resDates.append((i[0],i[1],i[2],res[0],res[1],niceD))
    #print (i[0],i[1],i[2],res[0],res[1],niceD)

#print MostRecPub(subLi[9][2])

#rT = urllib2.urlopen(subLi[33][2])
#parseTUrl = BeautifulSoup(rT, 'xml')
#print parseTUrl.find_all('updated')
#for i in parseTUrl.find_all('updated'):
#    print i.get_text()

#Drew Conway, search for time tag, view-source:http://drewconway.com/zia/?feed=rss2


#exporting to a csv file via pandas
df = pd.DataFrame(resDates, columns=['Folder','FeedTitle','FeedUrl','LastDateStr','TimeStamp','NiceDate'])
#df.to_csv(MyDir + r'\Results.csv')

