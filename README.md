# projectB

This is an educational project to practice Python and its libraries, exploring data engineering concepts by building a real pipeline from scratch on public data.

The data comes from [SaferProducts.gov](https://www.saferproducts.gov), the Consumer Product Safety Commission's (CPSC) public database of consumer complaints about potentially dangerous products. It publishes thousands of public reports about products that injured people or put them at risk, but very little analysis is done on them. This project turns that raw data into insights about which brands and products draw the most complaints, and how manufacturers respond.

The pipeline pulls 8 tables from the SaferProducts API (OData v2) page by page — `IncidentDetails`, `CompanyDetails`, `SourceTypes`, `SeverityTypes`, `Locales`, `RelationshipTypes`, `Sexes` and `ProductCategories`. Each table is cleaned in Python, dropping unused columns, converting decimal ID columns back to whole numbers and renaming columns and tables to snake_case, then loaded into the `saferproducts_raw` schema on Supabase. Each load truncates the table and inserts the new data in a single transaction, so a failed table never stays half loaded. Every step is logged to a timestamped activity log.

## How to run

Create a `.env` file in the project root with `CHROME_USER_AGENT`, `SAFERPRODUCTS_BASE_API_URL`, `SAFERPRODUCTS_API_KEY` and `DATABASE_URL` variables pointing to your API access and database — this makes the project plug and play, swap the values for local or production without changing any code. SaferProducts blocks the default `python-requests` User-Agent, so `CHROME_USER_AGENT` must hold Chrome's User-Agent string.

**Database setup** — creates the raw schema, since PostgreSQL won't create it when the tables are created, then run the SQL scripts in `table_schema_scripts/raw` to create the 8 raw tables:

```sql
CREATE SCHEMA IF NOT EXISTS saferproducts_raw;
```

**Pipeline** — pulls every table from the API, cleans it and loads it into the database:

```bash
python3 main.py  # macOS/Linux
python main.py   # Windows
```

## Documentation

- [`docs/ABOUT_THE_DATA.md`](docs/ABOUT_THE_DATA.md) — how a complaint goes from being filed to being public, and what that means for anyone reading the data
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — every table and column, filled in once all the dbt models are finished
- [`table_schema_scripts/raw`](table_schema_scripts/raw) — the SQL scripts that create the 8 raw tables

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

## GitHub Actions

Not set up yet. Workflow files will be located in `.github/workflows/`.

- Daily pipeline workflow — will run `main.py`, pulling every table from the API and loading it into Supabase
- dbt workflow — will run `dbt snapshot`, `dbt run` and `dbt test` after each pipeline run

### Required secrets

Both workflows will require the following repository secrets set in GitHub Settings → Secrets and variables → Actions. The Supabase session pooler connection string must be used instead of the direct connection — GitHub Actions only supports IPv4 and the direct connection is IPv6 only on the free tier.

For security, this project forces every connection to Supabase to be encrypted with SSL, the `DATABASE_URL` secret ends with `?sslmode=require`. Supabase doesn't require it, but with it the connection fails instead of falling back to unencrypted. Locally the project runs against a PostgreSQL database on `localhost`, so the local `.env` doesn't use `sslmode=require`, since the data never leaves the computer and there's nothing to encrypt.

| Secret | Used in | Description |
|--------|---------|-------------|
| `CHROME_USER_AGENT` | Daily pipeline workflow | Chrome's User-Agent string |
| `SAFERPRODUCTS_BASE_API_URL` | Daily pipeline workflow | SaferProducts API base URL |
| `SAFERPRODUCTS_API_KEY` | Daily pipeline workflow | SaferProducts API key |
| `DATABASE_URL` | Daily pipeline workflow | Full Supabase session pooler connection string |

### dbt version note

dbt isn't set up yet. Version details will be added here once the dbt layer is built.

## What's new?

- Switched from the SaferProducts zip export to the SaferProducts API, pulling 8 tables page by page
- Added transform step that drops unused columns, converts decimal ID columns to Int64 and renames columns and tables to snake_case
- Added load step that truncates and inserts each table into `saferproducts_raw` on Supabase in a single transaction with SQLAlchemy
- Fixed the page count in the extraction logs, so a failed pull names the exact page that broke
- Moved `ABOUT_THE_DATA.md` and `DATA_DICTIONARY.md` into `docs/`

## What's next?

projectB is in progress. The extract, transform and load steps are operational, raw data lands on Supabase on every run. Next comes the dbt layer — snapshots of every raw table (SCD Type 2) to keep the history of complaints that get corrected or deleted, since the raw tables are fully replaced on every run, then silver and gold models with data quality tests. After that, a daily schedule with GitHub Actions, the first insights (brands ranked by number of complaints, most recent complaint per brand, manufacturer replies vs. total complaints and complaints grouped by product category), a possible public site reporting all of them, and more.