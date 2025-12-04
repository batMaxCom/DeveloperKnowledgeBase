# Индексы

`Индекс` — это структура данных, которая ускоряет поиск строк в таблице.

Таблица без индекса читается `полным сканированием (Seq Scan)`.
С индексом — `быстрым поиском (Index Scan / Index Seek)`.

## Типы индексов PostgreSQL
### B-tree (по умолчанию)
Используется в 95% случаев.

B-tree работает там, где данные можно линейно упорядочить,
и не работает там, где данные сложные, вложенные или неупорядоченные по ожидаемому признаку.

Пример:
```sql
CREATE INDEX idx_users_email ON users(email);
```

Подходит для:
1. =
```sql
SELECT * FROM users WHERE email = 'test@test.com';
```
2. <, <=, >, >=
```sql
SELECT * FROM orders WHERE price >= 500; 
```
3. BETWEEN
```sql
WHERE age BETWEEN 18 AND 30
```
4. ORDER BY
```sql
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
```
И есть индекс:
```sql
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
```
5. JOIN
```sql
JOIN users u ON o.user_id = u.id
```
6. UNIQUE (нужен быстрый поиск дубликатов.)
7. LIKE 'Phone%' (поиск по началу строки) 

Не подходит для:
1. LIKE '%abc' (поиск по окончанию строки)
2. массивов (B-tree хранит данные отсортированно, а массивы могут быть: в разном порядке, с разным количеством элементов, ...)
3. JSONB (JSONB — вложенная структура, B-tree не может работать эффективно.)
4. геоданных (B-tree умеет сортировать только по одному ключу. Для гео используются GiST или SP-GIST.)

### Hash Index

Отдельный тип индекса (почти не используют).

Работает только для операции равенства =.

Ограничения Hash индексов:

- не работает для сортировки
- не ускоряет диапазоны
- редко выигрывает против B-Tree

### GIN Index (Generalized Inverted Index)

Это специальный тип индекса в PostgreSQL, созданный для работы с сложными структурами данных, где B-tree неэффективен.

Используется для:
- массивов (int[], text[])
- JSONB
- полнотекстового поиска (tsvector)
- hstore
- trigram (через pg_trgm)

Главная особенность:
GIN индексирует `каждый элемент` внутри структуры, а не всю строку как единое значение.

В зависимости от типа данных:
1. JSON
```json
{ "city": "Paris", "tags": ["europe", "travel"] }
```
GIN создаёт отдельные ключи в индексе:
```ini
city = Paris
tags = europe
tags = travel
```
2. Массив
```sql
tags = ['sql', 'postgres', 'indexes']
```
GIN создаёт записи:
```sql
sql
postgres
indexes
```

Пример создания:
```sql
--json
CREATE INDEX idx_users_data_gin ON users USING gin(data jsonb_path_ops);

-- массив
CREATE INDEX idx_tags ON posts USING gin(tags);

--для полнотекстного поиска
CREATE INDEX idx_docs_fts ON docs USING gin(to_tsvector('russian', text));
```
Пример запроса:
```sql
--json
SELECT * FROM users WHERE data ? 'city';
SELECT * FROM users WHERE data @> '{"city": "Paris"}';

--массив
SELECT * FROM posts WHERE tags @> '{postgres}';
SELECT * FROM posts WHERE '{sql}' && tags;

--Полнотекстовый поиск
SELECT * FROM docs WHERE to_tsvector('russian', text) @@ to_tsquery('postgres & sql');
```

Преимущества:

1. Очень быстрый поиск по содержимому структур:
- по элементам массива
- по ключам JSONB
- по словам в FTS

2. Идеален для многозначных полей
Если поле содержит много элементов, GIN работает лучше всех.

Недостатки:
1. Медленная запись (INSERT / UPDATE / DELETE)
2. GIN тяжелый:
   - записи в индекс ВСЕГДА тяжелее B-tree
   - обновления медленнее
   - VACUUM чаще нужен
3. Индекс большой по размеру(В 3–10 раз больше B-tree)
4. Не подходит для обычных сравнений (например, числа сравнивать через GIN нельзя)

### GiST Index (Generalized Search Tree)
`GiST` — это универсальное дерево поиска, которое можно обучить работать с любыми сложными типами данных.

`GiST Index` — это фреймворк, на базе которого в PostgreSQL реализованы разные механики поиска:
- геоданные (PostGIS)
- поиск по расстоянию / ближайшим соседям (kNN)
- поиск по диапазонам (range types: int4range, tsrange)
- полнотекстовый поиск (альтернативный вариант)
- поиск по подобию (trigrams)
- поиск пересечений фигур (полигонов, коробок, сегментов)

```sql
CREATE INDEX idx_locations_gist ON places USING GIST(geo_point);
```

## Главное правило
- Если нужны геоданные, диапазоны, расстояния, близость — бери `GiST`.
- Если нужен поиск внутри структур (JSONB/массивы/слова) — бери `GIN`.
- Если простые сравнения — `B-tree`.

# Покрывающие индексы (index-only scan)

Индекс считается покрывающим, если запрос может быть выполнен только по индексу, без чтения таблицы.

Пример:
```sql
CREATE INDEX idx_orders_cover ON orders(user_id, created_at);
```
```sql
SELECT user_id, created_at
FROM orders
WHERE user_id = 10
ORDER BY created_at DESC;
```