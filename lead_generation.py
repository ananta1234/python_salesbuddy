import pandas as pd
from apiclient.discovery import build
import requests
import json
import datetime


def getResults(company, keyword, get_email=True, pattern="", domain=""):

	current_time = datetime.datetime.now() 

	api_key = "AIzaSyCLOLyy8PdfeXmVj99sTFt6VABccYsF-lY"

	#Form the query
	query = '"' + company + '" "' + keyword + '" ' + "site:linkedin.com"
	num_pages = 3

	#Run the query for our specfic created search engine
	resource = build("customsearch", 'v1', developerKey=api_key).cse()
	initial = resource.list(q=query, cx='003064078597969779551:36doddfichj').execute()

	#Save and format the results
	try:
	    results = initial['items']
	    for i in range(11, num_pages*10+1, 10):
	        next_res = resource.list(q=query, cx='003064078597969779551:36doddfichj', start=i).execute()
	        results += next_res['items']

	    cleaned_results = [v for v in results if "/in/" in v['link']]

	    try:
	    	titles = [v['title'].split("-")[1].strip() for v in cleaned_results]
	    except:
	    	titles = [v['title'] for v in cleaned_results]
	    names = [(v['title'].split()[0], v['title'].split()[1]) for v in cleaned_results]
	    links = [v['link'] for v in cleaned_results]

	    ans = []

	    for i in range(len(cleaned_results)):
	        first, last = names[i]
	        link = links[i]
	        title = titles[i]

	        email = ""
	        status = ""
	        seniority = "NA"
	        department = "NA"
	        phone = "NA"
	        row = [company, keyword, first, last, email, status, title, seniority, department, link, phone, pattern, current_time]

	        ans.append(row)
	except:
		ans = []
		
	return ans