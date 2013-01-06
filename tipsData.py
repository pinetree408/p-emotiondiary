from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O
import os, pprint
import json

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
		
		ID = int(T[0])

		# Making sure wrong is short.	
		wrong = [W for W in T[7:] if len(W)>0]

		if ID not in Tips:
				Tips[ID] = {}

		#Assigning this Tips
		Tips[ID][T[1]] = O.Tip(T[2], T[3], T[4], T[5], T[6], wrong)
	return Tips

# Tip = buildTips()
# pprint.pprint(Tip)