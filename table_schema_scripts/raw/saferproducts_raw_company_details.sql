-- creates the raw company_details table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.company_details (
  id SERIAL PRIMARY KEY,
  company_id TEXT,
  company_name TEXT,
  address_line_1 TEXT,
  address_line_2 TEXT,
  address_line_3 TEXT,
  city_name TEXT,
  state_province TEXT,
  location_id TEXT,
  zip_code TEXT,
  primary_phone_number TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);