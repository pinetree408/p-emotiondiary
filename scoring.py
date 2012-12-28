import random, math

users = 100
rewardTotal = 1000.0


levels = [30.0,10.0,5.0]

rewarded = 0
for i in range(users):
	rewarded += levels[int(math.floor(3 * random.random()))]
	print rewarded