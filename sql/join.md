# JOIN и соединение таблиц

`JOIN` — это способ объединить данные из нескольких таблиц на основе логической связи.


## Базовый синтаксис JOIN
```sql
SELECT <столбцы>
FROM table1
JOIN table2 ON table1.id = table2.fk;
```

Условие соединения пишем в `ON`, а не в `WHERE`.

## Основные виды JOIN
### Пример структуры таблиц

Чтобы было проще учиться, представим две таблицы:

Таблица users:

| id | name  |
|----|-------|
| 1  | Alex  |
| 2  | Maria |
| 3  | John  |

Таблица orders:

| id | 	user_id | 	product    |
|----|----------|-------------|
| 1  | 	1       | 	iPhone     |
| 2  | 	1       | 	MacBook    |
| 3  | 	2       | 	Samsung TV |

### INNER JOIN

Возвращает только те строки, у которых есть совпадления в обеих таблицах.
```sql
SELECT u.name, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```
### LEFT JOIN

Возвращает все строки из левой таблицы + совпавшие строки из правой.
Если совпадений нет — правая часть будет NULL.
```sql
SELECT u.name, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### RIGHT JOIN

Почти как LEFT, только наоборот.
(На практике используется редко.)

### FULL OUTER JOIN

Возвращает все строки из обеих таблиц + NULL там, где нет пары.

```sql
SELECT *
FROM users u
FULL JOIN orders o ON u.id = o.user_id;
```

### CROSS JOIN

Декартово произведение: каждая строка × каждая строка.
Используется редко, но важно понимать.

```sql
SELECT u.name, o.product
FROM users u
CROSS JOIN orders o;
```
Используется:
- для генерации комбинаций
- календарей
- тестовых данных
- Но может легко убить производительность.

### USING vs ON

Если столбцы имеют одинаковые названия:
```sql
SELECT *
FROM orders
JOIN users USING (id);
```

Но чаще исползуют `ON` — он универсальней.

## Примеры

1) Получить список пользователей и их заказов (имя + продукт).
```sql
SELECT u.name, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```
2) Получить всех пользователей, даже тех, у кого нет заказов.
```sql 
SELECT u.name, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```
3) Получить всех пользователей и сумму их заказов.
```sql
SELECT u.name, SUM(o.price) AS sum_order
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name; 
```
4) Получить пользователей, у которых нет заказов.
```sql
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL; 
```