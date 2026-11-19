-- creates the raw source_types table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.source_types (
  id SERIAL PRIMARY KEY,
  source_type_id TEXT,
  source_type_public_name TEXT,
  source_type_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);