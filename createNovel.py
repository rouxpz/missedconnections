import re
import sqlite3
from random import randrange
import datetime
import os

#create optional arguments for a city-specific, directionally-specific (ie, w4m/m4w/w4w/m4m), or thematic novel
#set up optional city variable
city_input = raw_input("Please enter the city you want.  If none, hit return: ")

if city_input != "":
	city = city_input
else:
	city = "all"
print city

#set up optional orientation variable
direction_input = raw_input("Please enter an orientation you want.  If none, hit return: ")

if direction_input != "":
	direction = direction_input
else:
	direction = "all"
print direction

#setting up optional theme for novel
theme = []
theme_file = raw_input("Please enter the name of the theme file.  If none, hit return: ")
print len(theme)

#!!! CHANGE ORDER OF SENTENCE TYPES HERE !!!
# this is the array that the looping is referring to to tell what type of sentence you are on
content = ["intro", "description", "interaction", "more", "afterthought"]
content_lists = []

for c in content:
	c = []
	content_lists.append(c)

#initialize blank list, this is where we are storing the novel and the IDs of all the sentences in it
novel = []
ids = []

#setting up lists for the pronoun exchanges
# !!! CHANGE PRONOUN FILE HERE !!!
fromWords = []
toWords = []
fromFile = "from.txt"
toFile = "w4m.txt"

#function to pick a random sentence from a specified array
def selectSentence(type):

	seed = randrange(len(type))
	return seed

def printNovel():

	#generates a unique file name with the city and the date/time
	pubdate = datetime.datetime.now()
	filename = "novels/" + city + "-" + pubdate.strftime("%B%d%y-%I%M%p") + ".txt"
	dir = os.path.dirname(filename)
	if not os.path.exists(dir):
		os.makedirs(dir)

	print "Title is " + filename

	#pick a intros sentence at random from the list, append it to the novel list
	introsSentence = selectSentence(content_lists[0])
	novel.append(content_lists[0][introsSentence][0])
	# print content_lists[0][introsSentence][0]
	ids.append(content_lists[0][introsSentence][1])

	#if you want to start the novel with a type other than the first, change this to between 0-4
	currentSentence = 0
	count = len(content_lists[0][introsSentence][0])

	print "Intro sentence selected."

	#while the total character count is less than 5000...
	# !!! CHANGE CHARACTER COUNT HERE !!!
	while count < 5000:
		try:
			total = len(content)-1

			#picking new sentence type based on last sentence type
			#first type of sentence is only used at the beginning.  the other types cycle through.

			if currentSentence == total:
				nextSentence = selectSentence(content_lists[total])
				newcopy = content_lists[total][nextSentence][0]
				newid = content_lists[total][nextSentence][1]

				novels_set = set(novel)

				if newcopy in novels_set:
					#print "Found a " + content[i] + " match!  Trying again."
					currentSentence = i

				else:
					novel.append(newcopy)
					ids.append(newid)

					# for more of the first type of sentence (intro), change this to 0
					currentSentence = 1
					#print newcopy

					#adding the length of the last sentence to the total character count, determines whether the loop runs again
					count += len(novel[-1])

			else:
				for i in range(0, total):

					if currentSentence == i:

						# print currentSentence
						nextSentence = selectSentence(content_lists[i+1])
						newcopy = content_lists[i+1][nextSentence][0]
						newid = content_lists[i+1][nextSentence][1]

						novels_set = set(novel)

						if newcopy in novels_set:
							#print "Found a " + content[i] + " match!  Trying again."
							currentSentence = i

						else:
							novel.append(newcopy)
							ids.append(newid)
							currentSentence = i+1
							# print newcopy
							count += len(novel[-1])

		except KeyboardInterrupt:
			break

	#put a final sentence to end the novel
	nextSentence = selectSentence(content_lists[len(content)-1])
	novel.append(content_lists[len(content)-1][nextSentence][0])

	#writing to a text file
	file = open(filename, "w")

	#looping through novel list, cleaning up the text a little, and writing each sentence to the file
	for sentence in novel:
		sentence = sentence.strip()
		sentence = sentence.lower()
		for i in range(0,len(fromWords)):
			sentence = sentence.replace(fromWords[i], toWords[i])
		sentence = sentence.capitalize()
		sentence = sentence.replace("i'd", "I'd").replace("i'm", "I'm").replace(" i ", " I ").replace("i'll", "I'll")

		#print sentence
		file.write(sentence + ". ")

	file.close()

	print "Novel is generated at " + filename + ", count of " + str(count) + " characters"


#function to load words from a text file into an array
def loadFromFile(filename, destination):

	file = open("dictionaries/" + filename, "r")
	phrases = file.read()
	phrases = phrases.split('\n')

	for phrase in phrases:
		destination.append(phrase)


#load theme file
if theme_file != "":
	loadFromFile(theme_file, theme)
else:
	theme.append(' ')
# print len(theme)

#connect to the database
conn = sqlite3.connect('novelsDB.db')
c = conn.cursor()
conn.text_factory = str

print "Accessing data..."

if city == "all" and direction == "all":

	#select from all the db entries, doesn't matter what city or what direction
	c.execute('SELECT * from sentences')
	results = c.fetchall()

elif city == "all" and direction != "all":
	#select from all entries where the direction matches, regardless of city
	c.execute('SELECT * from sentences WHERE direction=:theDirection',
		{"theDirection": direction})
	results = c.fetchall()

elif city != "all" and direction == "all":
	#select from all entries where the direction matches, regardless of city
	c.execute('SELECT * from sentences WHERE city=:theCity',
		{"theCity": city})
	results = c.fetchall()

else:
	#select all db entries where the city matches the city argument AND the direction matches the direction argument
	c.execute('SELECT * from sentences WHERE city=:theCity AND direction=:theDirection',
		{"theCity":city, "theDirection":direction})
	results = c.fetchall()

print "Data accessed!"
# print results

#adding cities to lists by category of sentence
for result in results:

	category = result[4]
	sentence = result[3]
	id = result[0]

	# print "Data sorted..."

	#run this if the length of the theme array is greater than 1, meaning there is a theme file included
	if len(theme) > 1:
		for word in theme:
			if word in sentence:

				for c in content:
					if category == c:
						indices = [i for i, n in enumerate(content) if n == c]

						for i in range(0, len(indices)):
							j = indices[i]
							content_lists[j].append([sentence, id])

	#otherwise, if there's no theme file:
	else:
		for c in content:
			if category == c:
				indices = [i for i, n in enumerate(content) if n == c]

				for i in range(0, len(indices)):
					j = indices[i]
					content_lists[j].append([sentence, id])

# print content_lists[0]
#create pronoun exchange lists
loadFromFile(fromFile, fromWords)
loadFromFile(toFile, toWords)

#call printNovel to print result
printNovel()


