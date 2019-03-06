import xml.etree.ElementTree as ET

import re, json
from multiprocessing import Pool
from os import listdir
from functools import partial
# from nltk.corpus import stopwords
path1 = 'gcide-0.52/'

# parser = ET.XMLParser(encoding="utf-8")

stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
			"yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
			"it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
			"who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
			"been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
			"the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
			"with", "about", "against", "between", "into", "through", "during", "before", "after", 
			"above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", 
			"again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", 
			"any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
			"only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", 
			"should", "now"]
    	
def removestopwords(raw_text):
	from nltk.corpus import stopwords
	filtered_words = [word for word in raw_text if word not in stopwords.words('english')]

def cleantags(raw_text):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_text)
	cleantext = cleantext.lower().split(' ')
	cleantext = [word for word in cleantext if word.lower() not in stopwords]
	cleantext = ' '.join(cleantext)
	return cleantext


def create_def_dict(path):
	def_dict = {}
	file_list = (listdir(path))
	
	for file_name in file_list:
		if "CIDE." in file_name:
			with open(path1+file_name, encoding = "ISO-8859-1") as f:
				limit = 0
				current_key = ''
				dup = 0
				for line in f:
					try:
						if ('<ent>' in line):
							term = re.compile('<ent>(.*?)</ent>', re.DOTALL | re.IGNORECASE).findall(line)
							current_key = term[0]
							dup = 0
							continue
						if ('<def>' in line):
							defin = re.compile('<def>(.*?)</def>', re.DOTALL | re.IGNORECASE).findall(line)
							if (current_key in def_dict.keys()):
								dup += 1
								def_dict[current_key+'_'+str(dup)] = cleantags(defin[0])
								print(current_key+'_'+str(dup)+": "+def_dict[current_key+'_'+str(dup)])
							else:
								def_dict[current_key] = cleantags(defin[0])
								print(current_key+": "+def_dict[current_key])
							continue
					except:
						continue
		else:
			continue
		# break
	return def_dict

def find_synonyms(chunk, input_dict, threshold=.8):
	count = 0
	sampler_count = 100
	thesaurus = {}
	for key1, val1 in chunk.items():
		# thesaurus[key1] = []
		# if sampler_count % 100 == 0:
		synonyms = []
		def1 = val1.split()
		for key2, val2 in input_dict.items():
			# print("2:",thesaurus[key1])
		
			if key1 != key2:
				def2 = val2.split()
				
				# print("4:",thesaurus[key1])
				# print("3:",thesaurus[key1])
				if (len(set(def1)) < len(set(def2))):
					smaller_def = len(set(def1))
				else:
					smaller_def = len(set(def2))
				if (smaller_def == 0):
					continue
				common = set(def1).intersection( set(def2) )
				match_percentage = len(common)/smaller_def
				# print(key1, key2)
				if (match_percentage >= threshold):
					try:
						# if key1 in thesaurus.keys():
						# 	thesaurus[key1] = thesaurus[key1].append(key2)
						# else:
						# 	thesaurus[key1] = [key2]
						# print("5:",thesaurus[key1])
						synonyms.append(key2)
						# print(key1, key2, common, match_percentage)
					except:
						continue
		count +=1
		# sampler_count += 1
		thesaurus[key1] = synonyms
		if (count == 10000):
			print(count, "Term: ", key1, 'synonyms: ',synonyms)
		# else:
		# 	# sampler_count += 1
		# 	continue
		# count += 1
		# if count > 10:
		# 	break
		# break
	return thesaurus


def split_dict_equally(input_dict, chunks=2):
    "Splits dict by keys. Returns a list of dictionaries."
    # prep with empty dicts
    return_list = [dict() for idx in range(chunks)]
    idx = 0
    for k,v in input_dict.items():
        return_list[idx][k] = v
        if idx < chunks-1:  # indexes start at 0
            idx += 1
        else:
            idx = 0
    return return_list

def main():
	# def_dict = create_def_dict(path1)
	# with open('data.json', 'w') as fp:
	# 	json.dump(def_dict, fp, sort_keys=True, indent=4)


	
	with open('data.json', 'r') as fp:
		data = json.load(fp)

		'''
		# Multiprocess version
		dict_list = split_dict_equally(data, 8)
		p = Pool(processes=8)
		prod_x = partial(find_synonyms, input_dict=data) # prod_x has only one argument x (y is fixed to 10) 
		result_list = p.map(prod_x, dict_list) 
		p.close()
		# print(result_list)
		with open('thesaurus.json', 'w') as fp:
			combine_dict = {k: v for d in result_list for k, v in d.items()}
			json.dump(combine_dict, fp, sort_keys=True, indent=4)
		'''
		# No multiprocess
		thesaurus = find_synonyms(data, data, .85)
		with open('thesaurus.json', 'w') as fp:
			json.dump(thesaurus, fp, sort_keys=True, indent=4)
		

main()
with open('thesaurus.json', 'r') as fp:
	data = json.load(fp)
	print(len(data))
with open('thesaurus1.json', 'r') as fp:
	data = json.load(fp)
	print(len(data))
with open('thesaurus2.json', 'r') as fp:
	data = json.load(fp)
	print(len(data))

# print(split_dict_equally(samp_dict, 2))


