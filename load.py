# built into Python, no pip install needed — interacts with the operating system (files, folders, paths, environment variables),
# used here to read the database URL (DATABASE_URL) from the environment
import os

# imports load_dotenv function, reads the .env file in the project folder and 
# loads all key-value pairs into the session environment
from dotenv import load_dotenv  

# logging module, used here to log each table's load (rows loaded) and any SQLAlchemy error
# it provides the write functions, logging.info(), logging.warning() and logging.error()
# no need to import logfile_generator here, main.py already set up the log before this file runs,
# so every logging call in here writes to that same log file
import logging

# holds the project's message strings and lists, used here for the SQLAlchemy error message
import constants 

# sits on top of psycopg2, translates Python into PostgreSQL's SQL flavor and manages the connections,
# used here to create the engine, open the connection and run the truncate and to_sql() through it
import sqlalchemy

# parent of every SQLAlchemy error, so one except catches them all
from sqlalchemy.exc import SQLAlchemyError  


# load_dotenv reads the .env file and injects its key-value pairs into the environment,
# making them accessible via os.getenv() alongside system variables like PATH and USER.
# override=False ensures existing environment variables take precedence over .env values,
# so GitHub Actions secrets (or any pre-set env vars) are not overwritten.
load_dotenv(override=False)  

# os.environ is the environment variables pool, .get('DATABASE_URL') pulls the db url from it by key name
db_url = os.environ.get('DATABASE_URL')

# create_engine() builds the engine from DATABASE_URL, it doesn't connect yet,
# a connection only opens when engine.connect() is called inside load_data
# the engine keeps a pool of connections and reuses a free one instead of opening a new one each time
engine = sqlalchemy.create_engine(db_url)

# loads each cleaned DataFrame from transform into its Supabase raw table
def load_data(table_name, raw_df):

		# the try wraps the connection too, so if Supabase can't be reached the except still catches it and logs it
		try:

			# engine.connect() creates the connection object, 'as connection' just names it,
			# the with is the context manager, works like with open() as file:, it closes the connection
			# automatically when the block ends, even on an error,
			# closing also rolls back anything that wasn't committed, so a failed table never stays half loaded
			with engine.connect() as connection:

				# empties the table but keeps its design (columns, types, id SERIAL, upload_timestamp default),
				# text() marks the string as SQL, SQLAlchemy 2.0 won't run a plain string,
				# the f-string puts the real table name in, without it the SQL would look for a table literally named table_name
				connection.execute(sqlalchemy.text(f'TRUNCATE saferproducts_raw.{table_name}'))

				# DataFrame.to_sql(name_of_table, connection, *, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None)
				# only the 2 before '*' are mandatory, everything after has a default and must be passed by name
				# table_name → the Supabase table, already snake_case from transform
				# connection → the same connection that ran the truncate, so both get saved by one commit
				# schema → the tables live in saferproducts_raw, not the default public schema
				# if_exists='append' → inserts into the existing table, 'replace' would drop it and let pandas
				# recreate it with its own guessed types, losing the design we built ('delete_rows' would do the
				# truncate for us, but it needs pandas 3, which needs Python 3.11+, and this venv is on 3.10)
				# index=False → without it pandas adds its row numbers as an extra column, which the tables don't have
				raw_df.to_sql(table_name, connection, schema='saferproducts_raw', if_exists='append', index=False)

				# saves the truncate and the insert together, nothing is in Supabase until this runs
				connection.commit()

				# logged after the commit, so it only says loaded when the data is actually saved
				logging.info(f'{table_name}: truncated and loaded {len(raw_df)} rows successfully')

		# SQLAlchemyError is the parent of every SQLAlchemy error, so this catches any of them,
		# the table name goes in the log so we know exactly which table failed
		except SQLAlchemyError as e:
			print(constants.sql_alchemy_error)
			logging.error(f'{table_name}: load failed, SQLAlchemyError: {e}')





