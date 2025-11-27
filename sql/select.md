# Базовый синтаксис SELECT

## Базовый синтаксис

```sql
SELECT <столбцы>
FROM <таблица>
WHERE <условие>;
```
## Логический порядок выполнения SELECT

SQL не выполняется в том порядке, в котором написан.

Фактически SQL выполняется так:

- `FROM` — выбираем таблицы
- `JOIN` — соединяем (если есть)
- `WHERE` — фильтруем строки
- `GROUP BY` — группируем
- `HAVING` — фильтр по группам
- `SELECT` — выбираем столбцы
- `ORDER BY` — сортировка
- `LIMIT/OFFSET` — ограничение

Понимание этого — ключ к написанию корректных запросов и правильной оптимизации.

## Псевдонимы (Aliases)

Используются для удобства.

Таблица:

```sql
SELECT u.id, u.name
FROM users AS u;
```

Поле:
```sql
SELECT price * 1.2 AS price_with_tax
FROM products;
```

Алиасы:
- улучшают читаемость
- сокращают повторения
- обязательны при сложных запросах

## Условия в WHERE
Операторы сравнения:
- =
- <, >
- <=, >=
- <> или !=

Логические операторы:
- AND
- OR
- NOT

```sql
SELECT * FROM users
WHERE age >= 18 AND country = 'USA';

SELECT * FROM orders
WHERE status IN ('paid', 'shipped');

SELECT * FROM products
WHERE name LIKE '%iphone%';
```

# DISTINCT — уникальные значения
```sql
SELECT DISTINCT country FROM users;
```

## ORDER BY — сортировка
```sql
SELECT * FROM users
ORDER BY created_at DESC;
```
Где:
- ASC (ascending) сортирует по возрастанию 
- DESC (descending) — по убыванию

## LIMIT и OFFSET — пагинация
```sql
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```
Где:
`OFFSET` — это оператор, который пропускает указанное количество строк в результирующем наборе запроса перед началом выборки.