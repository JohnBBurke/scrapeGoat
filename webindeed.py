from flask import request, make_response, session
import flask, flask.views
from datetime import timedelta
from bs4 import BeautifulSoup
from os.path import expanduser
import os
import csv
import re
import io
import sys
import itertools
import requests

{
    "detect_indentation": False
}

app = flask.Flask(__name__)
app.secret_key = os.urandom(32)

home = expanduser("~")
desktop = home+'/Desktop'
desktopCheck = os.path.isdir(home+"/Desktop")
directory = desktop if desktopCheck is True else home   


class View(flask.views.MethodView):

    def get(self):
        return flask.render_template('index.html')

    @app.route('/download')
    def post(self):

        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=45)

        what = flask.request.form['what']
        where = flask.request.form['where']
        jobType = flask.request.form['jt']
        salary = flask.request.form['salary']
        fromage = flask.request.form['fromage']
        regNum = re.compile(r'[0-9]{3}-[0-9]{4}')
        altRegNum = re.compile(r'.[0-9]{3}. ?[0-9]{3}-[0-9]{4}|[0-9]{3}[-\.][0-9]{3}[-\.][0-9]{4}')

        def writeCsv():
            if not number:
                pass
            else:
                csvList.append([firmName,jobTitle,jobCity,jobState,number,names,bingNameSearch]) 
                # with open(directory+'/'+what.upper()+where+'.csv','w') as f:
                #     writer = csv.writer(f,delimiter=',',quoting=csv.QUOTE_ALL)
                #     writer.writerow(['FIRM NAME','JOB TITLE','JOB CITY','JOB STATE','NUMBER','NAMES FROM LINKEDIN','URL FOR LINKEDIN DATA'])
                #     [writer.writerow(row) for row in csvList]
        getInfo = lambda x,y,z: item.find_all(x,{y:z})[0].text.encode('utf-8').strip()
        intgr = lambda x: int(x) if x.isdigit() else x

        url = 'http://www.indeed.com/search?q='+what+'&l='+where+'&sr=directhire'+'&as_any=&ttl=&jt='+jobType+'&salary='+salary+'&fromage='+fromage
        r = requests.get(url)
        soup = BeautifulSoup(r.content)

        try:
            limit = soup.find_all(id='searchCount')[0].text.encode('utf-8').split()
        except:
            flask.flash("INDEED.COM RETURNED NO RESULTS!\n\nPlease try Again.\n\n")
            return self.get()

        limit = [re.sub(',','',str(x)) for x in limit]
        limit = [intgr(x) for x in limit]
        searchLimit = 1001 if limit[5] >= 1000 else limit[5]+10

        i = 0
        testList = []
        csvList = []
        while i<10:
            try:
                url = 'http://www.indeed.com/search?q='+what+'&l='+where+'&sr=directhire'+'&as_any=&ttl=&jt='+jobType+'&salary='+salary+'&fromage='+fromage+'&start='+str(i)
                r = requests.get(url)
                soup = BeautifulSoup(r.content)
                gData = soup.find_all('div',{'class':'row'})
                for item in gData:
                    try:
                        firmInfo = [getInfo('span','class','company'),
                                    getInfo('a','target','_blank'),
                                    getInfo('span','class','location')]
                        firmName,jobTitle,jobCityState = firmInfo
                        if jobCityState != 'United States':
                            jobCityState = re.sub('[0-9]*','',jobCityState).strip()
                            jobCityState = re.sub('\(.*\)','',jobCityState).strip()
                            jobCity = jobCityState[0:-4].encode('utf-8')
                            jobState = jobCityState[-2:].encode('utf-8')
                            jobCityPlus = re.sub(', ','+',jobCity)
                        else:
                            jobCity = 'United States'
                            jobState = ''
                        firmNamePlus = re.sub("\'",'',firmName)
                        firmNamePlus = re.sub('\W','+',firmName)+'+'
                        bingSearch = 'http://www.bing.com/search?q='+firmNamePlus+jobCity+'+'+jobState     
                        info = requests.get(bingSearch)
                        moreSoup = BeautifulSoup(info.content)
                        contactData = moreSoup.find_all('div',{'class':"b_factrow"})
                        altContactData = moreSoup.find_all('div',{'class':'b_imagePair tall_xb'})
                        altaltContactData = moreSoup.find_all('ul',{'class':'b_vList'})
                        testList.append([firmName,jobTitle,jobCity,jobState])
                        # creates short link for each job posting
                        # for link in item('a',href=re.compile('^/rc/clk\?jk=|^.*clk\?|^.*\?r=1')):
                            # source = 'http://www.indeed.com'+link.get('href')
                        #     post_url = 'https://www.googleapis.com/urlshortener/v1/url'
                        #     payload = {'longUrl': source}
                        #     headers = {'content-type':'application/json'}
                        #     r = requests.post(post_url, data=json.dumps(payload), headers=headers)
                        #     text = r.content
                        #     site = str(json.loads(text)['id'])
                        bingNameSearch = 'https://www.bing.com/search?q='+firmNamePlus+jobCity+'+'+jobState+'%20name%20site%3Alinkedin.com'
                        nameReq = requests.get(bingNameSearch)
                        nameSoup = BeautifulSoup(nameReq.content)
                        namesList = []
                        for n in nameSoup.find_all('li',{'class':'b_algo'}):
                            if re.search('^.* \|.*LinkedIn',n.text):
                                name = re.findall('^(.*) \|',n.text)[-1][0:-1].encode('utf-8').title()
                                namesList.append(name)
                                names = str(namesList)
                                names = re.sub('(\')',' ',str(names))
                                names = names.translate(None,'\[\]').strip()
                                print name
                        for this in contactData:
                            if re.search(regNum,this.text):
                                number = re.findall(altRegNum,this.text)[0].encode('utf-8')
                                writeCsv()
                        for z in altContactData:
                            if not contactData:
                                if re.search(altRegNum,z.text):
                                    number = re.findall(altRegNum,z.text)[0].encode('utf-8')
                                    writeCsv()
                        for q in altaltContactData:
                            if not contactData:
                                if not altContactData:
                                    if re.search(regNum,q.text):
                                        number = re.findall(altRegNum,q.text)[0].encode('utf-8')
                                        writeCsv()
                        for num in moreSoup:
                            if not contactData:
                                if not altContactData:
                                    if not altaltContactData:
                                        if re.search(altRegNum,moreSoup.text):
                                            number = re.findall(altRegNum,moreSoup.text)
                                            for p in number:
                                                number = p.encode('utf-8')
                                            writeCsv()
                                        else:
                                            number = re.findall(altRegNum,str(num))
                                            for z in number:
                                                number = z.encode('utf-8')
                                            writeCsv()
                    except:
                        pass
            except Exception as e:
                print e
                pass
            i+=10

        si = io.BytesIO()
        cw = csv.writer(si)
        [cw.writerow(row) for row in csvList]
        output = make_response("Firm Name,Job Title,Job City,Job State,Number,Names,URL to LinkedIn Data"+'\n'+si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename="+what.upper()+where+".csv"
        output.headers["Content-type"] = "text/csv"

        newList = [list(x[0:2]) for x in csvList]
        noReps = [x for x,_ in itertools.groupby(newList)]

        if limit[5]>=1000:
            scrapeRate = float(len(noReps))/len(testList)*100

        else:
            scrapeRate = float(len(noReps))/len(testList)*100
            
        scrapeRateStat = '%.3f'%round(scrapeRate,3)

        flask.flash('\n\n')
        flask.flash('SCRAPE RATES:')
        stats = str(scrapeRateStat)+'% scrape rate'
        flask.flash(stats),#'-- Actual'

        testStats = '%.3f'%(float(len(noReps))/len(testList)*100)

        nonScraped = []
        newList = [i[0:2] for i in csvList]

        for x in testList:
            if x[0:2] not in newList:
                nonScraped.append([x])
                with open(directory+'/NON-scraped'+what.upper()+where+'.csv','w') as f:
                    writer = csv.writer(f,delimiter=',',quoting=csv.QUOTE_ALL)
                    [writer.writerow(row) for row in nonScraped]
                print '\n'
            else:
                pass
        flask.flash('NON-scraped'+what.upper()+where+'.csv is ready in '+directory+'\n')
        flask.flash(str(len(nonScraped))+' out of '+str(len(testList))+' were NOT scraped\n\n')

        # else:
        for x in testList:
            if x[0:2] not in newList:
                nonScraped.append([x])
            else:
                pass

        return output


app.add_url_rule('/',
                view_func=View.as_view('main'), 
                methods=['GET','POST'])

app.debug = True
app.run()

