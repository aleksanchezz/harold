-- Добавить колонку авторов в таблицу текстов

ALTER TABLE texts ADD COLUMN author_id integer NOT NULL DEFAULT 1;

UPDATE texts SET author_id = 2 where id = 2;
UPDATE texts SET author_id = 2 where id = 3;
UPDATE texts SET author_id = 3 where id = 4;
UPDATE texts SET author_id = 3 where id = 5;
UPDATE texts SET author_id = 4 where id = 6;
UPDATE texts SET author_id = 4 where id = 7;
UPDATE texts SET author_id = 5 where id = 8;

ALTER TABLE texts ALTER COLUMN author_id DROP DEFAULT;
ALTER TABLE texts ADD FOREIGN KEY(author_id) REFERENCES authors(id);
