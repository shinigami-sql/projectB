-- creates the raw relationship_types table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.relationship_types (
  id SERIAL PRIMARY KEY,
  relationship_type_id TEXT,
  relationship_type_public_name TEXT,
  relationship_type_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);