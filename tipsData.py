from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O
import os, pprint

"""Tips = {123: {'EN':(O.Tip(
	'Aproximatly 25% of people are depressed to a degree that could be treated',
	'citation',
	'www.google.com',
	'What percentage humans do you think are treatably depressed',
	O.Answers('15%', '25%', '50%', '100%')), 'KR': 'None'}}"""

def buildTips():
	tipFile = open('static/tipsRaw.txt', 'r')
	Tips = {}
	for line in tipFile:
		line = line[0:-1]
		T = line.split('\t')
		
		if T[0] not in Tips:
				Tips[T[0]] = {}
		
		Tips[T[0]][T[1]] = O.Tip(T[2], T[3], T[4], T[5], T[6], T[7:])
	return Tips