# logging module, used here to log each transform step: dropped columns, converted columns and the renamed table
# it provides the write functions, logging.info(), logging.warning() and logging.error()
# no need to import logfile_generator here, main.py already set up the log before this file runs,
# so every logging call in here writes to that same log file
import logging

# built into Python, regex finds patterns in text and replaces them, used here to turn the CamelCase column names into snake_case
import re

# holds the project's message strings and lists, used here for columns_to_drop
import constants 

# holds the load function, used here to truncate each Supabase raw table and insert the cleaned DataFrame into it
from load import load_data

# drops the columns we don't need from the table (__metadata and the links to related tables)
# goes through the list in constants, and only drops the ones this table actually has, the rest get skipped
# dropped_columns keeps the names so the log shows what got dropped from each table
def drop_unused_columns(table_name, raw_df):
	dropped_columns = []
	for column in constants.columns_to_drop:
		if column in raw_df:
			raw_df.drop(columns=column, inplace=True)
			dropped_columns.append(column)

	logging.info(f'Dropped {len(dropped_columns)} columns for {table_name}: {dropped_columns}')

	# hands the DataFrame to the next transform step
	convert_float_to_int(table_name, raw_df)

# turns the decimal ID columns back into whole numbers, like 15794.0 → 15794
# when a column holding whole numbers has at least one empty value, pandas turns the whole column into float64,
# because it marks empties as NaN, and NaN counts as a decimal number, so every number gets a .0
# pandas does this by default because it was built on NumPy, whose whole number columns can't hold empty values,
# NaN (a float) was the only empty marker it had
# Int64 (capital I) showed up later as an option you pick yourself: it keeps whole numbers and marks empties as <NA>
# so this function goes through every column, and whenever it finds a float64 one, it converts the entire column to Int64
def convert_float_to_int(table_name, raw_df):
	to_int64_columns = []
	for column in raw_df.columns:
		if raw_df[column].dtype == 'float64':
			to_int64_columns.append(column)
			raw_df[column] = raw_df[column].astype('Int64')

	logging.info(f'{table_name}: converted {len(to_int64_columns)} decimal columns to whole numbers (Int64): {to_int64_columns}')

	# hands the DataFrame to the next transform step
	df_to_snake_case(table_name, raw_df)


# renames every column from CamelCase to snake_case, like IncidentReportId → incident_report_id, so they match the Supabase tables
# each column name goes through the 3 regexes, one after the other, each one working on the previous one's result
# if a regex finds no match, the name just passes through unchanged
# snake_case_columns stores original name : new name, and rename swaps them all at once at the end
def df_to_snake_case(table_name, raw_df):
	snake_case_columns = {}
	for column in raw_df.columns:

		# a lowercase, followed by an uppercase with a few lowercase after it, followed by a number, split in 2 spots
		# AddressLine1 → Address_Line_1
		lower_upper_number_regex = re.sub(r'([a-z])([A-Z][a-z]+)([0-9])', r'\1_\2_\3', column)

		# a lowercase followed by an uppercase, split between them
		# IncidentReportId → Incident_Report_Id
		lower_upper_regex = re.sub(r'([a-z])([A-Z])', r'\1_\2', lower_upper_number_regex)

		# a set of uppercases, followed by an uppercase with a lowercase after it, split between them
		# ProductUPCCode → Product_UPC_Code (the 2nd regex already split Product from UPC)
		upper_lower_regex = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', lower_upper_regex)

		# lowercases the final name and stores it, original name : new name
		snake_case_columns[column] = upper_lower_regex.lower()
	
	# rename takes a dictionary of old name : new name, and swaps every column name that matches a key,
	# inplace=True changes raw_df itself instead of returning a renamed copy	
	raw_df.rename(columns=snake_case_columns, inplace=True)

	# a lowercase followed by an uppercase, split between them, then lowercases it all to match the Supabase table names
	# IncidentDetails → incident_details
	# Locales has no match, but re.sub doesn't fail, it returns the name unchanged and .lower() still runs → locales
	table_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', table_name).lower()

	logging.info(f'{table_name}: table name converted to snake_case to match Supabase')

	# transform is done, hands the cleaned DataFrame and the snake_case table name to load
	load_data(table_name, raw_df)




