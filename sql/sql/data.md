# Работа с данными в SQL

## INSERT — добавление строк

| Пример | таблицы | users |
|--------|---------|-------|
| id     | 	name   | 	age  |
| 1      | 	Anna   | 	25   |
| 2      | 	Mar    | 	30   |

INSERT одной строки
```sql
INSERT INTO users (name, age)
VALUES ('John', 28);
```

Теперь таблица:

| id | 	name | 	age |
|----|-------|------|
| 1  | 	Anna | 	25  |
| 2  | 	Mark | 	30  |
| 3  | 	John | 	28  |

id создаётся автоматически (SERIAL/IDENTITY)

INSERT нескольких строк
```sql
INSERT INTO users (name, age)
VALUES 
  ('Kate', 22),
  ('Victor', 19),
  ('Oleg', 33);
```

## RETURNING — вернуть вставленные/обновлённые строки
Пример:
```sql
INSERT INTO users (name, age)
VALUES ('Alice', 29)
RETURNING id, name;
```

## UPDATE — изменение данных

Пример:
```sql
UPDATE users
SET age = 31
WHERE name = 'Mark';
```

UPDATE с RETURNING
```sql
UPDATE users
SET age = age + 1
WHERE id = 3
RETURNING *;
```

Вернёт обновлённую строку.

## DELETE — удаление строк
```sql
DELETE FROM users
WHERE id = 2;
```

DELETE с RETURNING
```sql
DELETE FROM users
WHERE age < 20
RETURNING id, name;
```
Вернёт список удалённых строк.

## UPSERT — вставить или обновить

ON CONFLICT (PostgreSQL)

Используется при попытке вставить строку, которая нарушает уникальный ключ.

Подготовка таблицы
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE,
    price NUMERIC
);
```

Пример: если sku уже есть — обновить price
```sql
INSERT INTO products (sku, price)
VALUES ('ABC-123', 10)
ON CONFLICT (sku) DO UPDATE
SET price = EXCLUDED.price;
```

Где:
- EXCLUDED — значения, которые мы пытались вставить

Работает так:
- Если нет строки с sku='ABC-123' → вставляется новая
- Если есть → обновляется price

UPSERT со сложной логикой
```sql
ON CONFLICT (sku) DO UPDATE
SET 
    price = products.price + EXCLUDED.price,
    updated_at = NOW();
```

## Транзакции: BEGIN / COMMIT / ROLLBACK

Транзакции = гарантированный набор операций, которые выполняются либо все, либо ни одна.

Пример транзакции
Пример успешной
```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

Оба перевода выполнятся.

Пример с ошибкой → ROLLBACK
```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 1;

-- ОШИБКА: таблицы не существует
UPDATE xxx
SET balance = 100
WHERE id = 2;

ROLLBACK;
```

Ничего не изменится.

8) Пример сложной транзакции
```sql
BEGIN;

INSERT INTO orders (user_id, price)
VALUES (10, 500)
RETURNING id INTO new_order_id;

INSERT INTO logs (order_id, message)
VALUES (new_order_id, 'Created order');

COMMIT;
```

Если любая строка выполнится с ошибкой → всё откатывается.

9) Авто-транзакции

Каждый одиночный запрос сам по себе уже транзакция:
```sql
INSERT ...
UPDATE ...
DELETE ...
```
— автоматически COMMIT.

Только BEGIN включает ручной режим.