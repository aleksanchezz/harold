CREATE TABLE IF NOT EXISTS authors
(
    id          integer NOT NULL PRIMARY KEY,               -- PK
    name        text NULL,
    code_name   text NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books
(
    id          integer NOT NULL PRIMARY KEY,               -- PK
    title       text NULL,
    author_id   integer NOT NULL REFERENCES authors (id),   -- FK
    genre       text NUll,
    date        text NULL,
    code_name   text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS texts
(
    id              integer NOT NULL PRIMARY KEY,            -- PK
    book_id         integer NOT NULL REFERENCES books (id),  -- FK
    ngramms_array   integer[],
    parts_array     integer[],
    punct_array     integer[],
    code_name       text NULL UNIQUE
);
