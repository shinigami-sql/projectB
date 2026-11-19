# projectB

This is a data engineering project that tracks consumer complaints about potentially dangerous products, using public data from [SaferProducts.gov](https://www.saferproducts.gov), the Consumer Product Safety Commission's (CPSC) public database. SaferProducts.gov publishes thousands of public reports about products that injured people or put them at risk, but very little analysis is done on them. This project turns that raw data into insights about which brands and products draw the most complaints, and how manufacturers respond.

The pipeline pulls 8 tables from the SaferProducts API (OData v2) page by page: `IncidentDetails`, `CompanyDetails`, `SourceTypes`, `SeverityTypes`, `Locales`, `RelationshipTypes`, `Sexes` and `ProductCategories`. Each table is cleaned in Python, dropping unused columns, converting decimal ID columns back to whole numbers and renaming columns and tables to snake_case, then loaded into the `saferproducts_raw` schema in PostgreSQL on Supabase. Each load truncates the table and inserts the new data in a single transaction, so a failed table never stays half loaded.

Every step is logged to a timestamped activity log: rows pulled, pages, columns dropped and converted, rows loaded and any errors.

## How to run

Create the raw schema for SaferProducts on your PostgreSQL database — PostgreSQL won't create it when the tables are created:

```sql
CREATE SCHEMA IF NOT EXISTS saferproducts_raw;
```

Create the raw tables by running the SQL scripts in [`table_schema_scripts/raw`](table_schema_scripts/raw) — they create the 8 tables inside `saferproducts_raw` that the load step inserts into.

Create a `.env` file in the project root with the following variables — this makes the project plug and play, swap the values for local or production without changing any code:

- `CHROME_USER_AGENT` — Chrome's User-Agent string, since the site blocks the default `python-requests` one
- `SAFERPRODUCTS_BASE_API_URL` — the SaferProducts API base URL
- `SAFERPRODUCTS_API_KEY` — your free SaferProducts API key
- `DATABASE_URL` — your PostgreSQL connection string

**Pipeline** — pulls every table from the API, cleans it and loads it into the database:

```bash
python3 main.py  # macOS/Linux
python main.py   # Windows
```

## Documentation

- [`docs/ABOUT_THE_DATA.md`](docs/ABOUT_THE_DATA.md) — how a complaint goes from being filed to being public, and what that means for anyone reading the data
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — every table and column, filled in once all the dbt models are finished
- [`table_schema_scripts/raw`](table_schema_scripts/raw) — the SQL scripts that create the raw tables

## Libraries

- pandas
- requests
- SQLAlchemy
- psycopg2
- python-dotenv
- logging (built-in)
- os (built-in)
- re (built-in)
- time (built-in)

## Tools

- PostgreSQL
- Supabase

## What's new?

- Switched from the SaferProducts zip export to the SaferProducts API, pulling 8 tables page by page
- Added transform step: drops unused columns, converts decimal ID columns to Int64 and renames columns and tables to snake_case
- Added load step: truncates and inserts each table into `saferproducts_raw` on Supabase in a single transaction with SQLAlchemy
- Fixed the page count in the extraction logs, so a failed pull names the exact page that broke
- Moved `ABOUT_THE_DATA.md` and `DATA_DICTIONARY.md` into `docs/`

## What's next?

- dbt snapshots of every raw table (SCD Type 2), keeping the history of complaints that get corrected or deleted, since the raw tables are fully replaced on every run
- dbt silver and gold models, from raw tables to clean, analysis-ready ones, with data quality tests
- Daily schedule with GitHub Actions
- Insights, for starters: brands ranked by number of complaints, most recent complaint per brand, manufacturer replies vs. total complaints and complaints grouped by product category
- A possible public site reporting all of these insights
- ...and more