#Packages to include
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauth import OAuth
import random, math, time, os
import sqlite3, pprint
from collections import namedtuple

#Files to include (from here)
from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O

#Setting up the database
#Access the database and set it up for read write

#Setting up the Application
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config['TRAP_BAD_REQUEST_ERRORS'] = TrapErrors

#Setting path to DB
if DEBUG == True:
  dbURL = 'sqlite:////tmp/test.db'
else: dbURL = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL

#Data management
userCache = {}

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    locale = db.Column(db.String(80))
    authID = db.Column(db.String(100), unique=True)
    # dateAdded: time.time(),
    # friends: len(friends.data['data']),
    # points: 1,
    # locale: me.data['locale'],
    # target: 'control',
    # scores:{},
    # tips:{} #tip ID keys with answers as values

    def __init__(self, authID, name, locale):
        self.name = name
        self.authID = authID
        self.locale = locale

    def __repr__(self):
        return str(self.name) + ' ' + str(self.authID)

if DEBUG == True:
  db.drop_all()
  db.create_all()

#Routes
@app.route('/database')
def database():
    return pprint.pformat(User.query.all())
    return pprint.pformat(userCache)

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sessionID = get_facebook_oauth_token()
        flash("Just a test Flash")
        return str(dir(request.form['CESDForm']))
    
    else:
        return redirect(url_for('login'))
 
@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
    next=request.args.get('next') or request.referrer or None,
    _external=True))

@app.route('/about')
def about():
    sessionID = get_facebook_oauth_token()
    return render_template('about.html', user=userCache[sessionID])

@app.route('/userInfo')
def userInfo():
    sessionID = get_facebook_oauth_token()
    return render_template('userInfo.html', user=userCache[sessionID])

@app.route('/share')
def share():
    rsp = facebook.post('/me', data={'caption': 'Testing', 'method':'feed', 'name':'A test'})
    return str(pprint.pprint(rsp))

@app.route('/tips', methods=['GET', 'POST'])
def tips():
    sessionID = get_facebook_oauth_token()

    tips = [O.Tip(123, 'Approximately 25% of people are depressed to a degree that could be treated.', 'www.google.com', 'What percentage depressed people do you think are treatable?', [O.Answer(1231, '15%'), O.Answer(1232, '25%'), O.Answer(1233, '50%')], 1232)]

    newTips = [tip for tip in tips if tip.tipID not in userCache[sessionID]['tips']]

    tip = newTips.pop()

    if request.method == 'POST':
      answer = request.form.get('answer')
      # if answer == tip.correctAnswer:
      #   response = 'Right!\n' + tip.tipText
      # else: response = "Try Again"
      response = tip.tipText
      userCache[sessionID]['points'] += 10
      flash(response, 'tip')

    return render_template('tips.html', user=userCache[sessionID], tip=tip)

@app.route('/game')
def game():
    sessionID = get_facebook_oauth_token()
    return render_template('game.html', user=userCache[sessionID])

@app.route('/test', methods=['GET', 'POST'])
def test():

    #Gives the right test to the current user and stores the score
    
    Tests = (O.Test('CESD1','ces-d.html',0), O.Test('TEST2','test2.html',4))
    sessionID = get_facebook_oauth_token()
    
    if request.method == 'GET':

        #Check the users complete tests
        #Check other test schedule data
        currentTest = Tests[0]
          #If there are no tests now, return otherActivitesPage
        
        #Load test
        return render_template('tests/ces-d.html', user=userCache[sessionID])

    if request.method == 'POST':
        
        #Store test scores
        #Reload base URL
        score = []
        for i in range(len(questions)):
            scoreItem = eval("request.form.get('var" + str(i) + "')")
            if scoreItem:
                score.append(int(scoreItem)) 
        userCache[sessionID]['scores']['CESD1'] = Test('CESD', int(sum(score)), time.time())
        flash("You're score is " + str(score) + " points.",'system')
        return redirect(url_for('/test'))

@app.route('/userSession/')
def userSession():
    sessionID = get_facebook_oauth_token()
    
    sessionUser = User.query.filter_by(authID=sessionID[0]).first()

    if sessionUser:
        #The user exists. Now lets show them a game
        userCache[sessionID]['points'] += 1
    
        #store the updated values to the database
        return render_template('returningUser.html', user=userCache[sessionID])
    
    else:
        #The user does not exist. Lets create them
        me = facebook.get('/me')
        friends = facebook.get('/me/friends')

        #Initiate user in database
        user = User(sessionID[0], me.data['name'], me.data['locale'])
        db.session.add(user)
        db.session.commit()
        
        #Build local user
        userCache[sessionID] = {'id': me.data['id'], 
                                'name': me.data['name'],
                                'dateAdded': time.time(),
                                'friends': len(friends.data['data']),
                                'points': 1,
                                'locale': me.data['locale'],
                                'target':'control',
                                'scores':{},
                                'tips':{} #tip ID keys with answers as values
                                }

        return render_template('firstTime.html', user=userCache[sessionID])

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
    return session.get('oauth_token')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)