# -*- coding: utf-8 -*-
#Packages to include
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauth import OAuth
import random, math, time, os, datetime
import sqlite3, pprint
from collections import namedtuple
#  from facepy.utils import get_extended_access_token

#Files to include (from here)
from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O, OFFLINE, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET

#Setting up Data
Crawl_Time = 2419200                 # 2419200 = 4 weeks in seconds
Crawl_By_Limit = False               # if False, it will crawl datas by Crawl_Time. if True, it will just crawl last 100 datas of user's timeline..

#Setting up the Application
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config['TRAP_BAD_REQUEST_ERRORS'] = TrapErrors

#Setting path to DB depending on DEBUG setting
if DEBUG == True:
    # dbURL = 'sqlite:////tmp/test.db'
    dbURL = os.environ['DATABASE_URL']
else: 
    dbURL = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL

userCache = {}

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authID = db.Column(db.PickleType, unique=True)
    facebookID = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode)
    locale = db.Column(db.Unicode)
    friendNum = db.Column(db.Integer)
    target = db.Column(db.String(10))
    points = db.Column(db.Integer)
    calendar = db.Column(db.PickleType)
    testscore = db.Column(db.PickleType)    ## Pickled 'Dictionary' type in Python
    tip = db.Column(db.PickleType)          ## Pickled 'Array(list)' type in Python. stores which number of tips user viewed.
    crawldata = db.Column(db.PickleType)
    accessTime = db.Column(db.Integer)
    # dateAdded: time.time(),
    # friends: len(friends.data['data']),
    # points: 1,
    # locale: me.data['locale'],
    # target: 'control',
    # scores:{},
    # tips:{} #tip ID keys with answers as values

    # def __init__(self, authID, facebookID, name, locale):
    def __init__(self, authID, facebookID, name, locale, friendNum, target, points, calendar, testscore, tip, crawlData, accessTime):
        self.authID = authID
        self.facebookID = facebookID
        self.name = name
        self.locale = locale
        self.friendNum = friendNum
        self.target = target
        self.points = points
        self.calendar = calendar
        self.testscore = testscore
        self.tip = tip
        self.crawldata = crawlData
        self.accessTime = accessTime
        

    def __repr__(self):
        return self.name.encode('utf-8') + ', ' + self.locale.encode('utf-8')

# if DEBUG == True:
#   db.drop_all()
#   db.create_all()

#Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    sessionID = get_facebook_oauth_token()

    if sessionID in userCache:
        sessionUser = User.query.filter_by(facebookID=userCache[sessionID].id).first()

        if sessionUser != None:
            newCrawl = userCache[sessionID].data
           
            # the code for update timeline Feed, it's time-consuming so we should comment out when unnecceary.
            if Crawl_By_Limit:
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&limit=100')
            else:  
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&since='+ str(int(time.time())-Crawl_Time) )  
            newCrawl[0] = timelineFeed.data
            #

            user = userCache[sessionID]._replace(locale = facebook.get('me').data['locale'], friends = len(facebook.get('me/friends?limit=5000').data['data']), data=newCrawl)
            userCache[sessionID] = user

            User.query.filter_by(facebookID=facebook.get('me').data['id']).update(dict(locale = user.locale, friendNum = user.friends, crawldata = newCrawl, accessTime = int(time.time())))
            db.session.commit()

            #Handling the base state of authenticated users
            if 'CESD1' in user.testscores.keys():
                return render_template('returningUser.html', user = user, userID=str(userCache[sessionID].id))
            else:
                return render_template('firstTime.html', user = user, userID=str(userCache[sessionID].id))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

    # #Deal with a POST request
    # if request.method == 'POST':
    #     # flash("Just a test Flash")
    #     # return str(dir(request.form['CESDForm']))
    #     if sessionID in userCache:
    #         user = userCache[sessionID]._replace(locale = facebook.get('me').data['locale'])
    #         userCache[sessionID] = user
    #         User.query.filter_by(facebookID=facebook.get('me').data['id']).update(dict(locale = user.locale))
    #         db.session.commit()

    #         #Handling the base state of authenticated users
    #         if 'CESD1' in user.testscores.keys():
    #             return render_template('returningUser.html', user = user)
    #         else:
    #             return render_template('firstTime.html', user = user)

    #     else: return redirect(url_for('login'))
    
    # #Deal with a GET request
    # else:

    #     #Check for user authentication
    #     if sessionID in userCache:
    #         user = userCache[sessionID]._replace(locale = facebook.get('me').data['locale'])
    #         userCache[sessionID] = user
    #         User.query.filter_by(facebookID=facebook.get('me').data['id']).update(dict(locale = user.locale))
    #         db.session.commit()

    #         #Handling the base state of authenticated users
    #         if 'CESD1' in user.testscores.keys():
    #             return render_template('returningUser.html', user = user)
    #         else:
    #             return render_template('firstTime.html', user = user)

    #     #Authenticate new users
    #     else: return redirect(url_for('login'))
 
