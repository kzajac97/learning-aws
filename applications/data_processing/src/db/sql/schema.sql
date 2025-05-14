CREATE TABLE countries (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE languages (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE databases (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Main answers table
CREATE TABLE answers (
  id                  BIGINT PRIMARY KEY,
  years_code          INTEGER,
  years_code_pro      INTEGER,
  country_id          INTEGER REFERENCES countries(id),
  ed_level            TEXT
);
-- The main table holds scalar attributes; foreign keys link to lookup tables :contentReference[oaicite:5]{index=5}

-- Join tables for many-to-many relationships

-- Which languages have been worked with
CREATE TABLE answer_languages_have (
  answer_id   INTEGER REFERENCES answers(id),
  language_id INTEGER REFERENCES languages(id),
  PRIMARY KEY (answer_id, language_id)
);

-- Which databases have been worked with
CREATE TABLE answer_databases_have (
  answer_id   INTEGER REFERENCES answers(id),
  database_id INTEGER REFERENCES databases(id),
  PRIMARY KEY (answer_id, database_id)
);

-- Which languages users want to work with
CREATE TABLE answer_languages_want (
  answer_id   INTEGER REFERENCES answers(id),
  language_id INTEGER REFERENCES languages(id),
  PRIMARY KEY (answer_id, language_id)
);

-- Which databases users want to work with
CREATE TABLE answer_databases_want (
  answer_id   INTEGER REFERENCES answers(id),
  database_id INTEGER REFERENCES databases(id),
  PRIMARY KEY (answer_id, database_id)
);

-- Index on country_id in answers
CREATE INDEX idx_answers_country_id
  ON answers(country_id);

-- Indexes on language and database join tables
CREATE INDEX idx_alh_language_id
  ON answer_languages_have(language_id);

CREATE INDEX idx_adh_database_id
  ON answer_databases_have(database_id);

CREATE INDEX idx_alw_language_id
  ON answer_languages_want(language_id);

CREATE INDEX idx_adw_database_id
  ON answer_databases_want(database_id);
