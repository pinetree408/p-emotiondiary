# Here we show what the anatomy of a tip is within our application

#Importing tools to make tips work
from collections import namedtuple
import pprint

#Defining the needed data structures
Tip = namedtuple('tip',['tipID', 'tipText', 'citation', 'questionText', 'answers', 'correctAnswer'])
Answer = namedtuple('answer', ['answerID', 'answerText'])
tips = []

#The code for adding a tip
tips.append(Tip(123,
				'Aproximatly 25% of people are depressed to a degree that could be treated',
				'www.google.com',
				'What percentage humans do you think are treatably depressed',
				[Answer(1231, '15%'), Answer(1232, '25%'), Answer(1233, '50%')],
				1232))

#As seen above tips have the following components:

#tipText - the text of the tip
#citation - the best source for the tip information
#questionText - a simple question about the tip
#answers - a list of Answer objects, basically a list of optional answer choices
#correctAnswer - the ID of the right answer