# Subqueries, CTE (Common Table Expressions)

## Подзапросы (Subqueries)

Подзапрос — это SELECT внутри другого SELECT / WHERE / FROM / HAVING

### 1. Скалярые подзапросы (возвращают одно значение)

Используются там, где ожидается значение:

```sql
SELECT name, age
FROM users
WHERE age > (SELECT AVG(age) FROM users);
```

### 2. Подзапросы в WHERE…IN

Ожидается список:
```sql
SELECT *
FROM orders
WHERE user_id IN (
    SELECT id FROM users WHERE role = 'admin'
);
```

### 3. Подзапросы в EXISTS / NOT EXISTS
Используются для проверки существования данных:
```sql
SELECT *
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### 4. Подзапрос → «виртуальная таблица» в FROM
```sql
SELECT t.user_id, t.total
FROM (
    SELECT user_id, SUM(price) AS total
    FROM orders
    GROUP BY user_id
) t
WHERE t.total > 1000;
```
## CTE (Common Table Expressions)

CTE = подзапрос, вынесенный в начало запроса для читаемости:

```sql
WITH user_totals AS (
    SELECT user_id, SUM(price) AS total
    FROM orders
    GROUP BY user_id
)
SELECT user_id
FROM user_totals
WHERE total > 1000;
```
Преимущества:
- читаемость
- можно использовать несколько раз
- можно строить многоступенчатые расчёты
- рекурсивные CTE (для иерархий и деревьев)

### Рекурсивный CTE (для вложенных структур, дерева категорий)
```
WITH RECURSIVE category_tree AS (
    SELECT id, parent_id, name
    FROM categories
    WHERE id = 10

    UNION ALL

    SELECT c.id, c.parent_id, c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

## Примеры

1. Найти пользователей, чья общая сумма заказов выше 500, используя CTE
```sql
WITH user_total AS (
    SELECT user_id, SUM(price) AS total_price
    FROM orders
    GROUP BY user_id
)
SELECT user_id
FROM user_total
WHERE total_price > 500;
```

2. Используя подзапрос в WHERE, найти пользователей, у которых средняя цена заказа выше средней цены по всем заказам
```sql
SELECT id
FROM users
WHERE (
    SELECT AVG(price) 
    FROM orders 
    WHERE user_id = users.id
) > (
    SELECT AVG(price) FROM orders
);
```
3. Используя NOT EXISTS, выбрать пользователей без заказов
```sql
SELECT *
FROM users u
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.user_id = u.id
);
```
4. С помощью CTE построить таблицу: user_id, total_orders, total_sum
```sql
WITH order_table AS (
    SELECT 
        user_id,
        COUNT(id) AS total_orders,
        SUM(price) AS total_sum
    FROM orders
    GROUP BY user_id
)
SELECT *
FROM order_table;
```
