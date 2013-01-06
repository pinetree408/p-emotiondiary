from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O
import os

"""Tips = {123: {'EN':(O.Tip(
	'Aproximatly 25% of people are depressed to a degree that could be treated',
	'www.google.com',
	'What percentage humans do you think are treatably depressed',
	O.Answers('15%', '25%', '50%', '100%'),
	'25%'), 'KR': None}}"""

Tips = {}

def buildTips():
	f = open('static/tipsRaw.txt', 'r').read()
	for line in f:
		

	
buildTips()