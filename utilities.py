#Packages to include
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_oauth import OAuth
import random, math, time, os
import sqlite3, pprint
from collections import namedtuple

#Management Variables
SECRET_KEY = str(int(math.floor(1000000000 * random.random()))) + '123' #secures interaction between the browser and Flask
DEBUG = True #Toggles Flask debug mode, changes FB App to a local friendly one and changes DB URL
OFFLINE = False #Toggles a local user instead of FB authentication (overwritten when not debugging)
TrapErrors = True #Toggles some error handling tools

#Setting up the appropriate Facebook session
if DEBUG == True:
	#Debug app codes
	# FACEBOOK_APP_ID = '292670767512606'
	# FACEBOOK_APP_SECRET = 'c8bf8a30da9fcb60b188cd196850ea47'
	FACEBOOK_APP_ID = '179513298889893'
	FACEBOOK_APP_SECRET = 'c3f6cf7954f3fe6deae0ff5d226d1acd'
	OFFLINE = False
else: 
	#Live app codes
	FACEBOOK_APP_ID = '179513298889893'
	FACEBOOK_APP_SECRET = 'c3f6cf7954f3fe6deae0ff5d226d1acd'
		
oauth = OAuth()

class Objects(object):
	"""Decelerations of objects"""
	#Basic user
	User = namedtuple('user', ['name','id', 'sessionID', 'dateAdded', 'friends', 'points', 'locale', 'target', 'testscores', 'tips', 'data'])
	
	#Test objects
	Score = namedtuple('score',['activity','score','time'])
	Test = namedtuple('test',['name', 'url', 'delay'])

	#Tip Definitions
	Tip = namedtuple('tip', ['tip', 'citation', 'url', 'quote', 'question', 'answer', 'wrong'])

PERMS = [
'email',
'user_about_me',
'friends_about_me',
'user_activities',
'friends_activities',
'user_education_history',
'friends_education_history',
'user_groups',
'friends_groups',
'user_interests',
'friends_interests',
'user_likes',
'friends_likes',
'user_relationships',
'friends_relationships',
'user_location',
'user_subscriptions',
'friends_subscriptions',
'friends_location',
'user_notes',
'friends_notes',
'user_status',
'friends_status',
'user_work_history',
'friends_work_history',
'read_friendlists',
'read_requests',
'read_stream',
'read_mailbox',
'create_event',
]
permissionRequest = ','.join(PERMS)
#Building the facebook object
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': permissionRequest}
    )