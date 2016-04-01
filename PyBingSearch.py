from py_bing_search import PyBingSearch
import os
import fileinput
import sys
import time
import re

reload(sys)

sys.setdefaultencoding('utf8')

filename = sys.argv[1] #Get file name

#Requried this BING ID for using Bing search Result
bing = PyBingSearch('UvG/iELD97We0KffqjrVFHwUrEHbe0ZCbeVfraImZRg') #Using bing api

outputfile = filename.replace('.txt', "") #Set the output file name
input_text = []
output_text = []

#Read text from input file
text = open(filename, 'r')
for line in text.readlines():
	input_text.append(line.rstrip());

all_text_length = len(input_text)

#This is for badword list
badwords = outputfile + "-badwords.txt"
#This is for final result list
total = outputfile + "-result.txt"

badwords_output = open(badwords, 'w')
total_output = open(total, 'w')

#Set the output file as JSON
output = open(outputfile + ".json", 'w')

output.write('{"result":[')

index = 0
total_matched_sum = 0
total_passphrase_sum = 0

for query_full in input_text:
	index = index + 1
	passphrase = re.sub(r"\'", '',query_full)
	#split a passphrase sentence using space so that it can be splitting by words
	query = query_full.split()


	for i in range(0, len(query)):
		query[i] = query[i].lower()
		print "qeury[" + str(i) + "] = " + query[i]

	new_list = []

	print passphrase
	#Exception handling in case of bad query
	try:
		result_list = bing.search(passphrase, limit=10, format='json')
	except:
		#Gathering a bad query
		badwords_output.write(query_full + '\n')

	# Initializing dictionary
	#matched_list = {"passphrase": passphrase, "cloestMatching": '', "maxMatchNumber" : 0, "Percentage":0}

	matched_list = {}

	matched_list["passphrase"] = []
	matched_list["title"] = []
	matched_list["matchedWords"] = []
	matched_list["maxMatchNumber"] = []
	matched_list["percentage"] = []
	matched_list["uniqueMatchedWords"] = []


	# Getting all titles from query, and making all letters to lower letters
	# Because matching string value is case-sensitive, converting to lower case will increase accuracy in string matching.
	for x in range(0, 10):
		#new_list is sanitized list by using regular expression.
		new_list.append(re.split(r"\((.*)\)|\s|-|,|:|;|u'|!|\?|\"|\'",result_list[0][x].title.encode('utf8').lower()))
		#new_list and result_list are same, but this result_list is necessary for showing result because it is not sanitized.
		result_list[0][x].title = re.sub(r"\"", '',result_list[0][x].title.encode('utf8').lower())

	#Initialization
	for i in range(0, 10):
		matched_list["passphrase"].append([])
		matched_list["title"].append([])
		matched_list["matchedWords"].append([])
		matched_list["maxMatchNumber"].append([])
		matched_list["percentage"].append([])
		matched_list["uniqueMatchedWords"].append([])

	# Get rid of duplicate words

	#Matching passphrase word by word with received titles in new_list
	for i in range(10): #Have to do 10 loops because we have 10 titles
		matched_list["passphrase"][i].append(passphrase)
		matched_list["title"][i].append(result_list[0][i].title)
		for j in range(len(new_list[i])): # j will have each title length, and will be counted by each word
			for k in range(len(query)): #length has to be query's length because all words in passphrase has to be comparing with all titles
				if query[k] == new_list[i][j]: #if it is matched,
					matched_list["matchedWords"][i].append(query[k])

	
	#=====================================================================#
	# 1. matched_list["matchedWords"] list will have matched words.

	#length_list list has the word and length of the word
	length_list = []
	for i in range(10):
		for j in range(len(matched_list["matchedWords"][i])):
			length_list.append([i, len(matched_list["matchedWords"][i])])


	bestValue = float("-infinity")
	position = 0

	#It picks the position of the word which has long length.
	for i in range(0,10):
		if bestValue <= length_list[i][1]:
			bestValue = length_list[i][1]
			position = i

	#=====================================================================#
	# 1. Using'set' removes duplicate words.
	# 2. This part is consisted of two sub parts.
	# 3. count_dic is related with passphrase words, so it will count duplicate words in passphrase
	# 4. search_count_dic is related with searched words, so it will count duplicate words in searched sentence.
	count = 0
	count_dic = {}
	new_set = set(matched_list["passphrase"][0])
	new_set_list = list(new_set)

	for i in range(len(new_set_list)):
		for j in range(len(matched_list["passphrase"])):
			if new_set_list[i] == matched_list["passphrase"][j]:
				count = count + 1
				count_dic[new_set_list[i]] = count
		count = 0

	search_count = 0
	search_count_dic = {}
	search_new_set = set(matched_list["matchedWords"][position])
	search_new_set_list = list(search_new_set)

	for i in range(len(search_new_set_list)):
		for j in range(len(matched_list["matchedWords"])):
			if search_new_set_list[i] == matched_list["passphrase"][j]:
				search_count = search_count + 1
				search_count_dic[search_new_set_list[i]] = search_count
		search_count = 0

	#=====================================================================#
	# 1. This step will decide choosing duplicate words according to matching.

	count_list = []
	search_count_list = []

	for k,v in count_dic.iteritems():
		count_list.append([k,v])

	for k,v in search_count_dic.iteritems():
		search_count_list.append([k,v])

	final_matching_list = []

	for i in range(len(count_list)):
		for j in range(len(search_count_list)):
			if count_list[i][0] == search_count_list[i][0]:
				if count_list[i][1] == search_count_list[i][1]:
					final_matching_list.append([count_list[i][0], count_list[i][1]])
				elif count_list[i][1] > search_count_list[i][1]:
					final_matching_list.append([count_list[i][0], search_count_list[i][1]])
				elif count_list[i][1] < search_count_list[i][1]:
					final_matching_list.append([count_list[i][0], count_list[i][1]])

	#=====================================================================#
	# 1. printing part

	printing_final_matching_list = []

	for i in range(len(final_matching_list)):
		for j in range(final_matching_list[i][1]):
			printing_final_matching_list.append(final_matching_list[i])

	matchedWords = ''

	for i in range(0, len(matched_list["uniqueMatchedWords"][position])):
		#matched_list["matchedWords"][position].append(matched_list["matchedWords"][position][i]+ ',')
		if i == len(matched_list["uniqueMatchedWords"][position]) -1:
			matchedWords = matchedWords + matched_list["uniqueMatchedWords"][position][i]
		else:
			matchedWords = matchedWords + matched_list["uniqueMatchedWords"][position][i] + ','

	output.write('{"passphrase":"')
	output.write(passphrase)
	output.write('", "title":"')
	output.write(result_list[0][position].title)
	output.write('", "matchedWords":"')
	output.write(matchedWords)
	output.write('", "maxMatchNumber":"')
	output.write(str(matched_list["maxMatchNumber"][position]))
	output.write('", "percentage":"')
	output.write(str(matched_list["percentage"][position]))

	if all_text_length == index:
		total_matched_sum = total_matched_sum + matched_list["maxMatchNumber"][position]
		total_passphrase_sum = total_passphrase_sum + len(query)
		output.write('"}')
	else:
		total_matched_sum = total_matched_sum + matched_list["maxMatchNumber"][position]
		total_passphrase_sum = total_passphrase_sum + len(query)
		output.write('"},')


total_output.write("***result***\n")
total_output.write("Total number of matched words: " + str(total_matched_sum) + '\n')
total_output.write("Total number of passphrase words: " + str(total_passphrase_sum) + '\n')
total_output.write("Percentage: " + str(float(total_matched_sum) / float(total_passphrase_sum) * 100))

total_output.close()

output.write(']}')

output.close()
badwords_output.close()
text.close()





