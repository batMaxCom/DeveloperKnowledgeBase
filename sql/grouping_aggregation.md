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
1. 
```sql
SELECT u.name, AVG(o.price) as avg_price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```
2. 
```sql
SELECT u.name, COUNT(o.id) as avg_price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```
3.
```sql
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
HAVING COUNT(o.id) > 2
```
4
```sql
SELECT u.name, o.id, MAX(o.price)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```