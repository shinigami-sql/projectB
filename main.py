
# built into Python, no pip install needed — interacts with the operating system (files, folders, paths, environment variables), 
# used here to read the User-Agent from the environment
import os

# zipfile is built into Python, no pip install needed
# it opens and extracts zip files, used here to unzip the downloaded export
# and get to the incident reports CSV inside
import zipfile

# imports load_dotenv function, reads the .env file in the project folder and 
# loads all key-value pairs into the session environment
from dotenv import load_dotenv

# requests turns main.py into a web client — it sends requests to websites and gets their responses back
# used here to download the SaferProducts zip file with a GET request ("give me what's at this URL")
# by default it identifies itself to servers as a Python script (python-requests), not as a browser like Chrome
import requests

# built into Python, gets the current date and time, used here to timestamp each downloaded zip 
# so every download is kept as history instead of overwriting the last one
from datetime import datetime  

# logfile_generator sets up the activity log for the entire session
# it sets up the connection — it tells Python where to write, 
# what format, and what minimum level. Think of it as opening and configuring the file.
from activity_logs import logfile_generator

# holds all static message strings used across main.py, keeps logic and text separate
import constants 

# logging module, used here to write to the activity log configured in logfile_generator
# it provides the write functions, logging.info(), logging.warning() and logging.error(), 
# that send entries to the file opened and configured by logfile_generator
import logging  


# loads the .env file into the session environment, 
# adds the key-value pairs to the same pool as system variables like PATH and USER
# override=False prevents load_dotenv from overwriting variables already in the environment,
# allowing GitHub Actions secrets to take priority over .env values
# IMPORTANT: This is not required here as the User-Agent doesn't include confidential data, just doing it for practice purposes
load_dotenv(override=False)

# os.environ is the environment variables pool — .get() pulls a value from it by key name, and returns None if the key isn't there
# CHROME_USER_AGENT → Chrome's User-Agent, sent in the request headers so SaferProducts doesn't block the script
# SAFERPRODUCTS_EXPORT_URL → direct link to the SaferProducts Public Database Export — a zip file holding
# the incident reports CSV, the recalls CSV and a disclaimer txt
user_agent = os.environ.get('CHROME_USER_AGENT')
url = os.environ.get('SAFERPRODUCTS_EXPORT_URL')

# os.makedirs creates the SaferProductsZipFiles folder, where every downloaded zip is stored
# open() can create a file but not a folder, so the folder has to exist before writing into it
# exist_ok=True skips the step if the folder is already there, instead of raising a FileExistsError
os.makedirs('safer_products_zipfiles', exist_ok=True)

def main():
	try:

	    # extra info sent with the request — merged with requests' defaults, so only User-Agent is replaced
	    # by default requests labels itself as a Python script (python-requests), and SaferProducts blocks that with a 403
	    # Chrome's User-Agent makes SaferProducts treat the script like a browser instead
	    headers = {'User-Agent': user_agent}

	    # sends a GET request ("give me what's at this URL") with the headers attached
	    # response holds the status code, the headers and the zip itself, in response.content as raw bytes
	    response = requests.get(url, headers=headers)

	    # raise_for_status() checks the status code — any bad status (400 and up, like 403 or 404)
	    # raises an HTTPError that jumps straight to the except, so the file never gets saved
	    # without it, a bad status isn't an error for requests, so the except would never trigger
	    # and the error page would get saved as a zip
	    # a good status returns None, meaning no problem found, and the script moves on to store_file
	    response.raise_for_status()

	    # shows the status code on screen — 200 means the download worked
	    print(f'Status Code: {response.status_code}')
	    logging.info(f'Status Code: {response.status_code}')

	    # saves the zip locally with a timestamp in its name, and returns its path for the unzip step
	    store_file(response.content)

	# triggered when the download fails — no internet, the site is down, the request times out,
	# or raise_for_status() finds a bad status like 403, 404 or 500
	# RequestException is the parent of all requests errors, so this one except catches every case
	except requests.exceptions.RequestException as e:
		print(constants.request_exception_error)
		logging.error(f'RequestException: {e}')
		


# saves the downloaded zip with a timestamp in its name, so every download is kept as history
# returns the file's path so the unzip step knows which zip to open
def store_file(binary_file):

    # builds the path: folder + date and time + SPDB.zip, e.g. SaferProductsZipFiles/2026-10-07_10-14-00_SPDB.zip
    # dashes instead of colons, since colons break file names on Finder and Windows
    file_path = f"safer_products_zipfiles/SPDB_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_')}.zip"

    # 'wb' writes raw bytes, since a zip isn't text — with closes the file automatically
    with open(file_path, 'wb') as file:
        file.write(binary_file)

    return file_path

# only runs main() when this file is run directly, not when it's imported from another file
if __name__ == '__main__':
    main()