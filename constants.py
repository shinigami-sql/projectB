# messages

request_exception_error = 'Download failed — check the log file for details'
bad_zip_file_error = 'Unzip failed, the downloaded file is not a valid zip'
sql_alchemy_error = 'Load to Supabase failed — check the log file for details'

# variables
raw_schema = 'saferproduts_raw'


# lists

# the SaferProducts API tables pulled every run — each name is the table's href, added to the base URL in 'response'
saferproducts_tables = [
    'IncidentDetails',
    'CompanyDetails',
    'SourceTypes',
    'SeverityTypes',
    'Locales',
    'RelationshipTypes',
    'Sexes',
    'ProductCategories'
]

# columns dropped from every table's DataFrame before loading: __metadata is the CPSC's internal address,
# and the rest are just links to related tables, we already have their IDs to join on later
columns_to_drop = [
    '__metadata',
    'Location',
    'IncidentDetails',
    'SourceType',
    'SeverityType',
    'Locale',
    'RelationshipType',
    'Sex',
    'ProductCategory',
    'CompanyComments',
    'IncidentDocuments',
    'RecallProductManufacturers',
    'RecallProductCategories'
]
