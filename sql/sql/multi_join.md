# Несколько JOIN (multi-join)
## 1.Базовый пример с тремя таблицами

Представим:
- users (id, name)
- orders (id, user_id, product_id, price)
- products (id, title)

Пример:
```sql
SELECT 
    u.name, 
    p.title, 
    o.price
FROM orders o
JOIN users u ON u.id = o.user_id
JOIN products p ON p.id = o.product_id;
````

Важно: порядок JOIN не влияет на результат, но влияет на читаемость.

## 2. LEFT JOIN в цепочке

Важно понимать, что LEFT JOIN тянет NULL дальше по цепочке.
```sql
SELECT 
    u.name,
    o.id,
    p.title
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN products p ON p.id = o.product_id;
```

Если у пользователя нет заказов:
- o.id = NULL
- p.title = NULL (потому что зависит от заказа)

## 3.  JOIN разных типов в одном запросе
```sql
SELECT 
    u.name,
    o.id,
    p.title,
    c.name AS category
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
JOIN products p ON p.id = o.product_id      -- INNER JOIN
LEFT JOIN categories c ON c.id = p.category_id;
```

Порядок важен логически:
- INNER JOIN "фильтрует" результаты
- LEFT JOIN "добавляет" данные

## 4. Комбинирование фильтров

Где ставить WHERE — критически важно.

Ошибка:
```sql
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.price > 100
```

Ты превращаешь LEFT JOIN в INNER JOIN
(потому что WHERE удалит все NULL).

Правильно:
```sql
LEFT JOIN orders o ON o.user_id = u.id AND o.price > 100
```
## 5. Много JOIN и группировка
```sql
SELECT 
    u.name,
    COUNT(o.id) AS total_orders,
    SUM(o.price) AS total_sum
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN products p ON p.id = o.product_id
LEFT JOIN categories c ON c.id = p.category_id
GROUP BY u.name;
```
## 6. Ошибки, которые допускают 90% разработчиков
Ошибка: перепутать порядок условий
```sql
... 
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid';
```
→ превращает LEFT JOIN в INNER JOIN

Правильно:
```
...
LEFT JOIN orders o 
   ON o.user_id = u.id
  AND o.status = 'paid'
```

## Примеры

1. Вывести: user.name, orders.id, products.title — через цепочку из 3 JOIN.
```sql
SELECT u.name, o.id, p.title
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN products p ON o.product_id = p.id
```

2. Вывести всех пользователей и сумму всех их заказов.
```sql
SELECT u.id, u.name, SUM(o.price) AS total_price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

3. Вывести пользователей, у которых есть заказ в категории “Phones”.
```sql
SELECT DISTINCT u.name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON p.id = o.product_id
JOIN categories c ON c.id = p.category_id
WHERE c.name = 'Phones';
```

4. Вывести пользователей без заказов, но через LEFT JOIN.
```sql
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```