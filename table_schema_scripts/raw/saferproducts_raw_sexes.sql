-- creates the raw sexes table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.sexes (
  id SERIAL PRIMARY KEY,
  sex_id TEXT,
  sex_public_name TEXT,
  sex_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);
