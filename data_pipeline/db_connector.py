# built into Python, no pip install needed — interacts with the operating system (files, folders, paths, environment variables),
# used here to read the database URL (DATABASE_URL) from the environment
import os

# imports load_dotenv function, reads the .env file in the project folder and 
# loads all key-value pairs into the session environment
from dotenv import load_dotenv  

import psycopg2 # psycopg2 is the client library, the Python equivalent of psql

# sits on top of psycopg2, translates Python into each database's SQL flavor and 
# manages the connections, used here to create the engine pandas needs for df.to_sql()
import sqlalchemy  

# load_dotenv reads the .env file and injects its key-value pairs into the environment,
# making them accessible via os.getenv() alongside system variables like PATH and USER.
# override=False ensures existing environment variables take precedence over .env values,
# so GitHub Actions secrets (or any pre-set env vars) are not overwritten.
load_dotenv(override=False)  

# os.environ is the environment variables pool, .get('DATABASE_URL') pulls the db url from it by key name
db_url = os.environ.get('DATABASE_URL')  

# psycopg2.connect() opens the pipeline between Python and the PostgreSQL server
# db_connection is the open pipeline, the active connection to the server
# cursor is the transport inside that pipeline, sends SQL commands and brings results back

# db_connection using DATABASE_URL from .env, contains all connection details in one string
# dsn= explicitly tells psycopg2 that db_url is a full connection string, 
# prevents it from misinterpreting it as separate key-value pairs
db_connection = psycopg2.connect(dsn=db_url)
cursor = db_connection.cursor()

# create_engine() builds the engine from DATABASE_URL, it doesn't connect yet,
# it opens a connection the first time it's used, like when to_sql() loads a DataFrame
# the engine keeps a pool of connections and reuses a free one instead of opening a new one each time
engine = sqlalchemy.create_engine(db_url)

