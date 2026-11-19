# projectB

A data engineering project that tracks consumer complaints about potentially dangerous products, using public data from [SaferProducts.gov](https://www.saferproducts.gov), the Consumer Product Safety Commission's (CPSC) public database.

## Why

SaferProducts.gov publishes thousands of public reports about products that injured people or put them at risk, but very little analysis is done on them. This project turns that raw data into insights about which brands and products draw the most complaints, and how manufacturers respond.

## What it does

- Pulls 8 tables from the SaferProducts API (OData v2), page by page: `IncidentDetails`, `CompanyDetails`, `SourceTypes`, `SeverityTypes`, `Locales`, `RelationshipTypes`, `Sexes` and `ProductCategories`
- Cleans each table in Python: drops unused columns, converts decimal ID columns back to whole numbers, and renames columns and tables to snake_case
- Loads each table into the `saferproducts_raw` schema in PostgreSQL on Supabase, truncating and inserting in a single transaction, so a failed table never stays half loaded
- Logs every step (rows pulled, pages, columns dropped and converted, rows loaded and any errors) to a timestamped activity log
- *(Planned)* dbt snapshots of every raw table (SCD Type 2), keeping the history of complaints that get corrected or deleted, since the raw tables are fully replaced on every run
- *(Planned)* dbt silver and gold models, from raw tables to clean, analysis-ready ones, with data quality tests
- *(Planned)* Daily schedule with GitHub Actions

## How to run

1. Create the raw schema for SaferProducts on your PostgreSQL database, since PostgreSQL won't create it when the tables are created:

   ```sql
   CREATE SCHEMA IF NOT EXISTS saferproducts_raw;
   ```

2. Create the raw tables: run the SQL scripts in [`table_schema_scripts/raw`](table_schema_scripts/raw). They create the 8 tables inside `saferproducts_raw` that the load step inserts into.

3. Create a `.env` file in the project root with:

   - `CHROME_USER_AGENT`: Chrome's User-Agent string, since the site blocks the default `python-requests` one
   - `SAFERPRODUCTS_BASE_API_URL`: the SaferProducts API base URL
   - `SAFERPRODUCTS_API_KEY`: your free API key
   - `DATABASE_URL`: your PostgreSQL connection string

4. Run the pipeline:

   ```bash
   python3 main.py  # macOS/Linux
   python main.py   # Windows
   ```

## Insights

For starters:

- Brands ranked by number of complaints
- Most recent complaint per brand
- Manufacturer replies vs. total complaints
- Complaints grouped by product category

...and more to come.

## About the data

For more info, check [ABOUT_THE_DATA.md](docs/ABOUT_THE_DATA.md).

[DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) will cover every table and column, and will be filled in once all the dbt models are finished.