-- creates the raw severity_types table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.severity_types (
  id SERIAL PRIMARY KEY,
  severity_type_id TEXT,
  severity_type_public_name TEXT,
  severity_type_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);