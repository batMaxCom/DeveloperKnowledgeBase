# Materialized CTE vs Inline CTE

В PostgreSQL есть синтаксис:
```
WITH MATERIALIZED cte AS (...)
WITH NOT MATERIALIZED cte AS (...)
```
Что происходит?
MATERIALIZED:
- CTE реально создаётся как временная таблица.
- Оптимизатор не может разворачивать её обратно.
- Используется, когда выгодно кэшировать результат.

NOT MATERIALIZED:
- Позволяет оптимизатору встраивать CTE в основной запрос.
- Часто быстрее при простых CTE (фильтры проталкиваются внутрь).

По умолчанию:
- PostgreSQL <= 11: CTE всегда материализованы
- PostgreSQL 12+: CTE inline (не материализуются автоматически)

Пример различия:

MATERIALIZED (результат кэшируется)
```sql
WITH MATERIALIZED big_orders AS (
    SELECT * FROM orders WHERE amount > 100
)
SELECT * FROM big_orders WHERE price > 500;
```

NOT MATERIALIZED (фильтры проталкиваются внутрь)
```sql
WITH NOT MATERIALIZED big_orders AS (
    SELECT * FROM orders
)
SELECT * FROM big_orders WHERE amount > 100 AND price > 500;
```

Производительность: правила


| Тип                           | Когда использовать                              |
|-------------------------------|-------------------------------------------------|
| Materialized CTE              | один и тот же CTE используется несколько раз    |
|                               | тяжёлый подзапрос, выгодно кэшировать           |
| Inline CTE (NOT MATERIALIZED) | простой подзапрос, который можно оптимизировать |
|                               | нужен быстрый execution plan                    |
