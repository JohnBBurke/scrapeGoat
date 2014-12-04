from flask import request, make_response, session
import flask, flask.views
# from flaskext.mysql import MySQL
from bs4 import BeautifulSoup
import requests
from datetime import timedelta
from os.path import expanduser
import json
import os
import csv
import re
import io
import sys
import itertools
import subprocess

# {
#     "detect_indentation": False
# }
subprocess.call('./open_browser.txt',shell=True)
# mysql = MySQL()
app = flask.Flask(__name__)
app.secret_key = os.urandom(32)
# app.config['MYSQL_DATABASE_USER'] = 'name'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
# app.config['MYSQL_DATABASE_DB'] = '*DB*'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)

# conn = mysql.connect()
# cursor = conn.cursor()

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

        regexPeriod = re.compile('^[0-9]{3}\.[0-9]{3}\.[0-9]{4}')
        regexDash = re.compile('^[0-9]{3}-[0-9]{3}-[0-9]{4}')
        regex800 = re.compile('^1-[0-9]{3}-[0-9]{3}-[0-9]{4}')
        regexPeriod1 = re.compile('^1\.[0-9]{3}\.[0-9]{3}\.[0-9]{4}')

        def reformatNumber(xperiod,xdash,x800,xperiod1,number):
            number = number.encode('utf-8').strip()
            if re.search(x800,number):
                number = number[0]+' ('+number[2:5]+') '+number[6:]
                print number
            elif re.search(xdash,number):
                number = '('+number[0:3]+') '+number[4:]
                print number
            elif re.search(xperiod,number):
                number = '('+number[0:3]+') '+number[4:7]+'-'+number[8:]
                print number
            elif re.search(xperiod1,number):
                number = number[0]+' ('+number[2:5]+') '+number[6:9]+'-'+number[10:]
                print number
            else:
                pass

        
        def writeCsv():
            if not number:
                pass
            else:
                csvList.append([lead_fname,lead_mname,lead_lname,number,name_prefix,name_suffix,firmName,lead_email,lead_address,lead_apto,jobCity,jobState,lead_zip,jobTitle,lead_site,lead_title,balance_due,googleNameSearch,custom2]) 
                with open(directory+'/'+what.upper()+where+'.csv','w') as f:
                    writer = csv.writer(f,delimiter=',',quoting=csv.QUOTE_ALL)
                    writer.writerow(['lead_fname','lead_mname','lead_lname','lead_number','name_prefix','name_suffix','firm_name','lead_email','lead_address','lead_apto','job_city','job_state','lead_zip','job_title','lead_site','lead_title','balance_due','linkedin_data','custom2'])
                    [writer.writerow(row) for row in csvList]
                # cursor.execute('INSERT into *DB* (firmname,jobtitle,jobcity,jobstate,phoneNumber,URLtoLinkedInData) values (%s, %s, %s, %s,%s,%s)',
                #                (firmName,jobTitle,jobCity,jobState,number,bingNameSearch))

        getInfo = lambda x,y,z: item.find_all(x,{y:z})[0].text.encode('utf-8').strip()
        intgr = lambda x: int(x) if x.isdigit() else x

        url = 'http://www.indeed.com/search?q='+what+'&l='+where+'&sr=directhire'+'&as_any=&ttl=&jt='+jobType+'&salary='+salary+'&fromage='+fromage
        r = requests.get(url)
        soup = BeautifulSoup(r.content)

        try:
            limit = soup.find_all(id='searchCount')[0].text.encode('utf-8').split()
        except:
            flask.flash("INDEED.COM RETURNED NO RESULTS!\n\nPlease try again.\n\n")
            return self.get()

        limit = [re.sub(',','',str(x)) for x in limit]
        limit = [intgr(x) for x in limit]
        searchLimit = 1001 if limit[5] >= 1000 else limit[5]+10

        i = 0
        testList = []
        csvList = []
        while i<searchLimit:
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
                        for link in item('a',href=re.compile('^/rc/clk\?jk=|^.*clk\?|^.*\?r=1')):
                            source = 'http://www.indeed.com'+link.get('href')
                            post_url = 'https://www.googleapis.com/urlshortener/v1/url'
                            payload = {'longUrl': source}
                            headers = {'content-type':'application/json'}
                            r = requests.post(post_url, data=json.dumps(payload), headers=headers)
                            text = r.content
                            lead_site = str(json.loads(text)['id'])
                        googleNameSearch = 'https://www.google.com/search?q=%'+jobCity+'+'+jobState+'%22+%2B+%22'+firmNamePlus+'%22-intitle:%22profiles%22+-inurl:%22dir%2F+%22+site:linkedin.com%2Fpub%2F'
                        # bingNameSearch = 'https://www.bing.com/search?q='+firmNamePlus+jobCity+'+'+jobState+'%20name%20site%3Alinkedin.com'
                        # nameReq = requests.get(bingNameSearch)
                        # nameSoup = BeautifulSoup(nameReq.content)
                        # namesList = []
                        # for n in nameSoup.find_all('li',{'class':'b_algo'}):
                        #     if re.search('^.* \|.*LinkedIn',n.text):
                        #         name = re.findall('^(.*) \|',n.text)[-1].encode('utf-8').title()
                        #         namesList.append(name)
                        #         names = str(namesList)
                        #         names = re.sub('(\')',' ',str(names))
                        #         names = names.translate(None,'\[\]').strip()

                        # dummy_variables/autoDialFormat

                        lead_fname = 'n/a'
                        lead_mname = 'n/a'
                        lead_lname = 'n/a'
                        # lead_phone -> number
                        name_prefix = 'n/a'
                        name_suffix = 'n/a'
                        # lead company -> firmName
                        lead_email = 'n/a'
                        lead_address = 'n/a'
                        lead_apto = 'n/a'
                        # lead_city -> jobCity
                        # lead_state -> jobState
                        lead_zip = 'n/a'
                        # lead_description -> jobTitle
                        # lead_website -> leadSite
                        lead_title = 'n/a'
                        balance_due = 'n/a'
                        # custom1 -> googleNameSearch
                        custom2 = 'n/a'
                        for this in contactData:
                            if re.search(regNum,this.text):
                                number = re.findall(altRegNum,this.text)[0].encode('utf-8')
                                reformatNumber(regexPeriod,regexDash,regex800,regexPeriod1,number)
                                writeCsv()
                        for z in altContactData:
                            if not contactData:
                                if re.search(altRegNum,z.text):
                                    number = re.findall(altRegNum,z.text)[0].encode('utf-8')
                                    reformatNumber(regexPeriod,regexDash,regex800,regexPeriod1,number)
                                    writeCsv()
                        for q in altaltContactData:
                            if not contactData:
                                if not altContactData:
                                    if re.search(regNum,q.text):
                                        number = re.findall(altRegNum,q.text)[0].encode('utf-8')
                                        reformatNumber(regexPeriod,regexDash,regex800,regexPeriod1,number)
                                        writeCsv()
                        for num in moreSoup:
                            if not contactData:
                                if not altContactData:
                                    if not altaltContactData:
                                        if re.search(altRegNum,moreSoup.text):
                                            number = re.findall(altRegNum,moreSoup.text)
                                            for p in number:
                                                number = p
                                                reformatNumber(regexPeriod,regexDash,regex800,regexPeriod1,number)
                                            writeCsv()
                                        else:
                                            number = re.findall(altRegNum,str(num))
                                            for z in number:
                                                number = z
                                                reformatNumber(regexPeriod,regexDash,regex800,regexPeriod1,number)
                                            writeCsv()
                    except:
                        pass
            except Exception as e:
                print e
                pass

            # data = cursor.fetchone()
            # conn.commit()

            i+=10

        si = io.BytesIO()
        cw = csv.writer(si)
        [cw.writerow(row) for row in csvList]
        output = make_response("lead_fname,lead_mname,lead_lname,lead_number,name_prefix,name_suffix,firm_name,lead_email,lead_address,lead_apto,job_city,job_state,lead_zip,lead_description,lead_site,lead_title,balance_due,linkedin_data,custom2"+'\n'+si.getvalue())
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
                # with open(directory+'/NON-scraped'+what.upper()+where+'.csv','w') as f:
                #     writer = csv.writer(f,delimiter=',',quoting=csv.QUOTE_ALL)
                #     [writer.writerow(row) for row in nonScraped]
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

        # conn.close()
        return output


app.add_url_rule('/',
                view_func=View.as_view('main'), 
                methods=['GET','POST'])

app.debug = True
app.run()