@app.route('/login')
def login():
    if OFFLINE: #Loading an off line test user
        sessionID = get_facebook_oauth_token()
        userCache[sessionID] =  O.User('John Smith', 'Test ID', sessionID, time.time(), 203, 1, 'ko_KR', 'control', {}, {}, ['TEMP_Data'])
        newUser = User(sessionID, u'TEST ID', u'John Smith', u'ko_KR', 203, 'control', 1, {}, {}, {'TEMP_crawlData'}, int(time.time()))
        db.session.add(newUser)
        db.session.commit()

        return redirect(url_for('index'))

    #If not OFFLINE:
    return facebook.authorize(callback=url_for('facebook_authorized',
    next=request.args.get('next') or request.referrer or None,
    _external=True))

# @app.route('/database')
# def database(): #A function to render raw data - can be improved later
#     # return pprint.pformat(Tips) #For rendering Tips
#     # return pprint.pformat(User.query.all()) #For rendering User DB
#     # return pprint.pformat(userCache) #For rendering userCache
#     return pprint.pformat(userCache) #For rendering userCache

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    sessionID = get_facebook_oauth_token()
    user_fbID = facebook.get('me').data['id']
    test = User.query.filter_by(facebookID=user_fbID).first().calendar
    todaydate = datetime.date.today()

    if len(test) > 0:
        lastdate = test[(len(test) - 1)][0]

        if request.method == 'GET':
            if todaydate == lastdate:
                return redirect(url_for('calendarresult'))
                #return render_template('calendar.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

            else:
                if (todaydate.toordinal() - lastdate.toordinal()) > 1:
                    for i in range(todaydate.toordinal() - lastdate.toordinal() - 1):
                        blankemotion = []
                        blankdate = lastdate + datetime.timedelta(days=(i+1))
                        blankemotion.append(blankdate)
                        result = 0
                        blankemotion.append(result)
                        index = len(test) + i + 1
                        blankemotion.append(index)
                        memo = ""
                        blankemotion.append(memo)
                        userCache[sessionID].calendar.append(blankemotion)
                    User.query.filter_by(facebookID=user_fbID).update(dict(calendar = userCache[sessionID].calendar))
                    db.session.commit()
                    return render_template('calendar.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
                else:
                    return render_template('calendar.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
    else:
        if request.method == 'GET':
            return render_template('calendar.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))


    if request.method == 'POST':

        todayemotion = []

        today = datetime.date.today()
        todayemotion.append(today)
        scoreItem = eval("request.form.get('var1')")
        memo = eval("request.form.get('memo')")
        if scoreItem:
            result = int(scoreItem)
        else:
            result = 0
        todayemotion.append(result)
        index = len(userCache[sessionID].calendar) + 1
        todayemotion.append(index)
        todayemotion.append(memo)

        tempUser = O.User(userCache[sessionID].name, userCache[sessionID].id, sessionID, userCache[sessionID].dateAdded, userCache[sessionID].friends,
                               userCache[sessionID].points + 3,  userCache[sessionID].calendar, userCache[sessionID].locale, userCache[sessionID].target, userCache[sessionID].testscores,
                               userCache[sessionID].tips, userCache[sessionID].data)

        user_fbID = facebook.get('me').data['id']
        userCache[sessionID] = tempUser
        userCache[sessionID].calendar.append(todayemotion)
        User.query.filter_by(facebookID=user_fbID).update(dict(calendar = userCache[sessionID].calendar))
        User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
        db.session.commit()

        return redirect(url_for('calendarresult'))

@app.route('/calendarresult', methods=['GET', 'POST'])
def calendarresult():
    sessionID = get_facebook_oauth_token()
    user_fbID = facebook.get('me').data['id']
    dayset = User.query.filter_by(facebookID=user_fbID).first().calendar
    
    month9 = []
    #month10 = []
    #month11 = []
    #month12 = []
    for day in dayset:
        if day[0].month == 9:
            month9.append(day)
    #    if day[0].strftime("%m") == "10":
    #        month10.append(day)
    #    if day[0].strftime("%m") == "11":
    #        month11.append(day)
    #    if day[0].strftime("%m") == "12":
    #        month12.append(day)

    year = []
    year.append(month9)
    #year.append(month10)
    #year.append(month11)
    #year.append(month12)

    yearset = []

    for month in year:
        week1 = []
        week2 = []
        week3 = []
        week4 = []
        week5 = []
        week6 = []
        week7 = []
        week8 = []

        for day in month:
            if day[0].day < 5:
                week1.append(day)
            elif day[0].day < 9:
                week2.append(day)
            elif day[0].day < 13:
                week3.append(day)
            elif day[0].day < 17:
                week4.append(day)
            elif day[0].day < 21:
                week5.append(day)
            elif day[0].day < 25:
                week6.append(day)
            elif day[0].day < 29:
                week7.append(day)
            else:
                week8.append(day)

        monthset = []
        if len(week1) > 0:
            monthset.append(week1)
        if len(week2) > 0:
            monthset.append(week2)
        if len(week3) > 0:
            monthset.append(week3)
        if len(week4) > 0:
            monthset.append(week4)
        if len(week5) > 0:
            monthset.append(week5)
        if len(week6) > 0:
            monthset.append(week6)
        if len(week7) > 0:
            monthset.append(week7)
        if len(week8) > 0:
            monthset.append(week8)

        yearset.append(monthset)

    if request.method == 'GET':
        todaysmonth = []

        for month in yearset:
            if len(month) > 0:
                if month[0][0][0].strftime("%m") == datetime.date.today().strftime("%m"):
                    todaysmonth = month

        length = len(todaysmonth)
        prev = datetime.date.today().month - 1
        next = datetime.date.today().month + 1

        return render_template('calendarresult.html', user=userCache[sessionID], monthhead=todaysmonth[0][0][0].strftime("%m"), month=todaysmonth, len=length ,userID=str(userCache[sessionID].id), prev=prev, next=next)

    if request.method == 'POST':

        prev = eval("request.form.get('prev')")

        if prev:
            prevmonth = int(prev.split(u'월')[0])

            prevsmonth = []

            for month in yearset:  
                if len(month) > 0:
                    if month[0][0][0].month == prevmonth:
                        prevsmonth = month

            length = len(prevsmonth)

            prevprev = prevmonth - 1
            nextnext = prevmonth + 1

            return render_template('calendarresult.html', user=userCache[sessionID], monthhead=str(prevmonth), month=prevsmonth, len=length ,userID=str(userCache[sessionID].id), prev=prevprev, next=nextnext)

        next = eval("request.form.get('next')")

        if next:
            nextmonth = int(next.split(u'월')[0])

            nextsmonth = []

            for month in yearset:
                if len(month) > 0:
                    if month[0][0][0].month == nextmonth:
                        nextsmonth = month

            length = len(nextsmonth)

            prevprev = nextmonth - 1
            nextnext = nextmonth + 1

            return render_template('calendarresult.html', user=userCache[sessionID], monthhead=str(nextmonth), month=nextsmonth, len=length ,userID=str(userCache[sessionID].id), prev=prevprev, next=nextnext)

@app.route('/about')
def about():
    sessionID = get_facebook_oauth_token()
    return render_template('about.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/privacy')
def userInfo():
    sessionID = get_facebook_oauth_token()
    return render_template('userInfo.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/tips', methods=['GET', 'POST'])
def tips():
    sessionID = get_facebook_oauth_token()

    if request.method == 'GET':
        tipFile = open('static/tipsRaw.txt', 'r')

        tipNum = int(tipFile.readline()[3:].split()[0])

        if len(userCache[sessionID].tips) >= tipNum:        # Shown all tips
            return render_template('viewedAlltip.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

        randInt = 1
        while randInt in userCache[sessionID].tips:
            randInt = random.randrange(1, tipNum+1)
        for lines in tipFile:
            splittedTip = lines.split('\t')
            if int(splittedTip[0]) == randInt:
                if userCache[sessionID].locale[-2:] == u'KR':
                    if splittedTip[1] == u'KR':
                        newTip = O.Tip(splittedTip[2].decode('utf8'), splittedTip[3].decode('utf8'), splittedTip[4].decode('utf8'),
                                                splittedTip[5].decode('utf8'), splittedTip[6].decode('utf8'), splittedTip[7].decode('utf8'),
                                                map(lambda a:a.decode('utf8'), splittedTip[8:]))
                        # splittedTip[0]:Number, 1:Locale, 2:Tip, 3:Cite, 4:URL, 5:quotation, 6:question, 7:answer, 8~:wrong
                        return render_template('newTips.html', questionNum = randInt, tip=newTip, user=userCache[sessionID], userID=str(userCache[sessionID].id))
                    else:
                        continue
                else:
                    newTip = O.Tip(splittedTip[2].decode('utf8'), splittedTip[3].decode('utf8'), splittedTip[4].decode('utf8'),
                                             splittedTip[5].decode('utf8'), splittedTip[6].decode('utf8'), splittedTip[7].decode('utf8'),
                                            map(lambda a:a.decode('utf8'), splittedTip[8:]))
                    # splittedTip[0]:Number, 1:Locale, 2:Tip, 3:Cite, 4:URL, 5:quotation, 6:question, 7:answer, 8~:wrong
                    return render_template('newTips.html', questionNum = randInt, tip=newTip, user=userCache[sessionID], userID=str(userCache[sessionID].id))

    if request.method == 'POST':
        resp = eval("request.form.get('response')")
        if int(resp) % 10 == 1:   # correct answer
            if not ((int(resp) / 10) in userCache[sessionID].tips):
                tempUser = O.User(userCache[sessionID].name, userCache[sessionID].id, sessionID, userCache[sessionID].dateAdded, userCache[sessionID].friends,
                                   userCache[sessionID].points + 3,  userCache[sessionID].calendar, userCache[sessionID].locale, userCache[sessionID].target, userCache[sessionID].testscores,
                                   userCache[sessionID].tips, userCache[sessionID].data)
                    # We can't change the value of userCache[sessionID] because it's namedtuple, the immutable object. to adjust the value, we should change the whole object.
                user_fbID = facebook.get('me').data['id']
                userCache[sessionID] = tempUser
                userCache[sessionID].tips.append(int(resp) / 10)
                User.query.filter_by(facebookID=user_fbID).update(dict(tip = userCache[sessionID].tips))
                User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
                db.session.commit()   

            return render_template('tipCorrect.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

        else:                   # wrong or no answer at all
            return render_template('tipWrong.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/admin')
def admin():
    adminUser = [u'100002383326449', u'567239032', u'100001838301582', u'2022228']
    sessionID = get_facebook_oauth_token()

    if not userCache[sessionID].id in adminUser:
        return render_template('notAdmin.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
    else:
        alluser = User.query.all()
        usertable = []
        for person in alluser:
            newdict = {}
            newdict['name'] = person.name
            newdict['locale'] = person.locale
            newdict['friendNum'] = person.friendNum
            newdict['points'] = person.points
            try:    newdict['CESD1'] = person.testscore['CESD1'][0]
            except KeyError:    newdict['CESD1'] = ""
            try:    newdict['BDI'] = person.testscore['BDI'][0]
            except KeyError:    newdict['BDI'] = ""
            newdict['tip'] = len(person.tip)
            newdict['accessTime'] = time.strftime("%y/%m/%d %H:%M:%S", time.gmtime(person.accessTime))
            usertable.append(newdict)
        return render_template('admin.html', user=userCache[sessionID], alluser=usertable, userID=str(userCache[sessionID].id))

@app.route('/game')
def game():
    sessionID = get_facebook_oauth_token()

    tempUser = O.User(userCache[sessionID].name, userCache[sessionID].id, sessionID, userCache[sessionID].dateAdded, userCache[sessionID].friends,
                               userCache[sessionID].points + 0,  userCache[sessionID].calendar, userCache[sessionID].locale, userCache[sessionID].target, userCache[sessionID].testscores,
                               userCache[sessionID].tips, userCache[sessionID].data)
                # We can't change the value of userCache[sessionID] because it's namedtuple, the immutable object. to adjust the value, we should change the whole object.
    userCache[sessionID] = tempUser
    user_fbID = facebook.get('me').data['id']
    User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
    db.session.commit()   

    return render_template('game.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/test', methods=['GET', 'POST'])
def test():

    #Gives the right test to the current user and stores the score

    Tests = (O.Test('CESD1','ces-d.html',0), O.Test('BDI','bdi.html',4))
    sessionID = get_facebook_oauth_token()

    currentTest = Tests[0]                   # CES-D1: 2013.4. - 4.
    # currentTest = Tests[1]

    if currentTest.name in userCache[sessionID].testscores.keys():
        return render_template('returningUser.html', user = userCache[sessionID], userID=str(userCache[sessionID].id))

    if request.method == 'GET':     
        #Load test
        return render_template('tests/' + currentTest.url, testName=currentTest.name, user=userCache[sessionID], userID=str(userCache[sessionID].id))

    if request.method == 'POST':
                
        #Store test scores at TEST NAME (which is returned)
        #Load an outgoing URL

        score = []
        for i in range(20):
            scoreItem = eval("request.form.get('var" + str(i) + "')")
            if scoreItem:
                score.append(int(scoreItem))
        scoresum = int(sum(score))

        tempUser = O.User(userCache[sessionID].name, userCache[sessionID].id, sessionID, userCache[sessionID].dateAdded, userCache[sessionID].friends,
                               userCache[sessionID].points + 5,  userCache[sessionID].calendar, userCache[sessionID].locale, userCache[sessionID].target, userCache[sessionID].testscores,
                               userCache[sessionID].tips, userCache[sessionID].data)
        # We can't change the value of userCache[sessionID] because it's namedtuple, the immutable object. to adjust the value, we should change the whole object.
        userCache[sessionID] = tempUser
        
        # put the test score to user DB (User.testscore)
        user_fbID = facebook.get('me').data['id']
        userCache[sessionID].testscores[currentTest.name] = [scoresum, time.time()]
        tempDict = dict(User.query.filter_by(facebookID=user_fbID).first().testscore)
        tempDict[currentTest.name] = [scoresum, time.time()]
        User.query.filter_by(facebookID=user_fbID).update(dict(testscore = tempDict))
        User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
        db.session.commit()

        if scoresum < 10:
            return render_template('feedback1.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
        elif 10 <= scoresum < 21:
            return render_template('feedback2.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
        else:
            return render_template('feedback3.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/userSession/')
def userSession():
    sessionID = get_facebook_oauth_token()
    me = facebook.get('me')
    sessionUser = User.query.filter_by(facebookID=me.data['id']).first()
        # check whether user exists in DB

    if sessionUser != None:     # user exists in DB
        if sessionID in userCache:  # user exists in cache. sync user data in each memory.
            newCrawl = userCache[sessionID].data
            if Crawl_By_Limit:
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&limit=100')
            else:  
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&since='+ str(int(time.time())-Crawl_Time) )  
            newCrawl[0] = timelineFeed.data

            userCache[sessionID] = userCache[sessionID]._replace(sessionID = sessionID, friends = len(facebook.get('me/friends').data['data']),
                                                                 locale = me.data['locale'], data=newCrawl)
            User.query.filter_by(facebookID=me.data['id']).update(dict(authID = sessionID, friendNum = userCache[sessionID].friends,
                                                                        locale = userCache[sessionID].locale, crawlData=newCrawl))
            db.session.commit()
        else:                                  # returning User. apply user to cache and update the crawl data.
            # IN THIS PART WE SHOULD ADJUST THE TIME DATA LATER
            userCache[sessionID] = O.User(sessionUser.name, sessionUser.facebookID, sessionID, sessionUser.accessTime, len(facebook.get('me/friends').data['data']),
                                                            sessionUser.points + 1, sessionUser.calendar, me.data['locale'], sessionUser.target, sessionUser.testscore, sessionUser.tip, sessionUser.crawldata)

            # update the crawl data
            friends = facebook.get('me/friends')        
            if Crawl_By_Limit:
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&limit=100')
            else:  
                timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&since='+ str(int(time.time())-Crawl_Time) )  
            groups = facebook.get('me/groups?fields=name')
            interest = facebook.get('me/interests')
            likes = facebook.get('me/likes?fields=name')
            location = facebook.get('me/locations?fields=place')
            notes = facebook.get('me/notes')
            #messages = facebook.get('me/inbox?fields=comments')
            friendRequest = facebook.get('me/friendrequests?fields=from')
            events = facebook.get('me/events')
            try:
                relationStatus = me.data['relationship_status']
            except KeyError:
                relationStatus = "No data"
            #crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]
            crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, None, friendRequest.data, events.data]

            User.query.filter_by(facebookID=me.data['id']).update(dict(locale = userCache[sessionID].locale, points = userCache[sessionID].points,
                                                                                                        authID = sessionID, friendNum = userCache[sessionID].friends,
                                                                                                        crawldata = crawldata_new))
            db.session.commit()

    else:                                  # user does not exists in DB, ignore cache and create new User class.
        friends = facebook.get('me/friends')        
        if Crawl_By_Limit:
            timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&limit=100')
        else:  
            timelineFeed = facebook.get('me/posts?fields=created_time,story,picture,message&since='+ str(int(time.time())-Crawl_Time) )  
        groups = facebook.get('me/groups?fields=name')
        interest = facebook.get('me/interests')
        likes = facebook.get('me/likes?fields=name')
        location = facebook.get('me/locations?fields=place')
        notes = facebook.get('me/notes')
        #messages = facebook.get('me/inbox?fields=comments')
        friendRequest = facebook.get('me/friendrequests?fields=from')
        events = facebook.get('me/events')
        try:
            relationStatus = me.data['relationship_status']
        except KeyError:
            relationStatus = "No data"
        #crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]
        crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, None, friendRequest.data, events.data]

        newUser = User(sessionID, me.data['id'], me.data['name'], me.data['locale'], len(friends.data['data']), 'control', 1, [], {}, [], crawldata_new, int(time.time()))
        db.session.add(newUser)
        db.session.commit()

        userCache[sessionID] = O.User(me.data['name'], me.data['id'], sessionID, int(time.time()), len(friends.data['data']), 1, [], me.data['locale'], 'control', {}, [], crawldata_new)
    
    # after this part there should be identical user data in each memory, DB and cache.

    if 'CESD1' in userCache[sessionID].testscores.keys():
        return render_template('returningUser.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))
    else:
        return render_template('firstTime.html', user=userCache[sessionID], userID=str(userCache[sessionID].id))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['oauth_token'] = (resp['access_token'], '')

    return redirect(url_for('userSession'))

@facebook.tokengetter
def get_facebook_oauth_token():
    if OFFLINE:
        return (u'Debug Mode', "")
    try: 
        return session.get('oauth_token')
        # short_token = session.get('oauth_token')
        # extended_token = get_extended_access_token(short_token, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        # return extended_token[0]
        #### This code makes an internal servor error
    except ValueError:
        pass
    return None

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


# def userSession():                                        # Old version
#     sessionID = get_facebook_oauth_token()
#     user_fbID = facebook.get('me').data['id']
#     sessionUser = User.query.filter_by(facebookID=user_fbID).first()
#         # check whether user exists in DB

#     if sessionUser != None:     # user exists in DB
#         if sessionID in userCache:  # user exists in cache. sync user data in each memory.
#             me = facebook.get('me')
#             userCache[sessionID] = userCache[sessionID]._replace(sessionID = sessionID, friends = len(facebook.get('me/friends').data['data']),
#                                                                                                 locale = me.data['locale'])
#             User.query.filter_by(facebookID=user_fbID).update(dict(authID = sessionID, friendNum = userCache[sessionID].friends,
#                                                                                                 locale = userCache[sessionID].locale))
#             db.session.commit()
#         else:                                  # returning User. apply user to cache and update the crawl data.
#             # IN THIS PART WE SHOULD ADJUST THE TIME DATA LATER
#             userCache[sessionID] = O.User(sessionUser.name, sessionUser.facebookID, sessionID, sessionUser.accessTime, len(facebook.get('me/friends').data['data']),
#                                                             sessionUser.points + 1, me.data['locale'], sessionUser.target, sessionUser.testscore, sessionUser.tip, sessionUser.crawldata)

#             # update the crawl data
#             friends = facebook.get('me/friends')        
#             timelineFeed = facebook.get('me/feed?until='+ str(int(time.time())-604800) )    # 604800 = 1 week for seconds
#             groups = facebook.get('me/groups?fields=name')
#             interest = facebook.get('me/interests')
#             likes = facebook.get('me/likes?fields=name')
#             location = facebook.get('me/locations?fields=place')
#             notes = facebook.get('me/notes')
#             messages = facebook.get('me/inbox?fields=comments')
#             friendRequest = facebook.get('me/friendrequests?fields=from')
#             events = facebook.get('me/events')
#             try:
#                 relationStatus = me.data['relationship_status']
#             except KeyError:
#                 relationStatus = "No data"
#             crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]

#             User.query.filter_by(facebookID=user_fbID).update(dict(locale = userCache[sessionID].locale, points = userCache[sessionID].points,
#                                                                                                 authID = sessionID, friendNum = userCache[sessionID].friends,
#                                                                                                 crawldata = crawldata_new))
#             db.session.commit()

#     else:                                  # user does not exists in DB, ignore cache and create new User class.
#         friends = facebook.get('me/friends')        
#         timelineFeed = facebook.get('me/feed?until='+ str(int(time.time())-604800) )    # 604800 = 1 week for seconds
#         groups = facebook.get('me/groups?fields=name')
#         interest = facebook.get('me/interests')
#         likes = facebook.get('me/likes?fields=name')
#         location = facebook.get('me/locations?fields=place')
#         notes = facebook.get('me/notes')
#         messages = facebook.get('me/inbox?fields=comments')
#         friendRequest = facebook.get('me/friendrequests?fields=from')
#         events = facebook.get('me/events')
#         try:
#             relationStatus = me.data['relationship_status']
#         except KeyError:
#             relationStatus = "No data"
#         crawldata_new = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]

#         newUser = User(sessionID, me.data['id'], me.data['name'], me.data['locale'], len(friends.data['data']), 'control', 1, {}, [], crawlData, int(time.time()))
#         db.session.add(newUser)
#         db.session.commit()

#         userCache[sessionID] = O.User(me.data['name'], me.data['id'], sessionID, int(time.time()), len(friends.data['data']), 1, me.data['locale'], 'control', {}, [], crawlData)
    
#     # after this part there should be identical user data in each memory, DB and cache.

#     if 'CESD1' in userCache[sessionID].testscores.keys():
#         return render_template('returningUser.html', user=userCache[sessionID])
#     else:
#         return render_template('firstTime.html', user=userCache[sessionID])

#         def userSession():
#     sessionID = get_facebook_oauth_token()
#     user_fbID = facebook.get('me').data['id']
#     sessionUser = User.query.filter_by(facebookID=user_fbID).first()
#         # check whether user exists in DB

#     if sessionID in userCache:
#         #The user exists in userCache(cookie remains). just update the score.
#         User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
#         db.session.commit()

#         me = facebook.get('me')
#         userCache[sessionID] = O.User(sessionUser.name, sessionUser.facebookID, sessionID, time.time(), sessionUser.friendNum,
#                                         sessionUser.points + 1, me.data['locale'], sessionUser.target, sessionUser.testscore, sessionUser.tip, sessionUser.crawldata)

#         if 'CESD1' in userCache[sessionID].testscores.keys():
#             return render_template('returningUser.html', user=userCache[sessionID])
#         else:
#             return render_template('firstTime.html', user=userCache[sessionID])

#     elif sessionUser != None:
#         #Returning user :: The user exists in DB. apply user to cache and show them a game
#         me = facebook.get('me')
#         friends = facebook.get('me/friends')

#         userCache[sessionID] = O.User(sessionUser.name, sessionUser.facebookID, sessionID, time.time(), sessionUser.friendNum,
#                                     sessionUser.points + 1, me.data['locale'], sessionUser.target, sessionUser.testscore, sessionUser.tip, sessionUser.crawldata)

        
#         timelineFeed = facebook.get('me/feed?until='+ str(int(time.time())-604800) )    # 604800 = 1 week for seconds
#         groups = facebook.get('me/groups?fields=name')
#         interest = facebook.get('me/interests')
#         likes = facebook.get('me/likes?fields=name')
#         location = facebook.get('me/locations?fields=place')
#         notes = facebook.get('me/notes')
#         messages = facebook.get('me/inbox?fields=comments')
#         friendRequest = facebook.get('me/friendrequests?fields=from')
#         events = facebook.get('me/events')

#         try:
#             relationStatus = me.data['relationship_status']
#         except KeyError:
#             relationStatus = "No data"
        
#         # refresh crawling Data
#         crawlData = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]
#         User.query.filter_by(facebookID=user_fbID).update(dict(authID = sessionID))
#         User.query.filter_by(facebookID=user_fbID).update(dict(crawldata = crawlData))
#         User.query.filter_by(facebookID=user_fbID).update(dict(friendNum = len(friends.data['data'])))
#         User.query.filter_by(facebookID=user_fbID).update(dict(points = userCache[sessionID].points))
#         db.session.commit()

#         #store the updated values to the database
#         if 'CESD1' in userCache[sessionID].testscores.keys():
#             return render_template('returningUser.html', user=userCache[sessionID])
#         else:
#             return render_template('firstTime.html', user=userCache[sessionID])
    
#     else:
#         #The user does not exist. Lets create them
#         me = facebook.get('me')
#         friends = facebook.get('me/friends')

#         timelineFeed = facebook.get('me/feed?until='+ str(int(time.time())-604800) )    # 604800 = 1 week for seconds
#         groups = facebook.get('me/groups?fields=name')
#         interest = facebook.get('me/interests')
#         likes = facebook.get('me/likes?fields=name')
#         location = facebook.get('me/locations?fields=place')
#         notes = facebook.get('me/notes')
#         messages = facebook.get('me/inbox?fields=comments')
#         friendRequest = facebook.get('me/friendrequests?fields=from')
#         events = facebook.get('me/events')

#         try:
#             relationStatus = me.data['relationship_status']
#         except KeyError:
#             relationStatus = "No data"

#         #Instantiate user in database
        
#         crawlData = [timelineFeed.data, relationStatus, groups.data, interest.data, likes.data, location.data, notes.data, messages.data, friendRequest.data, events.data]
#         newUser = User(sessionID, me.data['id'], me.data['name'], me.data['locale'], len(friends.data['data']), 'control', 1, {}, [], crawlData, int(time.time()))
#         db.session.add(newUser)
#         db.session.commit()
        
#         #Instantiate local user
#         userCache[sessionID] = O.User(me.data['name'], me.data['id'], sessionID, time.time(), len(friends.data['data']), 1, me.data['locale'], 'control', {}, [], crawlData)
#         return redirect(url_for('index'))