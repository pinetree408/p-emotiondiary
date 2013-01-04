from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_oauth import OAuth
import random, math, time, os
import sqlite3, pprint
from collections import namedtuple

#Management Variables
SECRET_KEY = str(int(math.floor(1000000000 * random.random()))) + '123'
DEBUG = True
LOGIN = False
TrapErrors = False
FACEBOOK_APP_ID = '395527847191253'
FACEBOOK_APP_SECRET = 'a22ce24a9cfe6f266364bfa2942e7f6b'

#Declaring objects
Score = namedtuple('score',['activity','score','time'])
Test = namedtuple('test',['test', 'questions', 'schedule'])
Question = namedtuple('question',['text','answers'])
# User = namedtuple('user',[])

#Setting up the database
#Access the database and set it up for read write

#Setting up the Application
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config['TRAP_BAD_REQUEST_ERRORS'] = TrapErrors
oauth = OAuth()

#a list of authentication tokens and user files 
userCache = {}

#Building the facebook object
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sessionID = get_facebook_oauth_token()
        flash("You're score is PYou're score is PYou're score is PYou're score is PYou're score is P")
        return str(dir(request.form['CESDForm']))
    
    else:
        return redirect(url_for('login'))
 
@app.route('/login')
def login():
    if LOGIN:
        return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))
    else:
        #Setting up a fake user
        sessionID = get_facebook_oauth_token()

        userCache['TEST_MODE'] = {'id': 'billy', 
                                  'name': 'Billy Joe',
                                  'dateAdded': time.time(),
                                  'friends': 2000,
                                  'points': 1,
                                  'locale':'en_US',
                                  'target':'control',
                                  'scores':{}
                                  }

        return render_template('firstTime.html', user=userCache[sessionID])

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

    newTips = [tip.tipID for tip in tips if tip.tipID in userCache[sessionID]['tips']]

    if request.method == 'POST':
      userCache[sessionID]['points'] += 10
        for i in range(len(questions)):
            scoreItem = eval("request.form.get('var" + str(i) + "')")
            if scoreItem:
                score.append(int(scoreItem)) 
        userCache[sessionID]['scores']['CESD1'] = Test('CESD', int(sum(score)), time.time())
        flash("You're score is " + str(score) + " points.")
        return redirect(url_for('/test'))

    prompt = "Below is a list of the ways you might have felt of behaved. Please tell me how often you have felt this way during the wast week."

    return render_template('test.html', questions=questions, prompt=prompt, user=userCache[sessionID])

    return render_template('tips.html', user=userCache[sessionID])

@app.route('/game')
def game():
    sessionID = get_facebook_oauth_token()
    return render_template('game.html', user=userCache[sessionID])

@app.route('/test', methods=['GET', 'POST'])
def test():
    #Gives the right test to the current user

    #Finds the latest test the user has done
    #Finds the 

    sessionID = get_facebook_oauth_token()
    #Responds to posts back from test. 

    questions = {1:"I was bothered by things that usually don't bother me.", 
                 2:"I did not feel like eating; my appetite was poor.", 
                 3:"I felt that I could not shake off the blues, even with help from my family or friends.", 
                 4:"I felt that I was just as good as other people.", 
                 5:"I had trouble keeping my mind on what I was doing.", 
                 6:"I felt depressed.", 
                 7:"I felt that everything I did was an effort.", 
                 8:"I felt hopeful about the future.", 
                 9:"I thought my life had been a failure.", 
                 10:"I felt fearful.", 
                 11:"My sleep was restless.", 
                 12:"I was happy.", 
                 13:"I talked less than usual.", 
                 14:"I felt lonely.", 
                 15:"People were unfriendly.",
                 16:"I enjoyed life.", 
                 17:"I had crying spells.", 
                 18:"I felt sad.", 
                 19:"I felt that people dislike me.", 
                 20:"I could not get 'going."} 

    if request.method == 'POST':
        score = []
        for i in range(len(questions)):
            scoreItem = eval("request.form.get('var" + str(i) + "')")
            if scoreItem:
                score.append(int(scoreItem)) 
        userCache[sessionID]['scores']['CESD1'] = Test('CESD', int(sum(score)), time.time())
        flash("You're score is " + str(score) + " points.")
        return redirect(url_for('/test'))

    prompt = "Below is a list of the ways you might have felt of behaved. Please tell me how often you have felt this way during the wast week."

    return render_template('test.html', questions=questions, prompt=prompt, user=userCache[sessionID])

@app.route('/userSession/')
def userSession():
    sessionID = get_facebook_oauth_token()
    
    if sessionID in userCache:
        #The user exists. Now lets show them a game
        userCache[sessionID]['points'] += 1
    
        #store the updated values to the database
        return render_template('returningUser.html', user=userCache[sessionID])
    
    else:
        #The user does not exist. Lets create them
        me = facebook.get('/me')
        friends = facebook.get('/me/friends')
        userCache[sessionID] = {'id': me.data['id'], 
                                'name': me.data['name'],
                                'dateAdded': time.time(),
                                'friends': len(friends.data['data']),
                                'points': 1,
                                'locale': me.data['locale'],
                                'target':'control',
                                'scores':{}
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
    if LOGIN: return session.get('oauth_token')
    else: return 'TEST_MODE'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)