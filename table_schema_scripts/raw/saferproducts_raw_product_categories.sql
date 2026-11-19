-- creates the raw product_categories table: a row number, every API column as text,
-- and upload_timestamp, which defaults to now(), so it fills itself with the load time on each insert

CREATE TABLE saferproducts_raw.product_categories (
  id SERIAL PRIMARY KEY,
  product_category_id TEXT,
  product_category_public_name TEXT,
  product_category_description TEXT,
  upload_timestamp TIMESTAMPTZ DEFAULT now()
);