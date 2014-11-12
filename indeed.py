import re
import requests
from bs4 import BeautifulSoup
import json
import csv
import itertools

print
directory = raw_input('what directory? ')
print
what = raw_input('what: ')
print 
where = raw_input('where: ')
print 

def try_int(x):
    try:
        return int(x)
    except ValueError:
        pass
    
def writeCsv():
    csvList.append([firmName,jobTitle,jobCity,jobState,number])
    with open(directory+'/'+what.upper()+where+'.csv','w') as f:
        writer = csv.writer(f,delimiter=',',quoting=csv.QUOTE_ALL)
        [writer.writerow(row) for row in csvList]
        
getInfo = lambda x,y,z: item.find_all(x,{y:z})[0].text.encode('utf-8').strip()

regNum = re.compile(r'[0-9]{3}-[0-9]{4}')
altRegNum = re.compile(r'.[0-9]{3}. ?[0-9]{3}-[0-9]{4}|[0-9]{3}[-\.][0-9]{3}[-\.][0-9]{4}')

url = 'http://www.indeed.com/search?q='+what+'&l='+where+'&r=directhire'
r = requests.get(url)
soup = BeautifulSoup(r.content)
limit = soup.find_all(id='searchCount')[0].text.encode('utf-8').split()
limit = [re.sub(',','',str(x)) for x in limit]
limit = [try_int(x) for x in limit] 
searchLimit = 1001 if limit[5] >= 1000 else limit[5]+10

i = 0
testList = []
csvList = []
while i<10: # change to searchLimit when not testing
    try:
        url = 'http://www.indeed.com/search?q='+what+'&l='+where+'&r=directhire&start='+str(i)
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        gData = soup.find_all('div',{'class':'row'})
        for item in gData:
            try:
                firmInfo = [getInfo('span','class','company'),
                            getInfo('a','target','_blank'),
                            getInfo('span','class','location')]
                firmName,jobTitle,jobCityState = firmInfo
                jobCityState = re.sub('[0-9]*','',jobCityState).strip()
                jobCityState = re.sub('\(.*\)','',jobCityState).strip()
                jobCity = jobCityState[0:-4].encode('utf-8')
                jobState = jobCityState[-2:].encode('utf-8')
                jobCityPlus = re.sub(', ','+',jobCity)
                firmNamePlus = re.sub("\'",'',firmName)
                firmNamePlus = re.sub('\W','+',firmName)+'+'
                bingSearch = 'http://www.bing.com/search?q='+firmNamePlus+jobCity+'+'+jobState # try just jobCityState and compare     
                info = requests.get(bingSearch)
                moreSoup = BeautifulSoup(info.content)
                contactData = moreSoup.find_all('div',{'class':"b_factrow"})
                altContactData = moreSoup.find_all('div',{'class':'b_imagePair tall_xb'})
                altaltContactData = moreSoup.find_all('ul',{'class':'b_vList'})
                testList.append([firmName,jobTitle,jobCity,jobState])
                for z in altContactData:
                    if re.search(altRegNum,z.text):
                        if len(z)>1:
                            number = re.findall(altRegNum,z.text)[0]
                            # print firmName,jobTitle,jobCity,jobState,number
                            writeCsv()
                        else:
                            number = re.findall(altRegNum,z.text)[0]
                            # print firmName,jobTitle,jobCity,jobState,number
                            writeCsv()
                for q in altaltContactData:
                    if not contactData:
                        if re.search(regNum,q.text):
                            number = re.findall(altRegNum,q.text)[0]
                            # print firmName,jobTitle,jobCity,jobState,number
                            writeCsv()
                for num in moreSoup:
                    if not contactData:
                        if not altContactData:
                            number = re.findall(altRegNum,moreSoup.text)[0]
                            # print firmName,jobTitle,jobCity,jobState,number
                            writeCsv()
                for this in contactData:
                    if re.search(regNum,this.text):
                        number = re.findall(regNum,this.text)[0]
                        # print firmName,jobTitle,jobCity,jobState,number
                        writeCsv()
            except:
                pass
    except Exception as e:
        print e
        pass
    i+=10
print

newList = [list(x[0:2]) for x in csvList]
noReps = [x for x,_ in itertools.groupby(newList)]

if limit[5]>=1000:
    scrapeRate = float(len(noReps))/searchLimit*100

else:
    scrapeRate = float(len(noReps))/(limit[5]-10)*100
    
scrapeRate = '%.3f'%round(scrapeRate,3)

print 'SCRAPE RATES:'
print
stats = str(scrapeRate)+'% scrape rate'
print stats,'-- Actual'

testStats = '%.3f'%round(float(len(noReps))/len(testList)*100)
print str(testStats)+'% scrape rate -- Test'
print

nonScraped = []
newList = [i[0:2] for i in csvList]
print 'NON-SCRAPED DATA'
print
for x in testList:
    if x[0:2] not in newList:
        nonScraped.append([x])
        # print x
    else:
        pass
print 
print len(nonScraped), 'out of', len(noReps)
print

print what.upper()+where+'.csv','is ready in',directory
print
