-- Cards table
CREATE TABLE cards (
  id BIGSERIAL PRIMARY KEY,
  liga_link TEXT,
  myp_link TEXT,
  qtd INTEGER,
  card_name TEXT
);

-- Prices table
CREATE TABLE prices (
  id SERIAL PRIMARY KEY,
  id_card BIGINT REFERENCES cards(id),
  store TEXT,
  lowest_price NUMERIC,
  qtd INTEGER,
  lowest_price_qtd NUMERIC,
  qtd_qtd INTEGER,
  date_price TIMESTAMP
);