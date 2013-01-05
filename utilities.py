#Packages to include
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
oauth = OAuth()

class Objects(object):
	"""Declerations of objects"""
	Score = namedtuple('score',['activity','score','time'])
	Test = namedtuple('test',['test', 'questions', 'schedule'])
	Question = namedtuple('question',['text','answers'])
	Tip = namedtuple('tip',['tipID', 'tipText', 'citation', 'questionText', 'answers', 'correctAnswer'])
	Answer = namedtuple('answer', ['answerID', 'answerText'])
	# User = namedtuple('user',[])

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
