
# turns each table's list of records into a DataFrame, so we can drop columns and load it into Supabase
import pandas as pd  

# built into Python, used here to pause half a second between page requests so we don't overload the API
import time

# built into Python, no pip install needed — interacts with the operating system (files, folders, paths, environment variables),
# used here to read the User-Agent, the API URL and the API key from the environment
import os

# imports load_dotenv function, reads the .env file in the project folder and 
# loads all key-value pairs into the session environment
from dotenv import load_dotenv

# requests turns main.py into a web client — it sends requests to websites and gets their responses back
# used here to pull each table from the SaferProducts API, one page at a time, with GET requests ("give me what's at this URL")
# by default it identifies itself to servers as a Python script (python-requests), not as a browser like Chrome
import requests

# logging module, used here to write to the activity log configured in logfile_generator
# it provides the write functions, logging.info(), logging.warning() and logging.error(), 
# that send entries to the file opened and configured by logfile_generator
import logging  

# logfile_generator sets up the activity log for the entire session
# it tells Python where to write, what format to use, and the minimum level to record
from activity_logs import logfile_generator

# holds the message strings, the list of API tables we pull, and the columns we drop, keeps logic and text separate
import constants 

# drop_unused_columns drops the columns we don't need from each table (__metadata and the links to related tables)
from transform import drop_unused_columns


# load_dotenv reads the .env file and injects its key-value pairs into the environment,
# making them accessible via os.getenv() alongside system variables like PATH and USER.
# override=False ensures existing environment variables take precedence over .env values,
# so GitHub Actions secrets (or any pre-set env vars) are not overwritten.
load_dotenv(override=False)

# os.environ is the environment variables pool — .get() pulls a value by key, returning None if not found
# CHROME_USER_AGENT → Chrome's User-Agent string, sent in request headers to avoid being blocked by SaferProducts
# SAFERPRODUCTS_BASE_API_URL → base URL for the SaferProducts Web API (CPSC incident reports and recall data)
# SAFERPRODUCTS_API_KEY → SaferProducts API key, sent as the username in basic auth with an empty password
user_agent = os.environ.get('CHROME_USER_AGENT')
url = os.environ.get('SAFERPRODUCTS_BASE_API_URL')
username = os.environ.get('SAFERPRODUCTS_API_KEY')

print('SaferProducts pipeline started, pulling data from the API...', '\n')

def main():
	try:

		# extra info sent with the request — merged with requests' defaults, so only User-Agent and Accept are replaced
		# by default requests labels itself as a Python script (python-requests), and SaferProducts blocks that with a 403
		# Chrome's User-Agent makes SaferProducts treat the script like a browser instead
		# Accept asks the API to answer in JSON instead of XML — odata=verbose is the JSON style OData version 2 understands
		headers = {'User-Agent': user_agent, 'Accept': 'application/json;odata=verbose'}
		
		
		# goes through every table we pull, one at a time — table_name tells us which table this round is for
		for table_name in constants.saferproducts_tables:

			# fresh empty list for this table's records, so tables never mix
			json_list = []

			# the table's base address: base URL + table name, no skiptoken
			table_url = url + table_name

			# counts the pages that come back good, used in the logs at the end and in the except
			page_count = 0

			# asks for page 1, with the headers and the API key (auth sends the key as the username, with an empty password)
			# timeout=60 → waits up to 60 seconds for the server to answer before giving up
			# it was 30, but the CPSC server sometimes takes longer than that on a page, and one slow page was killing the whole run
			page_response = requests.get(table_url, headers=headers, timeout=60, auth=(username, ''))

			# keeps going as long as there's a page to read — we set page_response to None when we're done
			while page_response is not None:

				# raise_for_status() looks at the status code before we touch the data
				# if it's bad (400 and up, like 401, 403 or 404), it throws an HTTPError and we jump to the except
				# if it's good, it does nothing and we keep going
				# without it, requests doesn't see a bad status as an error, so the except would only catch stuff like timeouts
				# it goes before .json() on purpose: if the page came back bad, it holds an error message instead of data,
				# so we stop right there with the real reason (like 401 Unauthorized) instead of crashing later with something confusing like KeyError: 'd'
				page_response.raise_for_status()

				# .json() turns the page's JSON text into a Python dictionary, so we can grab its parts by key
				# every OData response wraps everything inside one key called 'd', so the data always lives in page_data['d']
				page_data = page_response.json()

				# counts the page once it came back good and turned into JSON
				page_count += 1

				# isinstance(value, type) checks what type a value is, and returns True or False
				# here it checks whether 'd' is a dictionary, because the API answers in 2 different shapes depending on the table:
				# big tables come back in OData v2, where d is a dictionary with 2 keys:
				# results (the list of records on this page) and __next (the link to the next page)
				if isinstance(page_data['d'], dict):

					# .get('results') pulls the list of records out of d
					# extend adds each record from that list into json_list as its own item,
					# append would add the whole list as one single item, giving us a list inside a list
					# like [1, 2].extend([3, 4]) → [1, 2, 3, 4], but [1, 2].append([3, 4]) → [1, 2, [3, 4]]
					json_list.extend(page_data['d'].get('results'))

					# .get('__next') pulls the link to the next page
					# .get() returns None instead of crashing with a KeyError when the key isn't there,
					# and on the last page the API doesn't send __next at all, so next_link ends up as None
					next_link = page_data['d'].get('__next')

					# no next link means this was the last page, so setting page_response to None stops the while
					if next_link == None:
						page_response = None

					else:
						# __next points to the CPSC's internal server, which we can't reach, so we only keep the part after the ?
						# split('?') cuts the link in 2 at the ?, [1] grabs the 2nd piece, and we add the ? back in front
						# like ?$skiptoken=1170640, which means "give me the records after this ID"
						next_skiptoken = '?' + next_link.split('?')[1]

						# half-second pause between requests so we don't overload the API
						time.sleep(0.5)

						# asks for the next page using our own URL + the skiptoken, with the same headers, timeout and API key,
						# the new response goes back into page_response, so the while runs again on this new page
						page_response = requests.get(table_url + next_skiptoken, headers=headers, timeout=60, auth=(username, ''))


				# small tables come back in OData v1, where d is just the list of records itself, no results or __next,
				# isinstance checks that d is a list, and since everything fits in one page there's nothing more to ask for
				elif isinstance(page_data['d'], list):

					# d is already the list of records, so extend adds each one straight into json_list
					json_list.extend(page_data['d'])

					# only one page, so setting page_response to None stops the while
					page_response = None

			# all pages collected, so the records become one DataFrame for this table
			raw_df = pd.DataFrame(json_list)

			# logs the table's final pull summary, the total rows collected and the total pages requested to get them
			logging.info(f'{table_name}: pull complete, {len(raw_df)} rows from {page_count} pages')

			# drop_unused_columns is the first transform step, it hands the DataFrame on to the rest of the cleanup
			drop_unused_columns(table_name, raw_df)


	# triggered when a page pull fails — no internet, the site is down, the request times out,
	# or raise_for_status() finds a bad status like 401, 403, 404 or 500
	# RequestException is the parent of all requests errors, so this one except catches every case
	except requests.exceptions.RequestException as e:
		print(constants.request_exception_error)
		logging.error(f'RequestException: {e}')

		# logs which table and exactly which page broke
		# page_count only counts the pages that came back good, so +1 is the page that failed
		logging.error(f'Request failed on {table_name}, at page: {page_count + 1}')

# only runs main() when this file is run directly, not when it's imported from another file
if __name__ == '__main__':
    main()