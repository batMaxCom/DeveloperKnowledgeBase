# Замена подзапросов JOIN-ом

Большинство подзапросов в WHERE или SELECT медленнее JOIN, особенно:

- IN (SELECT ...)
- EXISTS (SELECT ...)
- коррелированные подзапросы
- 
Пример медленного запроса
```sql
SELECT name
FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE price > 1000
);
```

Проблемы:
- PostgreSQL может выполнить подзапрос по сути N раз
- нет возможности эффективно использовать покрывающий индекс

Оптимизированный вариант
```sql
SELECT DISTINCT u.name
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.price > 1000;
```

Преимущества:

- использует индекс orders.user_id
- JOIN читается быстрее
- легко анализировать через EXPLAIN

### Когда подзапрос лучше JOIN?

Если мы используем EXISTS, PostgreSQL может оптимизировать лучше, чем JOIN:
```sql
SELECT name
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

`EXISTS` останавливается на первом найденном совпадении, это быстрее.

# Устранение N+1 проблемы
Это КЛАССИЧЕСКАЯ проблема ORM (особенно SQLAlchemy, Django ORM).

Что такое N+1

Пример:
```python
users = session.query(User).all()
for u in users:
    print(u.orders)  # ORM делает отдельный SELECT для каждого пользователя
```

Если пользователей 1000 → ORM делает 1001 запрос.

### Решение в SQL

Использовать JOIN + Group / JSON Agg:
```sql
SELECT 
    u.id,
    u.name,
    json_agg(o.*) AS orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```
### Решение в SQLAlchemy: опции загрузки
```python
from sqlalchemy.orm import selectinload

users = (
    session.query(User)
    .options(selectinload(User.orders))
    .all()
)
```

`selectinload` сделает 2 запроса вместо 1001:
- 1 запрос на users
- 1 запрос на все orders, где user_id IN (...)

# Переиспользование планов выполнения
PostgreSQL может использовать cached plans, но иногда:
- план неверно оптимизируется
- подготовленные запросы лучше (PREPARE)

Обычный запрос:
```sql
SELECT * FROM orders WHERE price > $1;
```

Каждый раз план строится с нуля.

Подготовленный запрос:
```sql
PREPARE get_orders AS
SELECT * FROM orders WHERE price > $1;
```

Вызов:
```sql
EXECUTE get_orders(100);
```

Преимущества:
- не строит план заново
- повторное выполнение → быстрее
- особенно эффективно в высоконагруженных системах

# Примеры

1. Замена подзапроса JOIN-ом
```sql
SELECT name
FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE price > 1000
);
```
Ответ:
```sql
SELECT DISTINCT name
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.price > 1000;
```

2. Оптимизация LIMIT + ORDER BY
```sql
SELECT *
FROM logs
ORDER BY created_at DESC
LIMIT 50;
```
Ответ:
```sql
CREATE INDEX idx_logs_created_at ON logs(created_at DESC)
```
```sql
SELECT *
FROM logs
ORDER BY created_at DESC
LIMIT 50;
```

3. Оптимизация EXISTS
```sql
SELECT *
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```
Ответ:
```sql
SELECT u.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.user_id IS NULL;
```
4. Убрать лишний CTE (inline)
Запрос:
```sql
WITH expensive AS (
    SELECT *
    FROM orders
    WHERE price > 5000
)
SELECT *
FROM expensive
WHERE created_at > NOW() - INTERVAL '1 month';
```
Ответ:
```sql
SELECT *
FROM orders
WHERE created_at > NOW() - INTERVAL '1 month' AND price > 5000;
```

5. Ускорить поиск по диапазону
```sql 
SELECT *
FROM events
WHERE time_range && '[2025-01-01, 2025-01-05)';
```
Ответ:
```sql
CREATE INDEX idx_events_time ON events USING gist(time_range)
```

6. Оптимизация LIKE '%abc'
```sql
SELECT *
FROM users
WHERE name LIKE '%abc';
```
Ответ:
```sql
CREATE INDEX idx_users_name ON users USING gin(name gin_trgm_ops);
```
```sql
SELECT *
FROM users
WHERE name LIKE '%abc';
```

7. Оптимизация JOIN-а
Исходно:
```
SELECT u.name, o.price
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '7 days';
```
Ответ:
```sql
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at);
```
8. Ускорить агрегацию
```sql
SELECT user_id, SUM(price)
FROM orders
GROUP BY user_id;
```
Ответ:
```sql
CREATE INDEX idx_orders_user_id_price ON orders (user_id, price);```
9. Проблема с OR
```sql
SELECT *
FROM products
WHERE category_id = 5
   OR price > 10000;
```

Ответ:
```sql
CREATE INDEX idx_orders_category_id ON products(category_id)
CREATE INDEX idx_orders_price ON products(price)
```
