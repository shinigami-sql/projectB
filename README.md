# projectB

A data engineering project that tracks consumer complaints about potentially dangerous products, using public data from [SaferProducts.gov](https://www.saferproducts.gov), the Consumer Product Safety Commission's (CPSC) public database.

## Why

SaferProducts.gov publishes thousands of public reports about products that injured people or put them at risk, but very little analysis is done on them. This project turns that raw data into insights about which brands and products draw the most complaints, and how manufacturers respond.

## What it does

- Downloads the full SaferProducts Public Database Export (a zip with all incident reports and recalls)
- Stores every download with a timestamp, building a history over time, including complaints that later get corrected or deleted
- Unzips and loads the incident reports for analysis
- *(Planned)* Loads the raw data into PostgreSQL
- *(Planned)* Transforms it with dbt models, from raw tables to clean, analysis-ready ones
- *(Planned)* Runs on a schedule with an orchestrator

## Insights

For starters:

- Brands ranked by number of complaints
- Most recent complaint per brand
- Manufacturer replies vs. total complaints
- Complaints grouped by product category

...and more to come.

## About the data

For more info, check [ABOUT_THE_DATA.md](ABOUT_THE_DATA.md).