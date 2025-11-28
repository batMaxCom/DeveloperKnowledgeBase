# GROUP BY, HAVING и агрегатные функции

## Агрегатные функции
Это функции, которые работают не над строкой, а над множеством строк.

Основные функции:

- `COUNT()` — количество строк
- `SUM()` — сумма
- `AVG()` — среднее
- `MIN()` — минимум
- `MAX()` — максимум

Примеры:
```sql
SELECT COUNT(*) FROM users;
SELECT AVG(price) FROM orders;
```

## GROUP BY

GROUP BY группирует строки по выбранным полям.
После группировки — каждая группа даёт одну результирующую строку.

Пример:
```sql
SELECT country, COUNT(*) 
FROM users
GROUP BY country;
```

Результат:

| country | 	count |
|---------|--------|
| USA     | 	50    |
| UK      | 	30    |
| France  | 	20    |

Когда в запросе есть `GROUP BY`, то в `SELECT` можно использовать только:
- поля из GROUP BY
- агрегатные функции

Плохой запрос:
```sql
SELECT country, age FROM users   -- age не агрегат!
GROUP BY country;
```

Хороший запрос:
```sql
SELECT country, AVG(age)
FROM users
GROUP BY country;
```

## HAVING — фильтрация после группировки

`WHERE` фильтрует строки до группировки.
`HAVING` — после.

Пример:
```sql
SELECT country, COUNT(*) 
FROM users
GROUP BY country
HAVING COUNT(*) > 10;
```

## Примеры
1) Получить среднюю сумму заказа по каждому пользователю.
```sql
SELECT u.name, AVG(o.price) as avg_price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```
2) Получить количество заказов у каждого пользователя.
```sql
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```
3) Получить только тех пользователей, у которых количество заказов > 2.
```sql
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name
HAVING COUNT(o.id) > 2;
```
4) Получить самый дорогой заказ каждого пользователя.
- Вариант 1: просто получить максимальную цену у каждого пользователя
```sql
SELECT u.name, MAX(o.price) AS max_price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```
- Вариант 2: получить именно заказ (id) с максимальной ценой

Используем подзапрос:
```sql
SELECT u.name, o.id, o.price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.price = (
    SELECT MAX(price)
    FROM orders
    WHERE user_id = u.id
);
```