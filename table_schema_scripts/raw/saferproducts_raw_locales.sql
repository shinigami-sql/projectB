-- creates the raw locales table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.locales (
  id SERIAL PRIMARY KEY,
  locale_id TEXT,
  locale_public_name TEXT,
  locale_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);