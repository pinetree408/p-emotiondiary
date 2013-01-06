#This code builds tips from tipsRaw.txt. It then saves the tips in tipsData.py

#Importing tools to make tips work
from collections import namedtuple
from utilities import facebook, DEBUG, SECRET_KEY, TrapErrors, Objects as O
import pprint

#The code for adding a tip
tips.append(O.Tip(123,
				'Aproximatly 25% of people are depressed to a degree that could be treated',
				'Google',
				'www.google.com',
				'What percentage humans do you think are treatably depressed',
				Answers('15%', '25%', '50%', '100%'),
				'25%'
				))

print tips[0].answers

TipsEN = []
TipsKR = []


#Tips have language which is represented in which list they belong to, i.e. TipsEN, TipsKR
#As seen above tips have the following calls:
	#ID - just a int for the tip
	#tip - the text of the tip
	#citation - the best source for the tip information
	#question - a simple question about the tip
	#answers - a list of Answer objects, basically a list of optional answer choices
	#answer - the correct anwer (it must match the correct answer exactly)