from py_bing_search import PyBingSearch
import os
import fileinput
import sys
import time
import re

reload(sys)
sys.setdefaultencoding('utf8')
filename = sys.argv[1]
bing = PyBingSearch('UvG/iELD97We0KffqjrVFHwUrEHbe0ZCbeVfraImZRg')

outputfile = filename.replace('.txt', "")
input_text = []
output_text = []

text = open(filename, 'r')
for line in text.readlines():
	input_text.append(line.rstrip());

all_text_length = len(input_text)

badwords = outputfile + "-badwords.txt"
total = outputfile + "-result.txt"

badwords_output = open(badwords, 'w')
total_output = open(total, 'w')

output = open(outputfile + ".json", 'w')

output.write('{"result":[')

index = 0
total_matched_sum = 0
total_passphrase_sum = 0

for query_full in input_text:
	index = index + 1
	passphrase = re.sub(r"\'", '',query_full)
	query = query_full.split()


	for i in range(0, len(query)):
		query[i] = query[i].lower()
		print "qeury[" + str(i) + "] = " + query[i]

	new_list = []

	print passphrase
	#Handling exception in case of bad query
	try:
		result_list = bing.search(passphrase, limit=10, format='json')
	except:
		#Gathering bad query
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
	for x in range(0, 10):
		new_list.append(re.split(r"\((.*)\)|\s|-|,|:|;|u'|!|\?|\"|\'",result_list[0][x].title.encode('utf8').lower()))
		result_list[0][x].title = re.sub(r"\"", '',result_list[0][x].title.encode('utf8').lower())

	for i in range(0, 10):
		matched_list["passphrase"].append([])
		matched_list["title"].append([])
		matched_list["matchedWords"].append([])
		matched_list["maxMatchNumber"].append([])
		matched_list["percentage"].append([])
		matched_list["uniqueMatchedWords"].append([])

	for i in range(10):
		for j in range(len(new_list[i])):
			for k in range(len(query)):
				if query[k] == new_list[i][j]:
					matched_list["matchedWords"][i].append(query[k])

	bestValue = -100
	position = 0
	for i in range(10):
		if bestValue <= len(matched_list["matchedWords"][i]):
			bestValue = len(matched_list["matchedWords"][i])
			position = i

	best_matched_list = matched_list["matchedWords"][position]
	print "position=",position
	print "best_matched_list=",best_matched_list
	count = 0
	count_dic = {}
	#this step will get rid of duplicate words
	new_set = set(query)
	new_set_list = list(new_set)

	print "new_set_list=",new_set_list

	for i in range(len(new_set_list)):
		for j in range(len(query)):
			if new_set_list[i] == query[j]:
				count = count + 1
				count_dic[new_set_list[i]] = count
		count = 0

	search_count = 0
	search_count_dic = {}
	search_new_set = set(best_matched_list)
	search_new_set_list = list(search_new_set)
	print "search_new_set_list=",search_new_set_list
	for i in range(len(search_new_set_list)):
		for j in range(len(best_matched_list)):
			if search_new_set_list[i] == best_matched_list[j]:
				search_count = search_count + 1
				search_count_dic[search_new_set_list[i]] = search_count
		search_count = 0

	count_list = []
	search_count_list = []


	for k,v in count_dic.iteritems():
		count_list.append([k,v])

	for k,v in search_count_dic.iteritems():
		search_count_list.append([k,v])


	final_matching_list = []

	for i in range(len(count_list)):
		for j in range(len(search_count_list)):
			if count_list[i][0] == search_count_list[j][0]:
				if count_list[i][1] == search_count_list[j][1]:
					final_matching_list.append([count_list[i][0], count_list[i][1]])
				elif count_list[i][1] > search_count_list[j][1]:
					final_matching_list.append([count_list[i][0], search_count_list[j][1]])
				elif count_list[i][1] < search_count_list[j][1]:
					final_matching_list.append([count_list[i][0], count_list[i][1]])

	printing_final_matching_list = []
	#print "final_matching_list", final_matching_list
	for i in range(len(final_matching_list)):
		for j in range(0, final_matching_list[i][1]):
			printing_final_matching_list.append(final_matching_list[i][0])

	#printing_final_matching_list has the final result
	#print "printing_final_matching_list=",printing_final_matching_list
	Printed_String_Of_Matched_Words = ", ".join(printing_final_matching_list)
	mmn = len(printing_final_matching_list)
	#print "passphrase=",passphrase
	#print "title=",result_list[0][position].title
	#print "matchedWords",Printed_String_Of_Matched_Words
	#print "maxMatchNumber",bestValue
	#print "percentage",float(bestValue) / float(len(query)) * 100
	percentage_result = float(mmn) / float(len(query)) * 100
	output.write('{"passphrase":"')
	output.write(passphrase)
	output.write('", "title":"')
	output.write(result_list[0][position].title)
	output.write('", "matchedWords":"')
	output.write(Printed_String_Of_Matched_Words)
	output.write('", "maxMatchNumber":"')
	output.write(str(mmn))
	output.write('", "percentage":"')
	output.write(str(percentage_result))

	if all_text_length == index:
		total_matched_sum = total_matched_sum + bestValue
		total_passphrase_sum = total_passphrase_sum + len(query)
		output.write('"}')

	else:
		total_matched_sum = total_matched_sum + bestValue
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


















