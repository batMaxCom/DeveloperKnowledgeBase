# Оконные функции (WINDOW FUNCTIONS)

Оконные функции позволяют выполнять вычисления по группе строк, не объединяя их в одну строку, в отличие от GROUP BY.

То есть ты можешь:
посчитать сумму по пользователю и всё ещё получить все строки заказов, а не только одну. Это делает оконные функции незаменимыми в аналитике.

## 1. Базовый синтаксис окна
```sql
<window_function>() OVER (
    PARTITION BY ...
    ORDER BY ...
)
```

## 2. PARTITION BY — "разделить на группы"

Например: посчитать сумму заказов по каждому пользователю, но оставить строки отдельными:
```sql

SELECT 
    user_id,
    price,
    SUM(price) OVER (PARTITION BY user_id) AS total_user_sum
FROM orders;
```

## 3. ORDER BY внутри окна

Считаем накопительную сумму:
```sql

SELECT
    user_id,
    price,
    created_at,
    SUM(price) OVER (
        PARTITION BY user_id
        ORDER BY created_at
    ) AS running_total
FROM orders;
```

## 4. ROW_NUMBER / RANK / DENSE_RANK

Используются для рейтингов, поиска первых/последних строк.

Главное отличие:

| Функция    | 	Как работает                                               |
|------------|-------------------------------------------------------------|
| ROW_NUMBER | 	Нумерует строки подряд (1,2,3,4,5...) всегда уникально     |
| RANK       | 	Даёт одинаковый ранг одинаковым значениям, делает пропуски |
| DENSE_RANK | 	Даёт одинаковый ранг одинаковым значениям, без пропусков   |

### ROW_NUMBER — строго уникальная нумерация
```sql
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY price DESC)
```
Например:
```
SELECT
    user_id,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS rownum
FROM scores;
```

ROW_NUMBER() не смотрит на одинаковые значения, а просто нумерует строки в заданном порядке.

Результат ROW_NUMBER:

| user_id | 	score | 	ROW_NUMBER |
|---------|--------|-------------|
| 2       | 	200   | 	1          |
| 3       | 	200   | 	2          |
| 4       | 	150   | 	3          |
| 1       | 	100   | 	4          |
| 5       | 	100   | 	5          |
| 6       | 	90    | 	6          |

### RANK — одинаковым значениям присваивается одинаковый ранг (с пропусками)
```sql
RANK() OVER (ORDER BY price DESC)
```
Например:
```sql
SELECT
    user_id,
    score,
    RANK() OVER (ORDER BY score DESC) AS rnk
FROM scores;
```
Результат RANK:

| user_id | 	score | 	RANK |
|---------|--------|-------|
| 2       | 	200   | 	1    |
| 3       | 	200   | 	1    |
| 4       | 	150   | 	3    |
| 1       | 	100   | 	4    |
| 5       | 	100   | 	4    |
| 6       | 	90    | 	6    |

Пояснение:

- Два пользователя имеют 200 → они оба получат 1
- Следующий после двух первых ― 150 → получает 3 (а не 2!)

Почему?

Потому что ранг 2 пропущен, т. к. RANK учитывает количество людей "выше".

### DENSE_RANK — без пропусков
```sql
DENSE_RANK() OVER (ORDER BY price DESC)
```
Например:
```sql
SELECT
    user_id,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) AS drnk
FROM scores;
```
Результат DENSE_RANK:

| user_id | 	score | 	DENSE_RANK |
|---------|--------|-------------|
| 2       | 	200   | 	1          |
| 3       | 	200   | 	1          |
| 4       | 	150   | 	2          |
| 1       | 	100   | 	3          |
| 5       | 	100   | 	3          |
| 6       | 	90    | 	4          |

Пояснение:
- Те же группы одинаковых значений
- Но следующий ранг всегда = предыдущий + 1
- Пропусков нет


## 5. LAG / LEAD

Используются для сравнения текущей строки с предыдущей или следующей.

LAG — значение предыдущей строки
```sql
LAG(price, 1) OVER (PARTITION BY user_id ORDER BY created_at) AS prev_price
```

LEAD — значение следующей строки
```sql
LEAD(price, 1) OVER (ORDER BY created_at) AS next_price
```

## 6. Агрегации поверх окон

Можно использовать любые агрегатные функции:

- SUM
- AVG
- MAX
- MIN
- COUNT

Пример: средняя цена заказа по категории:
```sql
AVG(price) OVER (PARTITION BY category_id)

```

## 7. Без PARTITION BY (одно "глобальное" окно)

```sql
SELECT price,
       RANK() OVER (ORDER BY price DESC) AS price_rank
FROM orders;
```

## 8. Окно без ORDER BY — "по всей группе целиком"
```sql
SELECT
    user_id,
    price,
    SUM(price) OVER (PARTITION BY user_id) AS total
FROM orders;
```

## Примеры
1. Для каждого пользователя вывести его заказы и добавить:

ROW_NUMBER() по убыванию цены.**

Результат:
user_id | order_id | price | row_number
```sql
SELECT 
    user_id, 
    order_id, 
    price, 
    ROW_NUMBER() OVER (ORDER BY price DESC) AS row_number
FROM orders;
```
2. Вывести заказы и разницу цены между текущим и предыдущим заказом пользователя.

Использовать LAG.
```sql
SELECT 
    id,
    price,
    price - LAG(price, 1) OVER (PARTITION BY user_id ORDER BY created_at) AS difference_price
FROM orders;
```
3. Для каждого продукта вывести накопительную сумму продаж (running sum) по дате.
```sql
SELECT
    product_id,
    SUM(price,  LAG(price, 1)) OVER (PARTITION BY product_id ORDER BY created_at) AS running_sum
FROM orders
```
4. Для каждой категории — средний чек заказа, но показать каждый заказ.
```sql
SELECT
    id,
    category_id,
    AVG(price) OVER (PARTITION BY category_id) AS avg_price_by_category
FROM orders
```
5. Найти для каждого пользователя его самый дорогой заказ, используя оконные функции (без LIMIT и подзапросов).

Подсказка: ROW_NUMBER() OVER (...).
```sql
WITH ranked_orders AS (
    SELECT
        id,
        user_id,
        price,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY price DESC
        ) AS rnk
    FROM orders
)
SELECT *
FROM ranked_orders
WHERE rnk = 1;
```